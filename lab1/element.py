import numpy as np
from typing import Optional

class Element:
    def __init__(
            self, length: float, S: float, k: float,
            alpha: float,
            q: float,
            t_sr: float,
            dir: int = 1,
            is_start: bool = False,
            is_end: bool = False,
    ) -> None:
        self.is_start: bool = is_start
        self.is_end: bool = is_end
        self.length: float = length
        self.q: float = q
        self.t_sr: float = t_sr
        self.S: float = S
        self.k: float = k
        self.alpha: float = alpha
        self.dir: int = dir  # 1 from left to right; -1 from right to left

        if not self.is_start:
            # we use it only in case of the first element
            self.q = 0
        if not self.is_end:
            # we use it only in case of the last element
            self.alpha = 0

        self.addon: Optional[any] = None
        self.C: float = self._calculate_C()
        self.H: np.ndarray = self._calculate_H()
        self.P: np.ndarray = self._calculate_P()

    def _calculate_C(self) -> float:
        return self.S * self.k / self.length

    def _calculate_P(self) -> np.ndarray:
        return np.array(
            [
                [
                    self.q * self.S
                    # != 0 only when element is FIRST
                ],
                [
                    -self.t_sr * self.alpha * self.S
                    # != 0 only when element is LAST
                ]
            ]
        )

    def _calculate_H(self) -> np.ndarray:
        # take a look later
        conv: float = self.alpha * self.S
        el_00: float = self.C + (conv if self.dir == -1 else 0)
        el_11: float = self.C + (conv if self.dir == 1 else 0)
        return np.array(
            [
                [el_00, -self.C],
                [-self.C, el_11]
            ]
        )

    @staticmethod
    def print_equation(H_lines: np.ndarray, P_lines: np.ndarray) -> None:
        H_lines = np.array2string(H_lines, separator=' ').splitlines()
        P_lines = np.array2string(P_lines, separator=' ').splitlines()

        # Zip and print
        t_ind: int = 1
        for H_line, P_line in zip(H_lines, P_lines):
            print(f"{H_line} |t_{t_ind}|   + {P_line}")
            t_ind += 1

    def print(self) -> None:
        H_lines: list[str] = np.array2string(self.H, separator=' ').splitlines()
        P_lines: list[str] = np.array2string(self.P, separator=' ').splitlines()

        # Zip and print
        for H_line, P_line in zip(H_lines, P_lines):
            print(f"{H_line}   {P_line}")
