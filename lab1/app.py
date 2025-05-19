# app.py
import streamlit as st
import numpy as np
from element import Element

st.set_page_config(page_title="Solve H t + P = 0", layout="wide")

st.title("📐 Visual Finite-Element Solver")

# 1) Sidebar inputs
st.sidebar.header("Global parameters")
ME      = st.sidebar.number_input("Number of elements (ME)",   min_value=1, value=2, step=1)
LG      = st.sidebar.number_input("Total length (LG)",         min_value=0.1, value=5.0)
S       = st.sidebar.number_input("Area (S)",                  min_value=0.1, value=2.0)
k       = st.sidebar.number_input("Conductivity (k)",          min_value=0.0, value=50.0)
alpha   = st.sidebar.number_input("Conv. coeff. (α)",          min_value=0.0, value=10.0)
q       = st.sidebar.number_input("Heat flux (q)",             value=-150.0)
t_sr    = st.sidebar.number_input("Ambient temp. (t_sr)",      value=400.0)
dir_val = st.sidebar.radio("Flow direction (dir)", options=(1, -1), index=0)

delta_L = LG / ME

if st.sidebar.button("🔢 Solve"):
    # 2) build elements & assemble
    MN = ME + 1
    H_final = np.zeros((MN, MN))
    P_final = np.zeros((MN, 1))
    elements = []
    for i in range(ME):
        el = Element(length=delta_L, S=S, k=k,
                     alpha=alpha, q=q, t_sr=t_sr,
                     dir=dir_val,
                     is_start=(i==0), is_end=(i==ME-1))
        elements.append(el)
        # assemble
        for r in range(2):
            for c in range(2):
                H_final[i+r, i+c] += el.H[r, c]
        for r in range(2):
            P_final[i+r, 0] += el.P[r, 0]

    # 3) helper to convert numpy → LaTeX bmatrix
    def to_latex(A: np.ndarray) -> str:
        rows = [" & ".join(f"{v:.2f}" for v in row) for row in A]
        body = r"\\ ".join(rows)
        return rf"\begin{{bmatrix}}{body}\end{{bmatrix}}"

    # 4) display
    st.subheader("Assembled Matrices")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**\(H\) matrix:**")
        st.latex(r"H = " + to_latex(H_final))
        # st.dataframe(H_final, width=300)
    with col2:
        st.markdown("**\(P\) vector:**")
        st.latex(r"P = " + to_latex(P_final))
        # st.dataframe(P_final, width=200)

    st.markdown("**Equation to solve:**")
    st.latex(r"H\,t + P = 0")

    # 5) solve and show t
    t = Element.solve_equation(H_final, P_final)
    st.subheader("Solution vector \(t\)")
    st.latex(r"t = " + to_latex(t.reshape(-1,1)))
    # st.dataframe(t, width=200)
