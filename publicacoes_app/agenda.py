"""Criação dos compromissos no calendário do Outlook."""

from __future__ import annotations

import html
from datetime import date, timedelta

from .graph import Graph
from .planilha import Tarefa

FUSO = "E. South America Standard Time"  # Brasília (Windows time zone id)

ROTULOS = {"lo": "Prazo LO", "revisao": "Revisão", "fatal": "FATAL"}


def corpo_evento(tarefa: Tarefa, processo: str | None, ato: str, link_email: str) -> str:
    linhas = [
        ("Cliente", tarefa.cliente),
        ("Caso", tarefa.caso),
        ("Processo", processo or ""),
        ("Providência", tarefa.providencia),
        ("Publicação", ato),
        ("Executor", tarefa.executor),
        ("Revisor", tarefa.revisor),
        ("Prazo LO", f"{tarefa.lo:%d/%m/%Y}" if tarefa.lo else "sine die"),
        ("Revisão", f"{tarefa.revisao:%d/%m/%Y}" if tarefa.revisao else ""),
        ("Fatal", f"{tarefa.fatal:%d/%m/%Y}" if tarefa.fatal else ""),
        ("Observações", tarefa.observacoes),
    ]
    itens = "".join(f"<b>{html.escape(k)}:</b> {html.escape(v)}<br>" for k, v in linhas if v)
    if link_email:
        itens += f'<br><a href="{html.escape(link_email)}">Abrir e-mail da publicação</a>'
    return itens


def criar_eventos(
    g: Graph,
    tarefa: Tarefa,
    processo: str | None,
    ato: str,
    link_email: str,
    tipos: list[str],
    convidados: list[str],
    lembrete_minutos: int,
    categoria: str,
) -> list[str]:
    """Cria um compromisso de dia inteiro para cada tipo de data. Retorna os links."""
    datas = {"lo": tarefa.lo, "revisao": tarefa.revisao, "fatal": tarefa.fatal}
    corpo = corpo_evento(tarefa, processo, ato, link_email)
    links = []
    criados: set[date] = set()
    for tipo in tipos:
        dia = datas.get(tipo)
        if not dia or dia in criados:
            continue
        criados.add(dia)
        titulo = f"[{ROTULOS[tipo]}] {tarefa.cliente} - {tarefa.providencia}"
        if processo:
            titulo += f" ({processo})"
        evento = {
            "subject": titulo[:255],
            "body": {"contentType": "HTML", "content": corpo},
            "start": {"dateTime": f"{dia:%Y-%m-%d}T00:00:00", "timeZone": FUSO},
            "end": {"dateTime": f"{dia + timedelta(days=1):%Y-%m-%d}T00:00:00", "timeZone": FUSO},
            "isAllDay": True,
            "showAs": "free",
            "isReminderOn": True,
            "reminderMinutesBeforeStart": lembrete_minutos,
            "importance": "high" if tipo == "fatal" else "normal",
            "attendees": [
                {"emailAddress": {"address": e}, "type": "required"} for e in convidados if e
            ],
        }
        if categoria:
            evento["categories"] = [categoria]
        criado = g.post("/me/events", evento)
        links.append(criado.get("webLink", ""))
    return links
