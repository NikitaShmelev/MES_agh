import pandas as pd
import matplotlib.pyplot as plt
import sys

# Nazwa pliku z wynikami symulacji
nazwa_pliku = 'temperat_py.txt'

try:
    # Wczytanie danych z pliku tekstowego przy użyciu biblioteki pandas.
    # skiprows=2 -> Pomiń dwie pierwsze linie nagłówka.
    # skipfooter=2 -> Pomiń dwie ostatnie linie stopki.
    # delim_whitespace=True -> Użyj białych znaków (spacje, tabulatory) jako separatora kolumn.
    # names=[...] -> Nadaj kolumnom czytelne nazwy.
    # engine='python' -> Wymagane, aby opcja 'skipfooter' działała poprawnie.
    dane = pd.read_csv(
        nazwa_pliku,
        skiprows=2,
        skipfooter=2,
        delim_whitespace=True,
        names=['Czas', 'T_srodek', 'T_powierzchnia', 'DeltaT'],
        engine='python'
    )

    # --- Tworzenie wykresu ---

    # Utworzenie figury i osi wykresu
    fig, ax = plt.subplots(figsize=(10, 6))

    # Narysowanie krzywej nr 1 (temperatura na powierzchni)
    ax.plot(dane['Czas'], dane['T_powierzchnia'], label='Na powierzchni wsadu (1)', color='black')

    # Narysowanie krzywej nr 2 (temperatura w osi/środku)
    ax.plot(dane['Czas'], dane['T_srodek'], label='W osi wsadu (2)', color='black')

    # Dodanie etykiet do osi, tytułu i legendy - stylizowane na Rys. 6.7
    ax.set_xlabel('Czas, s', fontsize=12)
    ax.set_ylabel('Temperatura, C', fontsize=12)
    ax.set_title('Wyniki obliczenia nagrzewania wsadu o przekroju okrągłym', fontsize=14)
    ax.legend(fontsize=12)

    # Ustawienie limitów osi, aby odpowiadały oryginalnemu wykresowi
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1200)

    # Włączenie siatki
    ax.grid(True)

    # Wyświetlenie wykresu
    plt.show()

except FileNotFoundError:
    print(f"Błąd: Plik wynikowy '{nazwa_pliku}' nie został znaleziony.")
    print("Upewnij się, że najpierw uruchomiłeś skrypt symulacyjny.")
    sys.exit(1)
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")
    sys.exit(1)