"""Pruebas de la politica de robots.txt del extractor, con un servidor SIMULADO (sin red)."""
import pytest

from extractores.base import NOTA_API, ExtractorEtico


class Resp:
    def __init__(self, status=200, text=""):
        self.status_code, self.text, self.content = status, text, text.encode()

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class SesionFalsa:
    """robots: dict dominio -> (status, texto). Cualquier otra URL responde 200 con '{}'."""

    def __init__(self, robots):
        self.headers, self.robots, self.pedidas = {}, robots, []

    def get(self, url, timeout=None):
        self.pedidas.append(url)
        for dominio, (status, texto) in self.robots.items():
            if url == f"https://{dominio}/robots.txt":
                return Resp(status, texto)
        return Resp(200, "{}")


PROHIBE_TODO = "User-agent: *\nDisallow: /\n"


def test_sitio_web_prohibido_no_se_consulta():
    s = SesionFalsa({"ejemplo.com": (200, PROHIBE_TODO)})
    ext = ExtractorEtico(pausa=0, sesion=s)
    with pytest.raises(PermissionError):
        ext.get("https://ejemplo.com/pagina")
    assert "https://ejemplo.com/pagina" not in s.pedidas


def test_api_documentada_se_consulta_y_deja_nota():
    s = SesionFalsa({"archive-api.open-meteo.com": (200, PROHIBE_TODO)})
    ext = ExtractorEtico(pausa=0, sesion=s)
    r = ext.get("https://archive-api.open-meteo.com/v1/archive?latitude=19.2")
    assert r.nota_robots == NOTA_API
    assert s.headers["User-Agent"].startswith("TDL-Observatorio/1.0")


def test_sin_robots_404_se_permite_sin_nota():
    s = SesionFalsa({"ejemplo.com": (404, "")})
    r = ExtractorEtico(pausa=0, sesion=s).get("https://ejemplo.com/datos")
    assert r.nota_robots == ""


def test_robots_con_error_5xx_bloquea_por_precaucion():
    s = SesionFalsa({"ejemplo.com": (503, "")})
    with pytest.raises(PermissionError):
        ExtractorEtico(pausa=0, sesion=s).get("https://ejemplo.com/datos")


def test_contacto_con_salto_de_linea_se_limpia():
    from extractores.base import CONTACTO_DEFECTO, limpiar_contacto
    assert limpiar_contacto(" correo@colima.tecnm.mx;\n https://github.com/x/y \n") == \
        "correo@colima.tecnm.mx; https://github.com/x/y"
    assert limpiar_contacto("") == CONTACTO_DEFECTO
