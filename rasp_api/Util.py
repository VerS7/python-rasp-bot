# -*- coding: utf-8 -*-
from io import BytesIO
import glob
import os


class Util(object):
    """Утилитарные функции"""
    @staticmethod
    def img_clear(path: str) -> None:
        """Удаление всех картинок по заданному пути"""
        try:
            imgs = glob.glob(path)
            for x in imgs:
                os.remove(x)
        except Exception as e:
            print(e)

    @staticmethod
    def pilobj_to_bytes(pilobj):
        """Создаёт байт-код из объекта Pillow"""
        try:
            bytes_ = BytesIO()
            pilobj.save(bytes_, format='png')
            bytes_.seek(0)
            return bytes_
        except Exception as e:
            print(e)

    @staticmethod
    def pilobjs_to_bytes(pilobjs):
        """Создаёт байт-код из объектов Pillow"""
        try:
            byteslist = []
            for obj in pilobjs:
                bytes_ = BytesIO()
                obj.save(bytes_, format='png')
                bytes_.seek(0)
                byteslist.append(bytes_)
            return byteslist
        except Exception as e:
            print(e)
