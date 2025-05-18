import os
from PIL import Image
import piexif

# Create output folder
os.makedirs("test_images", exist_ok=True)


def save_image_with_exif(filename, exif_dict):
    img = Image.new("RGB", (100, 100), color="white")
    exif_bytes = piexif.dump(exif_dict)
    img.save(f"test_images/{filename}", "jpeg", exif=exif_bytes)
    print(f"Saved {filename}")


# 1. Minimal EXIF
save_image_with_exif(
    "minimal.jpg",
    {
        "0th": {
            piexif.ImageIFD.Make: b"TestMake",
            piexif.ImageIFD.Model: b"TestModel",
        },
        "Exif": {},
        "1st": {},
        "GPS": {},
        "thumbnail": None,
    },
)

# 2. Full EXIF with DateTimeOriginal and Software
save_image_with_exif(
    "datetime_software.jpg",
    {
        "0th": {
            piexif.ImageIFD.Software: b"MyExifTool",
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: b"2025:05:01 14:30:00",
        },
        "1st": {},
        "GPS": {},
        "thumbnail": None,
    },
)

# 3. With GPS info
save_image_with_exif(
    "with_gps.jpg",
    {
        "0th": {},
        "Exif": {},
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: b"N",
            piexif.GPSIFD.GPSLatitude: ((37, 1), (48, 1), (30, 1)),  # 37°48'30"
            piexif.GPSIFD.GPSLongitudeRef: b"W",
            piexif.GPSIFD.GPSLongitude: ((122, 1), (25, 1), (0, 1)),  # 122°25'0"
        },
        "1st": {},
        "thumbnail": None,
    },
)

# 4. With Unicode characters (will be encoded as UTF-8)
save_image_with_exif(
    "unicode.jpg",
    {
        "0th": {
            piexif.ImageIFD.Artist: "测试用户".encode("utf-8"),
        },
        "Exif": {},
        "1st": {},
        "GPS": {},
        "thumbnail": None,
    },
)

# 5. Corrupt EXIF: intentionally malformed (will cause errors on read)
img = Image.new("RGB", (100, 100), color="white")
img.save("test_images/corrupt.jpg", "jpeg", exif=b"garbage_exif_data")
print("Saved corrupt.jpg (invalid EXIF)")
