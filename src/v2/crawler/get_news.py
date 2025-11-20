import requests
from bs4 import BeautifulSoup
from src.v2.models.news import News
from src.core.database.database import SessionLocal
from datetime import date, datetime, timezone

def process_content(soup):
    # Process headings
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = heading.name[1]
        heading_text = heading.get_text(strip=True)
        custom_tag = f"[HEADING:level={level}]{heading_text}[/HEADING]"
        heading.replace_with(custom_tag)
    
    # Process paragraphs
    for p in soup.find_all('p'):
        p_text = p.get_text(strip=True)
        if p_text:  # Only process non-empty paragraphs
            custom_tag = f"[PARAGRAPH]{p_text}[/PARAGRAPH]"
            p.replace_with(custom_tag)
    
    # Process links
    for a in soup.find_all('a', href=True):
        link_text = a.get_text(strip=True)
        if link_text:  # Only process links with text
            custom_tag = f"[LINK:url={a['href']}]{link_text}[/LINK]"
            a.replace_with(custom_tag)
    
    # Process images
    for img in soup.find_all('img', src=True):
        alt_text = img.get('alt', '')
        custom_tag = f"[IMAGE:src={img['src']}]{alt_text}[/IMAGE]"
        img.replace_with(custom_tag)
    
    # Process lists
    for ul in soup.find_all('ul'):
        list_items = [f"[LIST_ITEM]{li.get_text(strip=True)}[/LIST_ITEM]" 
                     for li in ul.find_all('li', recursive=False)]
        custom_tag = f"[UNORDERED_LIST]\n" + "\n".join(list_items) + "\n[/UNORDERED_LIST]"
        ul.replace_with(custom_tag)
    
    for ol in soup.find_all('ol'):
        list_items = [f"[LIST_ITEM:number={i+1}]{li.get_text(strip=True)}[/LIST_ITEM]" 
                     for i, li in enumerate(ol.find_all('li', recursive=False))]
        custom_tag = f"[ORDERED_LIST]\n" + "\n".join(list_items) + "\n[/ORDERED_LIST]"
        ol.replace_with(custom_tag)

def get_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find_all("h1")[0].get_text(strip=True)
    description = soup.select_one(r"#maincontent > div > div:nth-child(1) > div > div > div.flex.flex-col.gap-px-16.lg\:gap-px-24.justify-between.md\:max-w-content-fixed-md.lg\:max-w-content-fixed-lg > div.flex.flex-col.gap-rem-12.md\:gap-rem-16.lg\:gap-rem-24 > p").get_text(strip=True)
    process_content(soup)
    content: str = ""
    for article in soup.find_all("div", class_="content-rich-text"):
        content += article.get_text(separator='\n', strip=True)
    
    return title, description, content
  
def get_news(db, base_url):
    response = requests.get(base_url + "/en/latest?articleFilters=Article&page=3")
    soup = BeautifulSoup(response.content, "html.parser")
    
    articles = soup.select(r"#maincontent > div > div > div > div > div.flex.flex-col.gap-px-48.lg\:gap-px-64 > ul > li")
    for article in articles:
        thumbnail = article.select_one("img")["src"]
        href = article.select_one("a")["href"]
        display_title = article.select_one("a").get_text(strip=True)
        
        title, description, content = get_article_content(base_url + href)
        
        article_data = {
          "display_title": display_title,
          "title": title,
          "description": description,
          "content": content,
          "thumbnail": thumbnail,
          "url": base_url + href,
          "published_at": datetime.now(timezone.utc)
        }
        
        save_news(db, article_data)
        
def save_news(db, data):
  existing_news = db.query(News).filter(
    News.title == data["title"],
    News.display_title == data["display_title"],
    News.description == data["description"],
    News.content == data["content"],
    News.thumbnail == data["thumbnail"],
    News.url == data["url"]
  ).first()
  
  if existing_news:
    # Update existing news
    for key, value in data.items():
      setattr(existing_news, key, value)
    existing_news.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(existing_news)
    print(f"Updated news: {data['title']}")
  else:
    # Create new news
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)
    news = News(**data)
    db.add(news)
    db.commit()
    print(f"Saved new news: {data['title']}")
    
def init_db():
    """Initialize the database by creating all tables."""
    from src.core.database.database import Base, engine
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")
    

if __name__ == "__main__":  
    init_db()
    
    db = SessionLocal()
    try:
      base_url = "https://www.formula1.com"
      
      get_news(db, base_url)
    except Exception as e:
      print(f"Error in get_news: {str(e)}")
      raise
    finally:
      db.close()
        
