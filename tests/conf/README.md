This directory contains configuration to generate test images.

The metadata files are in JSON format and contain a dictionary of image filenames
and their corresponding tags.

These files are validated using Pydantic models defined in `src/tagkit/conf/models.py`
(specifically the `ImageMetadataConfig` model).

The tags are in the following format:

```json
{
    "filename": {
        "tags": [
            {
                "id": 271,
                "name": "Make",
                "value": "Tagkit",
                "ifd": "0th"
            },
            {
                "id": 272,
                "name": "Model",
                "value": "Test Camera",
                "ifd": "0th"
            }
        ]
    }
}
```

Images are created by the `create_test_images_from_metadata` function in
`tests/conftest.py`.

`base.jpg` is a metadata-free, 100×100 white RGB JPEG generated for this project.
The helper uses this fixed image and inserts the configured EXIF with `piexif`,
so tests and doctests do not need an image rendering dependency. Keep this base
image free of EXIF; image metadata belongs in the JSON configuration files.

Configuration validation is performed in `tests/test_conf_schemas.py`.
