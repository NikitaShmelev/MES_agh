import numpy as np
from element import Element

# dane

k = 50 # W/mk
alpha = 10 # W/m2K
S = 2 # m^2
LG = 5 # m - długość

q = -150 # W/m^2
t_sr = 400 # K

ME = 5 # liczba elemetów
MN = ME + 1 # licza węzłów

delta_L = LG / ME

dir = 1 # 1 from left to right; -1 from right to left

# start


final_H = np.zeros(
    (MN, MN)
) # macież o rozmiarze ilość węzłów x ilość węzłów
final_P = np.zeros(
    (MN, 1)
)

elemnts = []

for i in range(ME):
    element: Element  = Element(
        length=delta_L,
        S=S,
        k=50,
        alpha=alpha,
        q=q,
        t_sr=t_sr,
        is_start = (i == 0),
        is_end = (i == ME-1)
    )
    elemnts.append(
        element
    )



for i in range(ME):
    element: Element = elemnts[i]
    matrix_h = element.H
    matrix_P = element.P
    for row_ind, row in enumerate(matrix_h):
        for col_ind, val in enumerate(row):
            final_H[i + row_ind][i + col_ind] += val


    for col_ind, val in enumerate(matrix_P):
        # breakpoint()
        final_P[i + col_ind][0] += val[0] # val should has only 1 element


    # break



Element.print_equation(
        final_H,
        final_P
    )
