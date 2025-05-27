# Batch Processing Example

This example demonstrates how to efficiently process multiple image files using tagkit.

## Processing Files in a Directory

The following example shows how to process all image files in a directory:

```python
import os
from tagkit.image.exif import ExifImage

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
    # Create an ExifImage instance
    exif_image = ExifImage(image_path)

    # Perform your processing here
    # For example, add a copyright tag
    exif_image.set_tag("Copyright", " 2025 Your Name")

    # Save changes
    exif_image.save()
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
from tagkit.image.exif import ExifImage

def process_image(image_path):
    """Process a single image file."""
    try:
        # Create an ExifImage instance
        exif_image = ExifImage(image_path)

        # Perform your processing here
        # For example, add a copyright tag
        exif_image.set_tag("Copyright", " 2025 Your Name")

        # Save changes
        exif_image.save()
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
from tagkit.image.exif import ExifImage

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
            # Create an ExifImage instance
            exif_image = ExifImage(image_path)

            # Perform your processing here
            # For example, add a copyright tag
            exif_image.set_tag("Copyright", " 2025 Your Name")

            # Save changes
            exif_image.save()

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
from tagkit.image.exif import ExifImage

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
                # Create an ExifImage instance
                exif_image = ExifImage(file_path)

                # Apply filter
                if filter_func(exif_image.tags):
                    # Process the image file
                    exif_image.set_tag("Processed", "Yes")
                    exif_image.save()
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
    for tag in tags.values():
        if tag.name == "Model" and "Canon" in tag.value:
            return True
    return False

# Example usage
if __name__ == "__main__":
    process_directory_with_filter("path/to/your/images", camera_filter)
```
