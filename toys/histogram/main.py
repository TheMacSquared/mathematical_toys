"""
PyWebView wrapper dla aplikacji Histogram.

Uruchamia Flask server w tle i otwiera natywne okno aplikacji.
"""

import webview
from threading import Thread
import time
from app import app

PORT = 15000  # Wyższy port - mniejsze ryzyko blokady przez firewall

def start_flask():
    """Uruchom Flask server w osobnym wątku"""
    app.run(port=PORT, debug=False, use_reloader=False)

def main():
    """Główna funkcja - uruchom aplikację"""
    # Uruchom Flask w tle (daemon=True oznacza że wątek zakończy się gdy główny program się zamknie)
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Poczekaj chwilę na uruchomienie serwera Flask
    time.sleep(1)

    # Otwórz natywne okno aplikacji
    window = webview.create_window(
        title='Histogram - Rozkład Normalny',
        url=f'http://127.0.0.1:{PORT}',
        width=1200,
        height=900,
        resizable=True,
        min_size=(800, 600)
    )

    # Start event loop (blokuje aż okno zostanie zamknięte)
    webview.start()

if __name__ == '__main__':
    main()
