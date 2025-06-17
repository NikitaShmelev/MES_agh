# ---- Budujemy środowisko wykonawcze ----
FROM python:3.12-slim AS base

# 1) Instalacje systemowe (ułatwiają instalację wheeli)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# 2) Ustawiamy zmienne i katalog roboczy
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080
WORKDIR /app

# 3) Instalujemy zależności z cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Kopiujemy kod źródłowy
COPY . .

# 5) Komenda startowa – Streamlit w trybie headless na zadanym porcie
CMD streamlit run app.py --server.port $PORT --server.headless true
