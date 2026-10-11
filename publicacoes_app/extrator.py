"""Identificação dos prazos contidos em um e-mail de publicação.

Usa o Claude (API da Anthropic) quando ``ANTHROPIC_API_KEY`` está definida;
caso contrário, recorre a um extrator simples por expressões regulares.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime

from .prazos import MARCOS, normalizar_cnj


@dataclass
class PrazoIdentificado:
    processo: str | None
    orgao: str = ""
    partes: str = ""
    cliente: str = ""
    ato: str = ""
    providencia: str = ""
    prazo_dias: int | None = None
    uteis: bool = True
    marco: str = "publicacao"
    data_marco: date | None = None
    fatal_informado: date | None = None
    prazo_inferido: bool = False
    observacao: str = ""
    avisos: list[str] = field(default_factory=list)


SISTEMA = """\
Você é assistente da controladoria de um escritório de advocacia tributária \
brasileiro. Recebe o texto de um e-mail da pasta "Publicações" (boletins de \
publicações do WebJur/DJEN, notificações do Legal One/Datacloud com \
movimentações do eproc, ou mensagens da controladoria) e deve listar cada \
publicação/intimação que abre prazo para o escritório.

Regras:
- Uma entrada por processo/intimação que exija providência. Boletins sem \
publicações ("Total de publicações: 0") e respostas que só confirmam \
agendamento ("Prazo agendado", "Prazo já agendado") não geram entradas.
- processo: número no padrão CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO) ou número do \
processo administrativo, exatamente como aparece.
- marco e data_marco: a data a partir da qual o prazo corre.
  * "inicio_contagem": o texto informa a data inicial da contagem (ex.: eproc \
"Data inicial da contagem do prazo: 07/10/2026"). Essa data é o 1º dia do prazo.
  * "publicacao": há "Data de Publicação" (DJEN/WebJur). Prefira esta.
  * "disponibilizacao": só há data de disponibilização no diário.
  * "intimacao": intimação eletrônica com data de ciência/leitura.
- prazo_dias: o prazo em dias se o texto o informar (ex.: "Prazo: 5 dias"). \
Se não informar, deduza o prazo legal da providência cabível (ex.: embargos \
de declaração 5 dias; apelação, contrarrazões, agravo de instrumento, \
contestação, recurso especial/extraordinário 15 dias; manifestação sem prazo \
fixado 5 dias - CPC art. 218, §3º) e marque prazo_inferido = true. Não aplique \
prazo em dobro ao escritório (o dobro é da Fazenda Pública, MP e Defensoria). \
Se não houver como estimar, use null.
- uteis: false apenas para prazos em dias corridos (ex.: prazos penais, \
alguns administrativos).
- fatal_informado: preencha só se o texto trouxer a data final do prazo.
- providencia: a peça/ato a praticar, curta (ex.: "Contrarrazões aos Embargos \
de Declaração", "Manifestação sobre RPV expedida").
- ato: resumo do conteúdo publicado (1 frase).
- cliente: a parte representada pelo escritório, se identificável.
- observacao: dúvidas relevantes para quem vai conferir (curta, ou "").
- Datas no formato AAAA-MM-DD."""

_NULO_STR = {"anyOf": [{"type": "string"}, {"type": "null"}]}
_NULO_INT = {"anyOf": [{"type": "integer"}, {"type": "null"}]}

ESQUEMA = {
    "type": "object",
    "properties": {
        "prazos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "processo": _NULO_STR,
                    "orgao": {"type": "string"},
                    "partes": {"type": "string"},
                    "cliente": {"type": "string"},
                    "ato": {"type": "string"},
                    "providencia": {"type": "string"},
                    "prazo_dias": _NULO_INT,
                    "prazo_inferido": {"type": "boolean"},
                    "uteis": {"type": "boolean"},
                    "marco": {"type": "string", "enum": list(MARCOS)},
                    "data_marco": _NULO_STR,
                    "fatal_informado": _NULO_STR,
                    "observacao": {"type": "string"},
                },
                "required": [
                    "processo", "orgao", "partes", "cliente", "ato", "providencia",
                    "prazo_dias", "prazo_inferido", "uteis", "marco", "data_marco",
                    "fatal_informado", "observacao",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["prazos"],
    "additionalProperties": False,
}


def _data(valor: str | None) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(valor[:10])
    except ValueError:
        return None


def _de_dict(d: dict) -> PrazoIdentificado:
    processo = d.get("processo")
    return PrazoIdentificado(
        processo=normalizar_cnj(processo or "") or processo,
        orgao=d.get("orgao", ""),
        partes=d.get("partes", ""),
        cliente=d.get("cliente", ""),
        ato=d.get("ato", ""),
        providencia=d.get("providencia", ""),
        prazo_dias=d.get("prazo_dias"),
        uteis=d.get("uteis", True),
        marco=d.get("marco") if d.get("marco") in MARCOS else "publicacao",
        data_marco=_data(d.get("data_marco")),
        fatal_informado=_data(d.get("fatal_informado")),
        prazo_inferido=bool(d.get("prazo_inferido")),
        observacao=d.get("observacao", ""),
    )


class ExtratorClaude:
    def __init__(self, modelo: str):
        import anthropic

        self.anthropic = anthropic
        self.cliente = anthropic.Anthropic()
        self.modelo = modelo

    def extrair(self, assunto: str, texto: str, recebido: datetime) -> list[PrazoIdentificado]:
        conteudo = (
            f"Data de recebimento do e-mail: {recebido:%Y-%m-%d}\n"
            f"Assunto: {assunto}\n\n{texto}"
        )
        kwargs = dict(
            model=self.modelo,
            max_tokens=16000,
            system=SISTEMA,
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": ESQUEMA}},
            messages=[{"role": "user", "content": conteudo}],
        )
        if self.modelo.startswith(("claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5")):
            resposta = self.cliente.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
            )
        else:
            resposta = self.cliente.messages.create(**kwargs)

        if resposta.stop_reason == "refusal":
            raise RuntimeError("o modelo recusou a solicitação")
        if resposta.stop_reason == "max_tokens":
            raise RuntimeError("resposta truncada (max_tokens)")
        texto_json = next(b.text for b in resposta.content if b.type == "text")
        return [_de_dict(d) for d in json.loads(texto_json)["prazos"]]


_DATA_BR = r"(\d{2}/\d{2}/\d{4})"


def _br(valor: str) -> date:
    return datetime.strptime(valor, "%d/%m/%Y").date()


class ExtratorRegex:
    """Extração simples, sem IA: identifica processo, prazo em dias e datas-marco."""

    def extrair(self, assunto: str, texto: str, recebido: datetime) -> list[PrazoIdentificado]:
        if re.search(r"(?i)prazo (j[aá] )?agendado", texto[:400]) and not re.search(r"(?i)prazo:\s*\d+", texto):
            return []
        # Divide boletins do WebJur por publicação; demais e-mails são um bloco só.
        cabecalho = r"(?<!de )Publica[çc][ãa]o:\s*\d+(?![\d/])"
        blocos = re.split(f"(?={cabecalho})", texto)
        blocos = [b for b in blocos if re.match(cabecalho, b)] or [assunto + "\n" + texto]

        resultado = []
        vistos = set()
        for bloco in blocos:
            processo = normalizar_cnj(bloco) or normalizar_cnj(assunto)
            if not processo or processo in vistos:
                continue
            vistos.add(processo)
            p = PrazoIdentificado(processo=processo)
            if m := re.search(r"(?i)prazo:\s*(\d+)\s*dias", bloco):
                p.prazo_dias = int(m.group(1))
            else:
                p.prazo_dias = 15
                p.prazo_inferido = True
                p.avisos.append("Prazo não informado no texto; sugerido 15 dias úteis - confira.")
            if m := re.search(r"(?i)data inicial da contagem do prazo:\s*" + _DATA_BR, bloco):
                p.marco, p.data_marco = "inicio_contagem", _br(m.group(1))
            elif m := re.search(r"(?i)data de publica[çc][ãa]o:\s*" + _DATA_BR, bloco):
                p.marco, p.data_marco = "publicacao", _br(m.group(1))
            elif m := re.search(r"(?i)data de disponibiliza[çc][ãa]o:\s*" + _DATA_BR, bloco):
                p.marco, p.data_marco = "disponibilizacao", _br(m.group(1))
            else:
                p.marco, p.data_marco = "publicacao", recebido.date()
                p.avisos.append("Data da publicação não localizada; usada a data do e-mail.")
            if m := re.search(r"(?i)local:\s*(.+)", bloco):
                p.orgao = m.group(1).strip()[:150]
            if m := re.search(r"(?i)(ato ordinat[óo]rio|despacho|decis[ãa]o|senten[çc]a|ac[óo]rd[ãa]o)", bloco):
                p.ato = m.group(1).capitalize()
            resultado.append(p)
        return resultado


def criar_extrator(modelo: str):
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return ExtratorClaude(modelo)
    return ExtratorRegex()
