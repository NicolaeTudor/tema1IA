from itertools import combinations, chain

from bidict import Bidict
from typing import Set, List, Union


class Singleton(type):
    """
        metaclass with Singleton behavior
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ColorSrv(metaclass=Singleton):
    def __init__(self):
        self.colors = Bidict()
        self.combinations = Bidict()
        self.nextCode = 1

    def reset(self):
        self.colors = Bidict()
        self.combinations = Bidict()
        self.nextCode = 1

    def add_color(self, color: str) -> int:
        """
            Adds the color to the bidirectional dictionary and assign a unique code to it
        :param color: the color to add
        :return: the code of the color
        """

        if color not in self.colors.keys():
            self.colors[color] = self.nextCode
            self.nextCode += 1

        return self.colors[color]

    def get_color(self, code: int) -> str:
        """
            gets the color associated to a code
        :param code: the color code for which we want the color
        :return: the color
        """
        if code == -1:
            return "undefined"
        if code == 0:
            return "-"

        return self.colors.inverse[code][0]

    def get_code(self, color: str) -> int:
        """
            Gets the code associated to a color
        :param color: the color for which  we want the code
        :return: the color code
        """

        return self.colors[color]

    def add_combination(self, code_l: int, code_r: int, code_f: int) -> None:
        """
            Define color coded `code_f` as a combination of `code_l` and `code_r`
        """

        self.combinations[(code_l, code_r)] = code_f
        self.combinations[(code_r, code_l)] = code_f

    def get_combination_result(self, code_l: int, code_r: int) -> int:
        """
            Gets the result of combining colors coded `code_l` and `code_r`
        :return: the color code of the resulted combination or -1 if undefined
        """
        if code_l == code_r:
            return code_l

        if (code_l, code_r) in self.combinations.keys():
            return self.combinations[(code_l, code_r)]

        if code_r == 0:
            return code_l

        return -1

    def deconstruct_color(self, code: int) -> Union[int, list]:
        if code not in self.combinations.inverse.keys():
            return -1
        dec = self.combinations.inverse[code]
        chained = chain(*dec)
        lst = list(chained)
        return lst
