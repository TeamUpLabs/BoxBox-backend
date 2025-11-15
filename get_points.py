import aiohttp
import asyncio
import random
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional, Union
import json
import os
from datetime import datetime, timedelta

# Configuration
CACHE_DIR = ".cache"
CACHE_EXPIRY_HOURS = 24 * 7  # Cache for a week
MAX_RETRIES = 1  # Minimize retries for speed
INITIAL_RETRY_DELAY = 0.2  # Very short delay for retries
MAX_RETRY_DELAY = 2.0  # Maximum delay for retries
RATE_LIMIT_DELAY = 0.1  # Minimal delay between requests
RATE_LIMIT_JITTER = 0.1  # Minimal jitter
BATCH_SIZE = 20  # Larger batch size
MAX_CONCURRENT_REQUESTS = 8  # Increased concurrency
CONNECTION_TIMEOUT = 10.0  # Shorter timeout for faster failure
TOTAL_TIMEOUT = 30.0  # Total timeout per request

class APIClient:
    def __init__(self):
        self.session = None
        self.base_url = "https://api.openf1.org/v1"
        self.timeout = aiohttp.ClientTimeout(total=TOTAL_TIMEOUT, connect=CONNECTION_TIMEOUT)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            connector=aiohttp.TCPConnector(
                limit=MAX_CONCURRENT_REQUESTS,
                ttl_dns_cache=300,
                force_close=True
            )
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_path(self, endpoint: str, params: Dict) -> str:
        """Generate cache file path based on endpoint and parameters"""
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        cache_key = f"{endpoint.replace('/', '_')}_{hash(frozenset(params.items()))}"
        return os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache is still valid"""
        if not os.path.exists(cache_path):
            return False
            
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - cache_time < timedelta(hours=CACHE_EXPIRY_HOURS)
    
    async def _rate_limit_delay(self, retry_count: int) -> None:
        """Ultra-minimal delay for retries only"""
        if retry_count > 0:
            # Very short delay with minimal jitter
            delay = min(INITIAL_RETRY_DELAY * (retry_count ** 1.2), MAX_RETRY_DELAY)
            await asyncio.sleep(delay * (0.9 + random.random() * 0.2))  # ±10% jitter

    async def get(self, endpoint: str, params: Dict = None, retry_count: int = 0) -> List[Dict]:
        """Generic GET request with caching and retry logic"""
        if params is None:
            params = {}
        
        # Always try cache first for maximum speed
        cache_path = self._get_cache_path(endpoint, params)
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Cache read error, will refetch: {e}")
        
        # Apply minimal rate limiting only for retries
        if retry_count > 0:
            await self._rate_limit_delay(retry_count)
                
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 429:  # Rate limited
                    if retry_count < MAX_RETRIES:
                        retry_after = float(response.headers.get('Retry-After', '1'))
                        await asyncio.sleep(retry_after)
                        return await self.get(endpoint, params, retry_count + 1)
                    else:
                        response.raise_for_status()
                
                response.raise_for_status()
                data = await response.json()
                
                # Cache successful responses
                try:
                    with open(cache_path, 'w') as f:
                        json.dump(data, f)
                except (IOError, OSError) as e:
                    print(f"Warning: Failed to cache response: {e}")
                    
                return data
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if retry_count < MAX_RETRIES and not isinstance(e, aiohttp.ClientResponseError):
                return await self.get(endpoint, params, retry_count + 1)
            print(f"Error fetching {url} (attempt {retry_count + 1}/{MAX_RETRIES}): {e}")
            if hasattr(e, 'status') and e.status == 429:
                print("Rate limit exceeded. Please try again later or use cached data if available.")
            return []

async def get_race_sessions(year: int = 2025) -> List[int]:
    """Fetch race session keys for the given year"""
    async with APIClient() as client:
        sessions = await client.get("sessions", {"year": year})
        return [s['session_key'] for s in sessions if s.get('session_type') == 'Race']

async def get_session_results(session_key: int) -> List[Dict]:
    """Fetch results for a specific session with retry logic"""
    async with APIClient() as client:
        try:
            return await client.get("session_result", {"session_key": session_key})
        except Exception as e:
            print(f"Failed to get session results for session {session_key}: {e}")
            return []

async def process_batch(session_keys: List[int], semaphore: asyncio.Semaphore) -> List[Any]:
    """Process a batch of session keys with concurrency control"""
    async with semaphore:
        # Process all tasks in parallel with timeout
        tasks = [asyncio.wait_for(
            get_session_results(session_key),
            timeout=TOTAL_TIMEOUT
        ) for session_key in session_keys]
        
        # Gather results with error handling
        results = []
        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                results.append(result)
            except asyncio.TimeoutError:
                print("Request timed out, skipping...")
                results.append([])  # Return empty result on timeout
            except Exception as e:
                print(f"Error in batch processing: {e}")
                results.append([])  # Return empty result on error
        
        return results

async def get_driver_points(year: int = 2025) -> Dict[int, int]:
    """Get total points for each driver across all race sessions"""
    try:
        # Get all race session keys with error handling
        session_keys = await get_race_sessions(year)
        if not session_keys:
            print("No race sessions found for the specified year.")
            return {}
        
        print(f"Found {len(session_keys)} race sessions. Fetching results...")
        
        # Use a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        all_results = []
        
        # Process all sessions with controlled concurrency
        for i in range(0, len(session_keys), BATCH_SIZE):
            batch = session_keys[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (len(session_keys) + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"Processing batch {batch_num}/{total_batches} (sessions {i+1}-{min(i+BATCH_SIZE, len(session_keys))})")
            
            # Process batch with concurrency control
            batch_results = await process_batch(batch, semaphore)
            all_results.extend(batch_results)
            
            # Minimal delay only if we have more batches to process
            remaining_batches = (len(session_keys) - (i + BATCH_SIZE)) // BATCH_SIZE
            if remaining_batches > 0 and remaining_batches % 2 == 0:  # Every other batch
                await asyncio.sleep(0.05)  # Very short delay
        
        # Process results
        driver_points = defaultdict(int)
        session_count = 0
        
        for i, session_results in enumerate(all_results):
            if isinstance(session_results, Exception):
                print(f"Error processing session {session_keys[i] if i < len(session_keys) else 'unknown'}: {session_results}")
                continue
                
            if not isinstance(session_results, list):
                print(f"Unexpected response format for session {session_keys[i] if i < len(session_keys) else 'unknown'}")
                continue
                
            session_count += 1
            
            for result in session_results:
                try:
                    driver_number = result.get('driver_number')
                    points = result.get('points')
                    
                    if driver_number is not None and points is not None:
                        driver_points[driver_number] += points
                except (KeyError, TypeError) as e:
                    print(f"Error processing result: {e}")
        
        print(f"Successfully processed {session_count} out of {len(session_keys)} sessions")
        return dict(driver_points)
        
    except Exception as e:
        print(f"Unexpected error in get_driver_points: {e}")
        return {}

def get_points(year: int = 2025) -> Dict[int, int]:
    """
    Synchronous wrapper for the async get_driver_points function
    
    Args:
        year: The championship year to get points for (default: 2025)
        
    Returns:
        Dict mapping driver numbers to their total points
    """
    try:
        return asyncio.run(get_driver_points(year))
    except Exception as e:
        print(f"Error in get_points: {e}")
        return {}

