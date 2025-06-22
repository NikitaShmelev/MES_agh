import matplotlib.pyplot as plt
import csv
import time
import argparse 
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument('--nodes', type=int, default=51)
parser.add_argument('--time', type=float, default=1000.0)
args = parser.parse_args()

# Parametry
Rmin = 0.0
Rmax = 0.05
AlfaAir = 300.0
TempBegin = 100.0
t1 = 1200.0
t2 = 25.0
C = 700.0
Ro = 7800.0
K = 25.0
Tau1 = 0.0
Tau2 = args.time

nh = args.nodes
ne = nh - 1
Np = 2
a = K / (C * Ro)

E = [-0.5773502692, 0.5773502692]
W = [1.0, 1.0]
N1 = [0.5 * (1 - e) for e in E]
N2 = [0.5 * (1 + e) for e in E]

dR = (Rmax - Rmin) / ne
dTau = dR ** 2 / (0.5 * a)
TauMax = Tau1 + Tau2
nTime = int(TauMax / dTau) + 1
dTau = TauMax / nTime

vrtxCoordX = [Rmin + i * dR for i in range(nh)]
vrtxTemp = [TempBegin] * nh

time_history = []
t_center_history = []
t_surface_history = []
dT_list_history = []

Tau = 0.0

print(f"Krok czasowy dt = {dTau:.4f} s\nne={ne}")
start = time.time()
while Tau <= TauMax:
    time_history.append(Tau)
    t_center_history.append(vrtxTemp[0])
    t_surface_history.append(vrtxTemp[-1])
    dT_list_history.append(abs(vrtxTemp[0] - vrtxTemp[-1]))

    aC = [0.0] * nh
    aD = [0.0] * nh
    aE = [0.0] * nh
    aB = [0.0] * nh

    TempAir = t1  # stała temperatura otoczenia

    def assemble_element(ie):
        r1 = vrtxCoordX[ie]
        r2 = vrtxCoordX[ie + 1]
        t1e = vrtxTemp[ie]
        t2e = vrtxTemp[ie + 1]
        dR_local = r2 - r1
        Alfa = AlfaAir if ie == ne - 1 else 0.0

        Ke = [[0.0, 0.0], [0.0, 0.0]]
        Fe = [0.0, 0.0]

        for ip in range(Np):
            Rp = N1[ip] * r1 + N2[ip] * r2
            TpTau = N1[ip] * t1e + N2[ip] * t2e

            Ke[0][0] += K * Rp * W[ip] / dR_local + C * Ro * dR_local * Rp * W[ip] * N1[ip] ** 2 / dTau
            Ke[0][1] += -K * Rp * W[ip] / dR_local + C * Ro * dR_local * Rp * W[ip] * N1[ip] * N2[ip] / dTau
            Ke[1][0] = Ke[0][1]
            Ke[1][1] += K * Rp * W[ip] / dR_local + C * Ro * dR_local * Rp * W[ip] * N2[ip] ** 2 / dTau + 2 * Alfa * Rmax

            Fe[0] += C * Ro * dR_local * TpTau * Rp * W[ip] * N1[ip] / dTau
            Fe[1] += C * Ro * dR_local * TpTau * Rp * W[ip] * N2[ip] / dTau + 2 * Alfa * Rmax * TempAir

        return ie, Ke, Fe

    with ThreadPoolExecutor() as executor:
        results = executor.map(assemble_element, range(ne))

    for ie, Ke, Fe in results:
        aD[ie] += Ke[0][0]
        aD[ie + 1] += Ke[1][1]
        aE[ie] += Ke[0][1]
        aC[ie + 1] += Ke[1][0]
        aB[ie] += Fe[0]
        aB[ie + 1] += Fe[1]

    # Rozwiązanie układu równań metodą Thomasa
    for i in range(1, nh):
        m = aC[i] / aD[i - 1]
        aD[i] -= m * aE[i - 1]
        aB[i] -= m * aB[i - 1]

    aB[-1] /= aD[-1]
    for i in range(nh - 2, -1, -1):
        aB[i] = (aB[i] - aE[i] * aB[i + 1]) / aD[i]

    vrtxTemp = aB
    Tau += dTau

end = time.time()-start
print(f"Czas: {end:2f}s")

# Zapis do CSV
filename = f"dt_wyniki/wyniki_symulacji_{nh}.csv"
headers = ['Czas (s)', 'Temperatura w osi (C)', 'Temperatura na powierzchni (C)', 'Roznica dT (C)']

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    for row in zip(time_history, t_center_history, t_surface_history, dT_list_history):
        writer.writerow([f"{val:.4f}" for val in row])

print(f"Wyniki zostały zapisane do pliku: {filename}")

# Wykresy
plt.figure(figsize=(10, 7))
plt.plot(time_history, t_surface_history, label="1 – na powierzchni wsadu")
plt.plot(time_history, t_center_history, label="2 – w osi wsadu")
plt.xlabel("Czas [s]")
plt.ylabel("Temperatura [°C]")
plt.title("Wyniki obliczenia nagrzewania wsadu o przekroju okrągłym")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"dt_wykresy/temperatura_{nh}_{end}.png")
# plt.show()

plt.figure(figsize=(10, 7))
plt.plot(time_history, dT_list_history, label="ΔT", color="black")
plt.xlabel("Czas [s]")
plt.ylabel("Różnica temperatur [°C]")
plt.title("ΔT między powierzchnią a osią")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"dt_wykresy/delta_{nh}_{end}.png")
# plt.show()
