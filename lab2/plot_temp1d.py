import matplotlib.pyplot as plt
import numpy as np

# Wczytanie danych
filename = "temperat.txt"

# Pomijamy pierwszy wiersz nagłówka i odczytujemy kolumny
time = []
t_center = []
t_surface = []
dT = []

with open(filename, 'r') as f:
    next(f)  # pomiń nagłówek
    for line in f:
        parts = line.strip().split()
        if len(parts) == 4:
            time.append(float(parts[0]))
            t_center.append(float(parts[1]))
            t_surface.append(float(parts[2]))
            dT.append(float(parts[3]))

time = np.array(time)
t_center = np.array(t_center)
t_surface = np.array(t_surface)
dT = np.array(dT)

# Wykresy
plt.figure(figsize=(10, 6))
plt.plot(time, t_surface, label="1 – powierzchnia", linewidth=2)
plt.plot(time, t_center, label="2 – oś", linewidth=2)
plt.xlabel("Czas [s]")
plt.ylabel("Temperatura [°C]")
plt.title("Rozkład temperatury – TEMP1D")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Drugi wykres: różnica temperatur
plt.figure(figsize=(10, 5))
plt.plot(time, dT, label="ΔT = Tp - Tc", color='black')
plt.xlabel("Czas [s]")
plt.ylabel("Różnica temperatur [°C]")
plt.title("Różnica temperatury między powierzchnią a osią")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
