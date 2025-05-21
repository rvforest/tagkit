# Batch Processing Example

This example demonstrates how to efficiently process multiple image files using tagkit.

## Processing Files in a Directory

The following example shows how to process all image files in a directory:

```python
import os
from tagkit.image_exif import read_exif, write_exif

def process_directory(directory_path):
    """Process all image files in a directory."""
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Count of processed files
    processed_count = 0
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is an image
        if filename.lower().endswith(image_extensions):
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Process the image file
                process_image(file_path)
                processed_count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    print(f"Processed {processed_count} image files")

def process_image(image_path):
    """Process a single image file."""
    # Read existing tags
    tags = read_exif(image_path)
    
    # Perform your processing here
    # For example, add a copyright tag
    tags_to_write = {"Copyright": "© 2025 Your Name"}
    
    # Write tags back to the image
    write_exif(image_path, tags_to_write)
    print(f"Processed: {image_path}")

# Example usage
if __name__ == "__main__":
    process_directory("path/to/your/images")
```

## Parallel Processing with Concurrent Futures

For faster processing of large collections, you can use parallel execution:

```python
import os
import concurrent.futures
from tagkit.image_exif import read_exif, write_exif

def process_image(image_path):
    """Process a single image file."""
    try:
        # Read existing tags
        tags = read_exif(image_path)
        
        # Perform your processing here
        # For example, add a copyright tag
        tags_to_write = {"Copyright": "© 2025 Your Name"}
        
        # Write tags back to the image
        write_exif(image_path, tags_to_write)
        return f"Processed: {image_path}"
    except Exception as e:
        return f"Error processing {image_path}: {e}"

def batch_process_images(directory_path, max_workers=4):
    """Process all image files in a directory using parallel execution."""
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Collect all image files
    image_files = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, filename))
    
    # Process files in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_image, image_files))
    
    # Print results
    for result in results:
        print(result)
    
    print(f"Processed {len(image_files)} image files")

# Example usage
if __name__ == "__main__":
    batch_process_images("path/to/your/images", max_workers=8)
```

## Processing with Progress Tracking

For long-running batch operations, it's helpful to show progress:

```python
import os
import time
from tqdm import tqdm  # You'll need to install this: pip install tqdm
from tagkit.image_exif import read_exif, write_exif

def process_directory_with_progress(directory_path):
    """Process all image files in a directory with progress tracking."""
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Collect all image files
    image_files = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, filename))
    
    # Process files with progress bar
    for image_path in tqdm(image_files, desc="Processing images"):
        try:
            # Read existing tags
            tags = read_exif(image_path)
            
            # Perform your processing here
            # For example, add a copyright tag
            tags_to_write = {"Copyright": "© 2025 Your Name"}
            
            # Write tags back to the image
            write_exif(image_path, tags_to_write)
            
            # Small delay to avoid overwhelming the filesystem
            time.sleep(0.01)
        except Exception as e:
            print(f"\nError processing {image_path}: {e}")
    
    print(f"Processed {len(image_files)} image files")

# Example usage
if __name__ == "__main__":
    process_directory_with_progress("path/to/your/images")
```

## Batch Processing with Filtering

You can filter images based on their existing metadata:

```python
import os
from tagkit.image_exif import read_exif, write_exif

def process_directory_with_filter(directory_path, filter_func):
    """Process image files that match a filter criteria."""
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif', '.png')
    
    # Count of processed files
    processed_count = 0
    skipped_count = 0
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is an image
        if filename.lower().endswith(image_extensions):
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Read existing tags
                tags = read_exif(file_path)
                
                # Apply filter
                if filter_func(tags):
                    # Process the image file
                    tags_to_write = {"Processed": "Yes"}
                    write_exif(file_path, tags_to_write)
                    processed_count += 1
                    print(f"Processed: {filename}")
                else:
                    skipped_count += 1
                    print(f"Skipped: {filename} (didn't match filter criteria)")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    print(f"Processed {processed_count} image files, skipped {skipped_count}")

# Example filter function: only process images taken with a specific camera
def camera_filter(tags):
    camera_model = tags.get("Model", "")
    return "Canon" in camera_model

# Example usage
if __name__ == "__main__":
    process_directory_with_filter("path/to/your/images", camera_filter)
```

## Using the Operations Module

Tagkit provides an operations module for common batch tasks:

```python
from tagkit.operations import batch_process_images

def add_copyright(image_path):
    """Add copyright information to an image."""
    return {
        "Copyright": "© 2025 Your Name",
        "Artist": "Your Name"
    }

# Process all images in a directory and its subdirectories
batch_process_images(
    directory="path/to/your/images",
    process_func=add_copyright,
    recursive=True,
    max_workers=4
)
```

## Next Steps

Now that you've learned about batch processing, check out:

- [Custom Tags Example](custom_tags.md) to learn how to work with custom tags
- [Metadata Analysis Example](metadata_analysis.md) for analyzing image collections
