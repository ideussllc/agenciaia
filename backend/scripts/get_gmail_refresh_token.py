"""
Script de un solo uso para obtener el GMAIL_REFRESH_TOKEN.

Uso:
    cd backend
    python3 scripts/get_gmail_refresh_token.py

Pide el Client ID y Client Secret (los de la app de escritorio creada en
Google Cloud Console), abre el navegador para el consentimiento, y al
finalizar imprime el refresh_token para copiarlo a backend/.env.

IMPORTANTE: en la pantalla de login de Google que se abre, usa la cuenta
que va a enviar los borradores (ventas@ideuss.com, o latorres@ideuss.com si
administra ese alias) - no tu cuenta personal si es distinta.
"""
import http.server
import os
import threading
import urllib.parse
import webbrowser

import httpx

REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
SCOPE = "https://www.googleapis.com/auth/gmail.compose"

_result = {}


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _result["code"] = params.get("code", [None])[0]
        _result["error"] = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h1>Listo, ya puedes cerrar esta pestaña.</h1>".encode())

    def log_message(self, format, *args):
        pass


def main():
    client_id = os.getenv("GMAIL_CLIENT_ID") or input("Client ID: ").strip()
    client_secret = os.getenv("GMAIL_CLIENT_SECRET") or input("Client Secret: ").strip()

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    })

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), _CallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("\nAbriendo el navegador para iniciar sesion.")
    print("IMPORTANTE: usa la cuenta ventas@ideuss.com (o la que administre ese alias).\n")
    print(f"Si no se abre solo, entra manualmente a:\n{auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=180)

    if _result.get("error"):
        print(f"Google devolvio un error: {_result['error']}")
        return

    code = _result.get("code")
    if not code:
        print("No se recibio el codigo de autorizacion (tiempo agotado o cancelado).")
        return

    token_resp = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()

    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        print("Google no devolvio un refresh_token. Esto pasa si ya autorizaste esta app antes.")
        print("Solucion: ve a https://myaccount.google.com/permissions (con la cuenta ventas@ideuss.com),")
        print("revoca el acceso a esta app, y vuelve a correr este script.")
        print("Respuesta completa:", token_data)
        return

    print("\nListo. Copia esta linea a backend/.env:\n")
    print(f"GMAIL_REFRESH_TOKEN={refresh_token}")


if __name__ == "__main__":
    main()
