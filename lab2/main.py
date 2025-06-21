import matplotlib.pyplot as plt

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
Tau2 = 1000.0

nh = 51
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

# Siatka i początkowa temperatura
vrtxCoordX = [Rmin + i * dR for i in range(nh)]
vrtxTemp = [TempBegin] * nh

# Wyniki do wykresu
time = []
t_center = []
t_surface = []
dT_list = []

Tau = 0.0
for _ in range(nTime):
    aC = [0.0] * nh
    aD = [0.0] * nh
    aE = [0.0] * nh
    aB = [0.0] * nh

    TempAir = t2 if Tau < Tau1 else t1
    
    for ie in range(ne):
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

        aD[ie] += Ke[0][0]
        aD[ie + 1] += Ke[1][1]
        aE[ie] += Ke[0][1]
        aC[ie + 1] += Ke[1][0]
        aB[ie] += Fe[0]
        aB[ie + 1] += Fe[1]

    # Rozwiąż układ trójdiagonalny (jak solve_tridiagonal)
    for i in range(1, nh):
        m = aC[i] / aD[i - 1]
        aD[i] -= m * aE[i - 1]
        aB[i] -= m * aB[i - 1]

    aB[-1] /= aD[-1]
    for i in range(nh - 2, -1, -1):
        aB[i] = (aB[i] - aE[i] * aB[i + 1]) / aD[i]

    vrtxTemp = aB.copy()
    dT = abs(vrtxTemp[0] - vrtxTemp[-1])

    time.append(Tau)
    t_center.append(vrtxTemp[0])
    t_surface.append(vrtxTemp[-1])
    dT_list.append(dT)

    Tau += dTau

# Wykres temperatur
plt.plot(time, t_surface, label="1 – powierzchnia")
plt.plot(time, t_center, label="2 – oś")
plt.xlabel("Czas [s]")
plt.ylabel("Temperatura [°C]")
plt.title("Rozkład temperatury – Python")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Wykres dT
plt.plot(time, dT_list, label="ΔT", color="black")
plt.xlabel("Czas [s]")
plt.ylabel("Różnica temperatur [°C]")
plt.title("ΔT między powierzchnią a osią")
plt.grid(True)
plt.tight_layout()
plt.show()
