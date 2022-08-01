# -*- coding: utf-8 -*-


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
