# GPS Mapping Example

This example demonstrates how to work with GPS location data in image EXIF metadata using tagkit.

## Reading GPS Coordinates

The following example shows how to extract GPS coordinates from images:

```python
from tagkit.image_exif import read_exif

def extract_gps_coordinates(image_path):
    """Extract GPS coordinates from an image's EXIF data."""
    # Read EXIF data
    tags = read_exif(image_path)
    
    # Check if GPS data exists
    if not any(key.startswith('GPS') for key in tags):
        print(f"No GPS data found in {image_path}")
        return None
    
    # Extract latitude
    if 'GPSLatitude' in tags and 'GPSLatitudeRef' in tags:
        lat = tags['GPSLatitude']
        lat_ref = tags['GPSLatitudeRef']
        
        # Convert to decimal degrees
        lat_deg = lat[0] + lat[1]/60 + lat[2]/3600
        if lat_ref == 'S':
            lat_deg = -lat_deg
    else:
        print(f"No latitude data found in {image_path}")
        return None
    
    # Extract longitude
    if 'GPSLongitude' in tags and 'GPSLongitudeRef' in tags:
        lon = tags['GPSLongitude']
        lon_ref = tags['GPSLongitudeRef']
        
        # Convert to decimal degrees
        lon_deg = lon[0] + lon[1]/60 + lon[2]/3600
        if lon_ref == 'W':
            lon_deg = -lon_deg
    else:
        print(f"No longitude data found in {image_path}")
        return None
    
    # Extract altitude if available
    altitude = None
    if 'GPSAltitude' in tags and 'GPSAltitudeRef' in tags:
        altitude = tags['GPSAltitude']
        altitude_ref = tags['GPSAltitudeRef']
        
        # If altitude reference is 1, altitude is below sea level
        if altitude_ref == 1:
            altitude = -altitude
    
    # Return coordinates as a dictionary
    coordinates = {
        'latitude': lat_deg,
        'longitude': lon_deg,
        'altitude': altitude
    }
    
    print(f"GPS coordinates: {lat_deg:.6f}, {lon_deg:.6f}, altitude: {altitude}")
    return coordinates

# Example usage
if __name__ == "__main__":
    coordinates = extract_gps_coordinates("path/to/your/geotagged_image.jpg")
```

## Writing GPS Coordinates

The following example shows how to add GPS coordinates to an image:

```python
from tagkit.image_exif import write_exif

def add_gps_coordinates(image_path, latitude, longitude, altitude=None):
    """Add GPS coordinates to an image's EXIF data."""
    # Convert decimal degrees to degrees, minutes, seconds
    def decimal_to_dms(decimal):
        degrees = int(decimal)
        minutes_float = (decimal - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return (degrees, minutes, seconds)
    
    # Prepare latitude data
    lat_dms = decimal_to_dms(abs(latitude))
    lat_ref = 'N' if latitude >= 0 else 'S'
    
    # Prepare longitude data
    lon_dms = decimal_to_dms(abs(longitude))
    lon_ref = 'E' if longitude >= 0 else 'W'
    
    # Prepare GPS tags
    gps_tags = {
        'GPSLatitude': lat_dms,
        'GPSLatitudeRef': lat_ref,
        'GPSLongitude': lon_dms,
        'GPSLongitudeRef': lon_ref,
    }
    
    # Add altitude if provided
    if altitude is not None:
        gps_tags['GPSAltitude'] = abs(altitude)
        gps_tags['GPSAltitudeRef'] = 1 if altitude < 0 else 0
    
    # Write GPS tags to the image
    write_exif(image_path, gps_tags)
    print(f"GPS coordinates added to {image_path}")

# Example usage
if __name__ == "__main__":
    # Add coordinates for the Eiffel Tower
    add_gps_coordinates(
        "path/to/your/image.jpg",
        latitude=48.858844,
        longitude=2.294351,
        altitude=330  # meters
    )
```

## Batch Geotagging

The following example shows how to geotag multiple images based on a CSV file:

```python
import os
import csv
from tagkit.image_exif import write_exif

def batch_geotag_from_csv(csv_file, image_directory):
    """Geotag multiple images based on coordinates in a CSV file.
    
    Expected CSV format:
    filename,latitude,longitude,altitude
    image1.jpg,48.858844,2.294351,330
    image2.jpg,40.748817,-73.985428,10
    """
    # Read the CSV file
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        # Process each row
        for row in reader:
            # Get image path
            filename = row['filename']
            image_path = os.path.join(image_directory, filename)
            
            # Check if file exists
            if not os.path.isfile(image_path):
                print(f"Warning: File not found: {image_path}")
                continue
            
            try:
                # Parse coordinates
                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                
                # Parse altitude if available
                altitude = None
                if 'altitude' in row and row['altitude']:
                    altitude = float(row['altitude'])
                
                # Convert decimal degrees to degrees, minutes, seconds
                def decimal_to_dms(decimal):
                    degrees = int(decimal)
                    minutes_float = (decimal - degrees) * 60
                    minutes = int(minutes_float)
                    seconds = (minutes_float - minutes) * 60
                    return (degrees, minutes, seconds)
                
                # Prepare latitude data
                lat_dms = decimal_to_dms(abs(latitude))
                lat_ref = 'N' if latitude >= 0 else 'S'
                
                # Prepare longitude data
                lon_dms = decimal_to_dms(abs(longitude))
                lon_ref = 'E' if longitude >= 0 else 'W'
                
                # Prepare GPS tags
                gps_tags = {
                    'GPSLatitude': lat_dms,
                    'GPSLatitudeRef': lat_ref,
                    'GPSLongitude': lon_dms,
                    'GPSLongitudeRef': lon_ref,
                }
                
                # Add altitude if provided
                if altitude is not None:
                    gps_tags['GPSAltitude'] = abs(altitude)
                    gps_tags['GPSAltitudeRef'] = 1 if altitude < 0 else 0
                
                # Write GPS tags to the image
                write_exif(image_path, gps_tags)
                print(f"Geotagged: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    print("Batch geotagging completed")

# Example usage
if __name__ == "__main__":
    batch_geotag_from_csv("coordinates.csv", "path/to/your/images")
```

## Mapping Images on a Map

The following example shows how to create a simple HTML map with image locations:

```python
import os
import json
from tagkit.image_exif import read_exif

def create_image_map(image_directory, output_html):
    """Create an HTML map with markers for geotagged images."""
    # Collect image data
    images = []
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Process all images in the directory
    for root, _, files in os.walk(image_directory):
        for filename in files:
            if filename.lower().endswith(image_extensions):
                file_path = os.path.join(root, filename)
                
                try:
                    # Read EXIF data
                    tags = read_exif(file_path)
                    
                    # Check if GPS data exists
                    if not any(key.startswith('GPS') for key in tags):
                        continue
                    
                    # Extract latitude
                    if 'GPSLatitude' in tags and 'GPSLatitudeRef' in tags:
                        lat = tags['GPSLatitude']
                        lat_ref = tags['GPSLatitudeRef']
                        
                        # Convert to decimal degrees
                        lat_deg = lat[0] + lat[1]/60 + lat[2]/3600
                        if lat_ref == 'S':
                            lat_deg = -lat_deg
                    else:
                        continue
                    
                    # Extract longitude
                    if 'GPSLongitude' in tags and 'GPSLongitudeRef' in tags:
                        lon = tags['GPSLongitude']
                        lon_ref = tags['GPSLongitudeRef']
                        
                        # Convert to decimal degrees
                        lon_deg = lon[0] + lon[1]/60 + lon[2]/3600
                        if lon_ref == 'W':
                            lon_deg = -lon_deg
                    else:
                        continue
                    
                    # Get image title from EXIF if available
                    title = tags.get('ImageDescription', os.path.basename(file_path))
                    
                    # Add to images list
                    images.append({
                        'filename': os.path.basename(file_path),
                        'path': os.path.relpath(file_path, image_directory),
                        'latitude': lat_deg,
                        'longitude': lon_deg,
                        'title': title
                    })
                    
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    # Create HTML with Leaflet map
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Map</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            #map {{ height: 600px; width: 100%; }}
            .popup-image {{ max-width: 200px; max-height: 200px; }}
        </style>
    </head>
    <body>
        <h1>Image Map</h1>
        <div id="map"></div>
        <script>
            // Image data
            const images = {json.dumps(images)};
            
            // Create map
            const map = L.map('map');
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            
            // Add markers for each image
            const markers = [];
            images.forEach(image => {{
                const marker = L.marker([image.latitude, image.longitude])
                    .bindPopup(`
                        <h3>${{image.title}}</h3>
                        <img src="${{image.path}}" class="popup-image" />
                        <p>Coordinates: ${{image.latitude.toFixed(6)}}, ${{image.longitude.toFixed(6)}}</p>
                    `);
                markers.push(marker);
                marker.addTo(map);
            }});
            
            // Fit map to markers
            if (markers.length > 0) {{
                const group = L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.1));
            }} else {{
                map.setView([0, 0], 2);
            }}
        </script>
    </body>
    </html>
    '''
    
    # Write HTML file
    with open(output_html, 'w') as f:
        f.write(html)
    
    print(f"Created map with {len(images)} images at {output_html}")

# Example usage
if __name__ == "__main__":
    create_image_map("path/to/your/images", "image_map.html")
```

## Reverse Geocoding

The following example shows how to add location names based on GPS coordinates:

```python
import os
import requests
import time
from tagkit.image_exif import read_exif, write_exif

def reverse_geocode(latitude, longitude):
    """Convert GPS coordinates to a location name using Nominatim API."""
    # Use OpenStreetMap Nominatim API
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1"
    
    # Add a user agent as required by Nominatim
    headers = {
        "User-Agent": "tagkit-example-script/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Extract location information
        address = data.get("address", {})
        
        # Build location string
        location_parts = []
        
        # Add city or town
        if "city" in address:
            location_parts.append(address["city"])
        elif "town" in address:
            location_parts.append(address["town"])
        elif "village" in address:
            location_parts.append(address["village"])
        
        # Add county/state
        if "county" in address:
            location_parts.append(address["county"])
        elif "state" in address:
            location_parts.append(address["state"])
        
        # Add country
        if "country" in address:
            location_parts.append(address["country"])
        
        # Join parts
        location = ", ".join(location_parts)
        
        return location
    
    except Exception as e:
        print(f"Error in reverse geocoding: {e}")
        return None

def add_location_names_to_images(directory):
    """Add location names to images based on their GPS coordinates."""
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Process all images in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(image_extensions):
            file_path = os.path.join(directory, filename)
            
            try:
                # Read EXIF data
                tags = read_exif(file_path)
                
                # Check if GPS data exists
                if not any(key.startswith('GPS') for key in tags):
                    print(f"No GPS data in {filename}, skipping")
                    continue
                
                # Extract latitude
                if 'GPSLatitude' in tags and 'GPSLatitudeRef' in tags:
                    lat = tags['GPSLatitude']
                    lat_ref = tags['GPSLatitudeRef']
                    
                    # Convert to decimal degrees
                    lat_deg = lat[0] + lat[1]/60 + lat[2]/3600
                    if lat_ref == 'S':
                        lat_deg = -lat_deg
                else:
                    print(f"No latitude data in {filename}, skipping")
                    continue
                
                # Extract longitude
                if 'GPSLongitude' in tags and 'GPSLongitudeRef' in tags:
                    lon = tags['GPSLongitude']
                    lon_ref = tags['GPSLongitudeRef']
                    
                    # Convert to decimal degrees
                    lon_deg = lon[0] + lon[1]/60 + lon[2]/3600
                    if lon_ref == 'W':
                        lon_deg = -lon_deg
                else:
                    print(f"No longitude data in {filename}, skipping")
                    continue
                
                # Get location name
                location = reverse_geocode(lat_deg, lon_deg)
                
                if location:
                    # Add location to image metadata
                    tags_to_write = {
                        'City': location.split(',')[0].strip() if ',' in location else location,
                        'Country': location.split(',')[-1].strip() if ',' in location else '',
                        'Location': location
                    }
                    
                    write_exif(file_path, tags_to_write)
                    print(f"Added location '{location}' to {filename}")
                
                # Be nice to the API and avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage
if __name__ == "__main__":
    add_location_names_to_images("path/to/your/images")
```

## Next Steps

Now that you've learned how to work with GPS data, check out:

- [Photo Organizer Example](photo_organizer.md) for organizing your photo collection
- [Web Integration Example](web_integration.md) for integrating with web applications
