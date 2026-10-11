"""Leitura da pasta de publicações no Outlook."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .graph import Graph, GraphError


@dataclass
class Email:
    id: str
    assunto: str
    remetente: str
    recebido: datetime
    texto: str
    categorias: list[str]
    link: str


def html_para_texto(conteudo: str) -> str:
    texto = re.sub(r"(?is)<(script|style).*?</\1>", " ", conteudo)
    texto = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", texto)
    texto = re.sub(r"(?i)</t[dh]>", "\t", texto)
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = html.unescape(texto).replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n\s*\n+", "\n\n", texto)
    return texto.strip()


def localizar_pasta(g: Graph, nome: str) -> str:
    """Busca a pasta pelo nome em toda a árvore da caixa de correio."""
    alvo = nome.casefold()
    fila = ["/me/mailFolders"]
    while fila:
        caminho = fila.pop(0)
        for p in g.paginar(caminho, params={"$top": 100, "$select": "id,displayName,childFolderCount"}):
            if p["displayName"].casefold() == alvo:
                return p["id"]
            if p.get("childFolderCount"):
                fila.append(f"/me/mailFolders/{p['id']}/childFolders")
    raise GraphError(f'Pasta "{nome}" não encontrada no Outlook.')


def listar(g: Graph, pasta_id: str, desde: datetime, remetentes: list[str]) -> list[Email]:
    params = {
        "$filter": f"receivedDateTime ge {desde.astimezone(timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
        "$orderby": "receivedDateTime asc",
        "$select": "id,subject,from,receivedDateTime,body,categories,webLink",
        "$top": 50,
    }
    headers = {"Prefer": 'outlook.body-content-type="html"'}
    emails = []
    for m in g.paginar(f"/me/mailFolders/{pasta_id}/messages", params=params, headers=headers):
        remetente = (m.get("from") or {}).get("emailAddress", {}).get("address", "").lower()
        if remetentes and remetente not in remetentes:
            continue
        corpo = m.get("body") or {}
        texto = corpo.get("content", "")
        if corpo.get("contentType") == "html":
            texto = html_para_texto(texto)
        emails.append(
            Email(
                id=m["id"],
                assunto=m.get("subject") or "",
                remetente=remetente,
                recebido=datetime.fromisoformat(m["receivedDateTime"].replace("Z", "+00:00")),
                texto=texto,
                categorias=m.get("categories") or [],
                link=m.get("webLink", ""),
            )
        )
    return emails


def janela_inicial(dias: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=dias)


def marcar_processado(g: Graph, email: Email, categoria: str) -> None:
    if not categoria or categoria in email.categorias:
        return
    g.patch(f"/me/messages/{email.id}", {"categories": [*email.categorias, categoria]})
    email.categorias.append(categoria)
