"""Cliente mínimo do Microsoft Graph com autenticação delegada (device code)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import msal
import requests

GRAPH = "https://graph.microsoft.com/v1.0"
ESCOPOS = [
    "Calendars.ReadWrite",
    "Files.ReadWrite.All",
    "Sites.ReadWrite.All",
    "User.Read",
]


class GraphError(RuntimeError):
    pass


class Graph:
    def __init__(self, client_id: str, tenant_id: str, cache_path: Path):
        self.cache_path = cache_path
        self.cache = msal.SerializableTokenCache()
        if cache_path.exists():
            self.cache.deserialize(cache_path.read_text())
        self.app = msal.PublicClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            token_cache=self.cache,
        )
        self.sessao = requests.Session()

    def _token(self) -> str:
        contas = self.app.get_accounts()
        resultado = self.app.acquire_token_silent(ESCOPOS, account=contas[0]) if contas else None
        if not resultado:
            fluxo = self.app.initiate_device_flow(scopes=ESCOPOS)
            if "user_code" not in fluxo:
                raise GraphError(f"Falha ao iniciar login: {fluxo.get('error_description', fluxo)}")
            print(fluxo["message"])
            resultado = self.app.acquire_token_by_device_flow(fluxo)
        if "access_token" not in resultado:
            raise GraphError(f"Falha no login: {resultado.get('error_description', resultado)}")
        if self.cache.has_state_changed:
            self.cache_path.write_text(self.cache.serialize())
            self.cache_path.chmod(0o600)
        return resultado["access_token"]

    def request(
        self,
        metodo: str,
        caminho: str,
        *,
        json: Any = None,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        url = caminho if caminho.startswith("http") else GRAPH + caminho
        for tentativa in range(5):
            h = {"Authorization": f"Bearer {self._token()}"}
            h.update(headers or {})
            r = self.sessao.request(metodo, url, json=json, params=params, headers=h, timeout=60)
            if r.status_code in (429, 503, 504) and tentativa < 4:
                time.sleep(float(r.headers.get("Retry-After", 2 ** tentativa)))
                continue
            if r.status_code >= 400:
                raise GraphError(f"{metodo} {caminho} -> {r.status_code}: {r.text[:500]}")
            return r.json() if r.content else None
        raise GraphError(f"{metodo} {caminho}: muitas tentativas")

    def get(self, caminho: str, **kw) -> Any:
        return self.request("GET", caminho, **kw)

    def post(self, caminho: str, json: Any = None, **kw) -> Any:
        return self.request("POST", caminho, json=json, **kw)

    def patch(self, caminho: str, json: Any = None, **kw) -> Any:
        return self.request("PATCH", caminho, json=json, **kw)

    def paginar(self, caminho: str, **kw):
        dados = self.get(caminho, **kw)
        while True:
            yield from dados.get("value", [])
            proximo = dados.get("@odata.nextLink")
            if not proximo:
                return
            dados = self.get(proximo, headers=kw.get("headers"))


def q(texto: str) -> str:
    """Escapa um segmento de URL (nomes de abas, caminhos de arquivo)."""
    return quote(texto, safe="")
