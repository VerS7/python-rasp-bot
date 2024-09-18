"""
Utility logic
"""

from typing import Union, List
from pathlib import Path
from io import BytesIO
from PIL import Image


def image_to_bytes(images: Union[List[Image.Image], Image.Image]) -> List[bytes]:
    """
    :param images: list of Image.Image or Image.Image object
    :return: list of bytes from Image.Image objects
    """
    __images = []
    __output = []

    if isinstance(images, list):
        __images = images
    if isinstance(images, Image.Image):
        __images.append(images)

    for image in __images:
        with BytesIO() as output:
            image.save(output, format="PNG")
            __output.append(output.getvalue())

    return __output


def load_txt(path: str) -> str:
    """
    :param path: txt file path
    :return: string of txt contain
    """
    _path = Path(path)
    if _path.exists():
        if _path.suffix == ".txt":
            with open(path, "r", encoding="utf-8") as textfile:
                return textfile.read()
        else:
            raise FileNotFoundError("File is not .txt")
    else:
        raise FileNotFoundError("File not found by path")
