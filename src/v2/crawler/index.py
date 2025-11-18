import fastf1

fastf1.Cache.enable_cache('./cache')

# Get session data
session = fastf1.get_session(2025, 1, 'Q')
session.load()

# Get circuit information
circuit = session.get_circuit_info()

# Convert corners data to a list of dictionaries
corners_data = []
for corner in circuit.corners.itertuples(index=False):
    corner_dict = {
        'x': corner.X,
        'y': corner.Y,
        'number': corner.Number,
        'letter': corner.Letter,
        'angle': corner.Angle,
        'distance': corner.Distance
    }
    corners_data.append(corner_dict)

# Print the result
print(corners_data)
