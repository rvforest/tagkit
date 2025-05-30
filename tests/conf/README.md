This directory contains configuration to generate test images.

The metadata files are in JSON format and contain a dictionary of image filenames
and their corresponding tags.

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
