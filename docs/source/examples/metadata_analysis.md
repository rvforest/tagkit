# Metadata Analysis Example

This example demonstrates how to analyze EXIF metadata across a collection of images using tagkit.

## Basic Metadata Statistics

The following example collects basic statistics about a collection of images:

```python
import os
from collections import Counter
from tagkit.image_exif import read_exif

def analyze_image_collection(directory):
    """Analyze EXIF metadata across a collection of images."""
    # Statistics to collect
    stats = {
        'total_images': 0,
        'cameras': Counter(),
        'lenses': Counter(),
        'focal_lengths': Counter(),
        'apertures': Counter(),
        'iso_values': Counter(),
        'has_gps': 0,
        'no_metadata': 0
    }
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Process all images in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(image_extensions):
            file_path = os.path.join(directory, filename)
            
            try:
                # Read EXIF data
                tags = read_exif(file_path)
                
                # Update statistics
                stats['total_images'] += 1
                
                # Check if image has any metadata
                if not tags:
                    stats['no_metadata'] += 1
                    continue
                
                # Camera model
                if 'Model' in tags:
                    stats['cameras'][tags['Model']] += 1
                
                # Lens model
                if 'LensModel' in tags:
                    stats['lenses'][tags['LensModel']] += 1
                
                # Focal length
                if 'FocalLength' in tags:
                    stats['focal_lengths'][str(tags['FocalLength'])] += 1
                
                # Aperture
                if 'FNumber' in tags:
                    stats['apertures'][f"f/{tags['FNumber']}"] += 1
                
                # ISO
                if 'ISO' in tags:
                    stats['iso_values'][str(tags['ISO'])] += 1
                
                # GPS data
                if any(key.startswith('GPS') for key in tags):
                    stats['has_gps'] += 1
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Print statistics
    print(f"Total images: {stats['total_images']}")
    print(f"Images without metadata: {stats['no_metadata']}")
    print(f"Images with GPS data: {stats['has_gps']}")
    
    print("\nTop 5 cameras:")
    for camera, count in stats['cameras'].most_common(5):
        print(f"  {camera}: {count}")
    
    print("\nTop 5 lenses:")
    for lens, count in stats['lenses'].most_common(5):
        print(f"  {lens}: {count}")
    
    print("\nTop 5 focal lengths:")
    for focal_length, count in stats['focal_lengths'].most_common(5):
        print(f"  {focal_length}mm: {count}")
    
    print("\nTop 5 apertures:")
    for aperture, count in stats['apertures'].most_common(5):
        print(f"  {aperture}: {count}")
    
    print("\nTop 5 ISO values:")
    for iso, count in stats['iso_values'].most_common(5):
        print(f"  ISO {iso}: {count}")
    
    return stats

# Example usage
if __name__ == "__main__":
    stats = analyze_image_collection("path/to/your/images")
```

## Timeline Analysis

This example analyzes when photos were taken over time:

```python
import os
from datetime import datetime
from collections import defaultdict
from tagkit.image_exif import read_exif

def analyze_photo_timeline(directory):
    """Analyze when photos were taken over time."""
    # Timeline data
    timeline = {
        'by_year': defaultdict(int),
        'by_month': defaultdict(int),
        'by_hour': defaultdict(int),
        'by_day_of_week': defaultdict(int)
    }
    
    # Day of week names
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Process all images in the directory
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(image_extensions):
                file_path = os.path.join(root, filename)
                
                try:
                    # Read EXIF data
                    tags = read_exif(file_path)
                    
                    # Check for date information
                    date_str = tags.get('DateTimeOriginal')
                    if not date_str:
                        continue
                    
                    # Parse the date
                    try:
                        date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                        
                        # Update timeline statistics
                        timeline['by_year'][date.year] += 1
                        timeline['by_month'][f"{date.year}-{date.month:02d}"] += 1
                        timeline['by_hour'][date.hour] += 1
                        timeline['by_day_of_week'][day_names[date.weekday()]] += 1
                        
                    except ValueError:
                        # Skip if date format is invalid
                        continue
                    
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    # Print timeline statistics
    print("Photos by year:")
    for year in sorted(timeline['by_year'].keys()):
        print(f"  {year}: {timeline['by_year'][year]}")
    
    print("\nPhotos by hour of day:")
    for hour in range(24):
        count = timeline['by_hour'].get(hour, 0)
        print(f"  {hour:02d}:00: {count}")
    
    print("\nPhotos by day of week:")
    for day in day_names:
        count = timeline['by_day_of_week'].get(day, 0)
        print(f"  {day}: {count}")
    
    return timeline

# Example usage
if __name__ == "__main__":
    timeline = analyze_photo_timeline("path/to/your/images")
```

## Camera Settings Analysis

This example analyzes the camera settings used across a collection:

```python
import os
import json
from collections import defaultdict
from tagkit.image_exif import read_exif

def analyze_camera_settings(directory, output_file=None):
    """Analyze camera settings across a collection of images."""
    # Settings data
    settings = {
        'exposure_time': defaultdict(int),
        'aperture': defaultdict(int),
        'iso': defaultdict(int),
        'focal_length': defaultdict(int),
        'camera_models': defaultdict(int),
        'lens_models': defaultdict(int),
        'exposure_program': defaultdict(int),
        'metering_mode': defaultdict(int),
        'flash': defaultdict(int),
        'settings_combinations': defaultdict(int)
    }
    
    # Exposure program names
    exposure_programs = {
        0: "Not defined",
        1: "Manual",
        2: "Normal program",
        3: "Aperture priority",
        4: "Shutter priority",
        5: "Creative program",
        6: "Action program",
        7: "Portrait mode",
        8: "Landscape mode"
    }
    
    # Metering mode names
    metering_modes = {
        0: "Unknown",
        1: "Average",
        2: "Center-weighted average",
        3: "Spot",
        4: "Multi-spot",
        5: "Pattern",
        6: "Partial"
    }
    
    # Flash status names
    flash_statuses = {
        0x0000: "No Flash",
        0x0001: "Flash Fired",
        0x0005: "Flash Fired, Return not detected",
        0x0007: "Flash Fired, Return detected",
        0x0008: "On, Flash did not fire",
        0x0009: "On, Flash fired",
        0x000D: "On, Return not detected",
        0x000F: "On, Return detected",
        0x0010: "Off, Flash did not fire",
        0x0018: "Auto, Flash did not fire",
        0x0019: "Auto, Flash fired",
        0x001D: "Auto, Return not detected",
        0x001F: "Auto, Return detected",
        0x0020: "No flash function",
        0x0041: "Red-eye reduction",
        0x0045: "Red-eye reduction, Return not detected",
        0x0047: "Red-eye reduction, Return detected",
        0x0049: "On, Red-eye reduction",
        0x004D: "On, Red-eye reduction, Return not detected",
        0x004F: "On, Red-eye reduction, Return detected",
        0x0059: "Auto, Red-eye reduction",
        0x005D: "Auto, Red-eye reduction, Return not detected",
        0x005F: "Auto, Red-eye reduction, Return detected"
    }
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Process all images in the directory
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(image_extensions):
                file_path = os.path.join(root, filename)
                
                try:
                    # Read EXIF data
                    tags = read_exif(file_path)
                    
                    # Extract camera settings
                    exposure_time = tags.get('ExposureTime')
                    aperture = tags.get('FNumber')
                    iso = tags.get('ISO')
                    focal_length = tags.get('FocalLength')
                    camera_model = tags.get('Model')
                    lens_model = tags.get('LensModel')
                    exposure_program = tags.get('ExposureProgram')
                    metering_mode = tags.get('MeteringMode')
                    flash = tags.get('Flash')
                    
                    # Update settings statistics
                    if exposure_time:
                        settings['exposure_time'][str(exposure_time)] += 1
                    
                    if aperture:
                        settings['aperture'][f"f/{aperture}"] += 1
                    
                    if iso:
                        settings['iso'][str(iso)] += 1
                    
                    if focal_length:
                        settings['focal_length'][f"{focal_length}mm"] += 1
                    
                    if camera_model:
                        settings['camera_models'][camera_model] += 1
                    
                    if lens_model:
                        settings['lens_models'][lens_model] += 1
                    
                    if exposure_program is not None:
                        program_name = exposure_programs.get(exposure_program, f"Unknown ({exposure_program})")
                        settings['exposure_program'][program_name] += 1
                    
                    if metering_mode is not None:
                        mode_name = metering_modes.get(metering_mode, f"Unknown ({metering_mode})")
                        settings['metering_mode'][mode_name] += 1
                    
                    if flash is not None:
                        flash_name = flash_statuses.get(flash, f"Unknown ({flash})")
                        settings['flash'][flash_name] += 1
                    
                    # Track combinations of settings
                    if aperture and exposure_time and iso:
                        combo = f"f/{aperture}, {exposure_time}s, ISO {iso}"
                        settings['settings_combinations'][combo] += 1
                    
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    # Convert defaultdicts to regular dicts for JSON serialization
    result = {
        category: dict(data) for category, data in settings.items()
    }
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Analysis saved to {output_file}")
    
    # Print some statistics
    print("Top 5 camera models:")
    for model, count in sorted(settings['camera_models'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {model}: {count}")
    
    print("\nTop 5 lens models:")
    for model, count in sorted(settings['lens_models'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {model}: {count}")
    
    print("\nTop 5 exposure programs:")
    for program, count in sorted(settings['exposure_program'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {program}: {count}")
    
    print("\nTop 5 settings combinations:")
    for combo, count in sorted(settings['settings_combinations'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {combo}: {count}")
    
    return result

# Example usage
if __name__ == "__main__":
    settings = analyze_camera_settings("path/to/your/images", "camera_settings_analysis.json")
```

## Next Steps

Now that you've learned how to analyze metadata, check out:

- [GPS Mapping Example](gps_mapping.md) for working with location data
- [Photo Organizer Example](photo_organizer.md) for organizing your photo collection
