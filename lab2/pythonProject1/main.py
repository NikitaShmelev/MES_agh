import numpy as np
from scipy.linalg import solve_banded
import sys

# ===================================================================================
# PROGRAM: TEMP1D (wersja Python)
# ... (reszta komentarzy bez zmian)
# ===================================================================================

def temp_1d(Rmin, Rmax, AlfaAir, TempBegin, t1, t2, C, Ro, K, Tau1, Tau2):
    # --- Inicjalizacja parametrów symulacji ---
    nh = 51
    ne = nh - 1
    Np = 2
    a = K / (C * Ro)
    E = np.array([-0.5773502692, 0.5773502692])
    W = np.array([1.0, 1.0])
    N1 = 0.5 * (1 - E)
    N2 = 0.5 * (1 + E)

    # --- Tworzenie siatki i warunki początkowe ---
    dR = (Rmax - Rmin) / ne
    
    # Obliczenie kroku czasowego i liczby kroków
    dTau_stable = (dR**2) / (0.5 * a) # Użycie formuły z kodu FORTRAN dla wierności
    TauMax = Tau1 + Tau2
    if TauMax > 0:
        nTime = int(TauMax / dTau_stable) + 1
        dTau = TauMax / nTime
    else:
        nTime = 0
        dTau = 0

    vrtxCoordX = np.linspace(Rmin, Rmax, nh)
    vrtxTemp = np.full(nh, TempBegin, dtype=np.float64)

    aC, aD, aE, aB = np.zeros(nh), np.zeros(nh), np.zeros(nh), np.zeros(nh)
    dTmax = 0.0
    Tau = 0.0

    # --- Główna pętla czasowa ---
    try:
        with open('temperat_py.txt', 'w') as nPrint:
            nPrint.write(f'{"Time,s":>12} {"T_center,C":>15} {"T_surface,C":>15} {"DeltaT,C":>15}\n')
            nPrint.write("************************************************************\n")

            for iTime in range(nTime):
                aC.fill(0); aD.fill(0); aE.fill(0); aB.fill(0)
                TempAir = t1 if Tau < Tau1 else t2

                for ie in range(ne):
                    r = vrtxCoordX[ie:ie+2]
                    TempTau = vrtxTemp[ie:ie+2]
                    dR_elem = r[1] - r[0]
                    Alfa = AlfaAir if ie == ne - 1 else 0.0
                    Ke = np.zeros((2, 2))
                    Fe = np.zeros(2)

                    for ip in range(Np):
                        Rp = N1[ip] * r[0] + N2[ip] * r[1]
                        TpTau = N1[ip] * TempTau[0] + N2[ip] * TempTau[1]
                        stiffness_term = K * Rp * W[ip] / dR_elem
                        capacity_term = C * Ro * dR_elem * Rp * W[ip] / dTau
                        load_vector_C = C * Ro * dR_elem * TpTau * Rp * W[ip] / dTau
                        
                        Ke[0, 0] += stiffness_term + capacity_term * N1[ip]**2
                        Ke[0, 1] += -stiffness_term + capacity_term * N1[ip] * N2[ip]
                        Ke[1, 0] = Ke[0, 1]
                        Ke[1, 1] += stiffness_term + capacity_term * N2[ip]**2
                        Fe[0] += load_vector_C * N1[ip]
                        Fe[1] += load_vector_C * N2[ip]

                    if Alfa > 0:
                        Ke[1, 1] += 2 * Alfa * Rmax
                        Fe[1] += 2 * Alfa * Rmax * TempAir

                    i_glob = ie
                    aD[i_glob]     += Ke[0, 0]
                    aD[i_glob + 1] += Ke[1, 1]
                    aE[i_glob]     += Ke[0, 1]
                    aC[i_glob + 1] += Ke[1, 0]
                    aB[i_glob]     += Fe[0]
                    aB[i_glob + 1] += Fe[1]

                ab = np.zeros((3, nh)); ab[0, 1:] = aE[:-1]; ab[1, :] = aD; ab[2, :-1] = aC[1:]
                
                try:
                    vrtxTemp = solve_banded((1, 1), ab, aB)
                except np.linalg.LinAlgError:
                    print("Błąd: Macierz osobliwa."); sys.exit(1)

                dT_current = abs(vrtxTemp[-1] - vrtxTemp[0])
                if dT_current > dTmax: dTmax = dT_current
                
                # Zapisuj co pewien czas, aby plik nie był zbyt duży
                if iTime % 5 == 0:
                    nPrint.write(f"{Tau:12.2f} {vrtxTemp[0]:15.2f} {vrtxTemp[-1]:15.2f} {dT_current:15.2f}\n")
                
                Tau += dTau

            nPrint.write("************************************************************\n")
            nPrint.write(f"dTmax = {dTmax:12.2f}\n")
        print("Symulacja zakończona pomyślnie. Wyniki zapisano do pliku 'temperat_py.txt'.")
    except IOError:
        print("Błąd: Nie można otworzyć pliku do zapisu 'temperat_py.txt'.")

# ===================================================================================
# Główny blok programu
# ===================================================================================
if __name__ == '__main__':
    # ========================================================================
    # ZMIANA: Dane wejściowe poprawione zgodnie z Rys. 6.5 z dokumentu PDF,
    # aby odtworzyć wykres z Rys. 6.7.
    # ========================================================================
    Rmin = 0.0          # Promień minimalny, m 
    Rmax = 0.05         # Promień maksymalny, m 
    AlfaAir = 300.0     # Współczynnik konwekcji, W/(m^2*K) 
    TempBegin = 100.0   # Temperatura początkowa, C 
    t1 = 1200.0         # Temperatura otoczenia, C 
    t2 = 1200.0         # Temperatura otoczenia (faza 2, nieużywana)
    C = 700.0           # Ciepło właściwe, J/(kg*C) 
    Ro = 7800.0         # Gęstość, kg/m3 
    K = 25.0            # Przewodność cieplna, W/(mC) 
    Tau1 = 1000.0       # Czas procesu, s (odpowiada TauMax) 
    Tau2 = 0.0          # Czas fazy 2 (nieużywana)
    # ========================================================================

    temp_1d(Rmin, Rmax, AlfaAir, TempBegin, t1, t2, C, Ro, K, Tau1, Tau2)