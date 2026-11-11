"""Extractor etico (base del Kit de arranque): respeta robots.txt, se identifica y no satura sitios."""
import os
import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

# Cambia TDL_CONTACTO (variable de entorno / secret del repo) por tu usuario de GitHub o un correo de equipo.
CONTACTO = os.environ.get("TDL_CONTACTO", "github.com/USUARIO/tdl-ximena")
UA = f"TDL-Observatorio/1.0 (proyecto academico; contacto: {CONTACTO})"


class ExtractorEtico:
    def __init__(self, pausa=1.5):
        self.pausa = pausa  # segundos minimos entre peticiones al mismo dominio
        self.robots = {}
        self.ultimo = {}
        self.sesion = requests.Session()
        self.sesion.headers["User-Agent"] = UA

    def _reglas(self, url):
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self.robots:
            rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
            rp.read()
            self.robots[base] = rp
        return self.robots[base]

    def get(self, url, intentos=3):
        reglas = self._reglas(url)
        if not reglas.can_fetch(UA, url):
            raise PermissionError(f"robots.txt no permite {url}")
        dominio = urlparse(url).netloc
        pausa = max(self.pausa, reglas.crawl_delay(UA) or 0)
        espera = pausa - (time.time() - self.ultimo.get(dominio, 0))
        if espera > 0:
            time.sleep(espera)
        for i in range(intentos):
            r = self.sesion.get(url, timeout=30)
            self.ultimo[dominio] = time.time()
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(pausa * 2 ** i)  # espera exponencial ante saturacion
                continue
            r.raise_for_status()
            return r
        raise RuntimeError(f"Sin respuesta valida de {url} tras {intentos} intentos")
