from .element import Element


class ElementsSet:

    def __init__(self):
        self.k = k  # W/mk
        self.alfa = alfa  # W/m2K
        self.S = S  # m^2
        self.LG = 5  # m - długość

        q = -150  # W/m^2
        t_sr = 400  # K

        ME = 5  # liczba elemetów
        MN = ME + 1  # licza węzłów
        self._elements: list[Element] = []

