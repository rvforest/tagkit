# Batch Processing Example

This guide demonstrates how to efficiently process multiple image files using tagkit.

## Command Line Interface

See [Reading Exif Tags](./reading.md) for examples on using the CLI to read EXIF data from multiple files.

## API

### Batch Reading Tags

To read EXIF tags from multiple images at once, use the `ExifImageCollection` class.
This class lets you load and access EXIF data for a group of files efficiently.

```{testcode}
from tagkit.image.collection import ExifImageCollection

# List of image file paths
image_files = [
    "image1.jpg",
    "image2.jpg",
    "image3.jpg"
]

# Create a collection for these files
collection = ExifImageCollection(image_files)

# Access EXIF data for each file as a dictionary
exif_data = collection.as_dict()

for filename, tags in exif_data.items():
    print(f"EXIF tags for {filename}:")
    for tag_name, tag_info in tags.items():
        print(f"  {tag_name}: {tag_info['value']}")
    print()
```

You can also get the total number of tags and files:

```{testcode}
print(f"Total files: {collection.n_files}")
print(f"Total tags: {collection.n_tags}")
```

### Batch Modifying Tags

You can set or remove tags for all or selected images in a collection using `write_tag` and `delete_tag`:

```{testcode}
from tagkit.image.collection import ExifImageCollection
collection = ExifImageCollection(["image1.jpg", "image2.jpg"])

# Set the camera make for all images
collection.write_tag("Make", "Tagkit Labs")

# Set the camera model for only one image
collection.write_tag("Model", "Special Edition", files=["image1.jpg"])

# Remove the camera model from one image
collection.delete_tag("Model", files=["image1.jpg"])

# Remove the camera make from all images
collection.delete_tag("Make")
```

### Saving All Changes

After modifying tags in a collection, you can save all changes at once:

```{testcode}
from tagkit.image.collection import ExifImageCollection

collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
collection.write_tag("Make", "Tagkit Labs")
collection.save_all(create_backup=True)
```
