"""Extractor etico (base del Kit de arranque): revisa robots.txt, se identifica y no satura sitios.

Politica de robots.txt (decision documentada en docs/E0/propuesta.md, seccion 5.2):
- Para paginas web (scraping), si robots.txt prohibe la ruta, la peticion NO se hace.
- Para las APIs REST oficiales y documentadas de APIS_DOCUMENTADAS, el robots.txt se sigue
  descargando y guardando como evidencia, pero no bloquea la peticion: sus directivas estan
  dirigidas a rastreadores web (crawlers), no a clientes de una API publicada para acceso
  programatico. Excepcion autorizada por el docente de Ingenieria de Datos el 2026-11-12.
  La pausa minima, el User-Agent con contacto y los reintentos aplican igual.
"""
import os
import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

# Contacto del User-Agent: variable del repositorio TDL_CONTACTO (correo institucional + repo).
CONTACTO = os.environ.get("TDL_CONTACTO", "https://github.com/Ximenaar1/tdl-ximena")
UA = f"TDL-Observatorio/1.0 (proyecto academico TecNM Colima; contacto: {CONTACTO})"

# Dominio -> pagina de terminos de uso de la API documentada.
APIS_DOCUMENTADAS = {
    "archive-api.open-meteo.com": "https://open-meteo.com/en/terms",
    "api.open-meteo.com": "https://open-meteo.com/en/terms",
    "power.larc.nasa.gov": "https://power.larc.nasa.gov/docs/",
}

NOTA_API = "robots.txt Disallow (dirigido a crawlers); API documentada, uso autorizado 2026-11-12"


def leer_robots(sesion, base):
    """Descarga robots.txt con nuestro User-Agent y devuelve un RobotFileParser.
    404 u otro 4xx: no hay reglas (se permite). 5xx o error de red: se prohibe todo (conservador)."""
    rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
    try:
        r = sesion.get(base + "/robots.txt", timeout=30)
        if r.status_code == 200:
            rp.parse(r.text.splitlines())
        elif 400 <= r.status_code < 500:
            rp.parse([])
        else:
            rp.parse(["User-agent: *", "Disallow: /"])
    except requests.RequestException:
        rp.parse(["User-agent: *", "Disallow: /"])
    return rp


class ExtractorEtico:
    def __init__(self, pausa=1.5, sesion=None):
        self.pausa = pausa  # segundos minimos entre peticiones al mismo dominio
        self.robots = {}
        self.ultimo = {}
        self.sesion = sesion or requests.Session()
        self.sesion.headers["User-Agent"] = UA

    def _reglas(self, url):
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self.robots:
            self.robots[base] = leer_robots(self.sesion, base)
        return self.robots[base]

    def get(self, url, intentos=3):
        reglas = self._reglas(url)
        dominio = urlparse(url).netloc
        nota = ""
        if not reglas.can_fetch(UA, url):
            if dominio not in APIS_DOCUMENTADAS:
                raise PermissionError(f"robots.txt no permite {url}")
            nota = NOTA_API
        pausa = max(self.pausa, reglas.crawl_delay(UA) or 0)
        espera = pausa - (time.time() - self.ultimo.get(dominio, 0))
        if espera > 0:
            time.sleep(espera)
        for i in range(intentos):
            r = self.sesion.get(url, timeout=60)
            self.ultimo[dominio] = time.time()
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(pausa * 2 ** i)  # espera exponencial ante saturacion
                continue
            r.raise_for_status()
            r.nota_robots = nota
            return r
        raise RuntimeError(f"Sin respuesta valida de {url} tras {intentos} intentos")
