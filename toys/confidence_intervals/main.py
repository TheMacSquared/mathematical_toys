import webview
from threading import Thread
import time
from app import app

def start_flask():
    """Uruchom Flask w tle (daemon thread)"""
    app.run(port=5002, debug=False, use_reloader=False)

def main():
    # Uruchom Flask
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Poczekaj na inicjalizację Flask
    time.sleep(1)

    # Utwórz okno PyWebView
    window = webview.create_window(
        title='Przedziały Ufności - Quiz',
        url='http://127.0.0.1:5002',
        width=1000,
        height=900,
        resizable=True,
        min_size=(800, 700)
    )

    webview.start()

if __name__ == '__main__':
    main()
