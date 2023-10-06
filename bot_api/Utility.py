# -*- coding: utf-8 -*-
from PIL import Image
from io import BytesIO
from typing import Union, List


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
            image.save(output, format='PNG')
            __output.append(output.getvalue())

    return __output


