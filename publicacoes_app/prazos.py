"""Contagem de prazos processuais em dias úteis (CPC, arts. 219, 220 e 224).

O cálculo é uma estimativa: o app sempre mostra as datas para confirmação
antes de agendar. Feriados municipais e suspensões pontuais (indisponibilidade
de sistema, portarias do tribunal) devem ser informados em
``prazos.feriados_extras`` no config.toml ou ajustados manualmente.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache

import holidays

CNJ_RE = re.compile(r"\b(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})\b")

# Segmento do Judiciário no número CNJ (campo "J").
SEGMENTOS = {
    "1": "STF",
    "2": "CNJ",
    "3": "STJ",
    "4": "Justiça Federal",
    "5": "Justiça do Trabalho",
    "6": "Justiça Eleitoral",
    "7": "Justiça Militar da União",
    "8": "Justiça Estadual",
    "9": "Justiça Militar Estadual",
}


def normalizar_cnj(texto: str) -> str | None:
    """Retorna o número CNJ formatado (NNNNNNN-DD.AAAA.J.TR.OOOO), se houver."""
    m = CNJ_RE.search(texto or "")
    if not m:
        return None
    n, dv, ano, j, tr, orig = m.groups()
    return f"{n}-{dv}.{ano}.{j}.{tr}.{orig}"


def segmento(cnj: str | None) -> str | None:
    if not cnj:
        return None
    partes = cnj.split(".")
    return partes[2] if len(partes) >= 3 else None


class CalendarioForense:
    """Dias úteis forenses: sem fins de semana, feriados e recesso (20/12–20/01)."""

    def __init__(self, uf: str = "", extras: list[date] | None = None, federal: bool = False):
        self.uf = uf or None
        self.extras = set(extras or [])
        self.federal = federal

    @lru_cache(maxsize=None)
    def _feriados(self, ano: int) -> frozenset[date]:
        dias = set(holidays.Brazil(years=ano, subdiv=self.uf).keys())
        pascoa = _pascoa(ano)
        # Carnaval (segunda e terça) e Corpus Christi: sem expediente forense.
        dias |= {pascoa - timedelta(days=48), pascoa - timedelta(days=47), pascoa + timedelta(days=60)}
        if self.federal:
            # Lei 5.010/66, art. 62: feriados da Justiça Federal.
            dias |= {
                pascoa - timedelta(days=4),  # quarta-feira santa
                pascoa - timedelta(days=3),  # quinta-feira santa
                date(ano, 8, 11),
                date(ano, 11, 1),
                date(ano, 12, 8),
            }
        return frozenset(dias)

    def eh_util(self, d: date) -> bool:
        if d.weekday() >= 5:
            return False
        if d in self.extras or d in self._feriados(d.year):
            return False
        # Recesso forense: prazos suspensos de 20/12 a 20/01 (CPC, art. 220).
        if (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20):
            return False
        return True

    def proximo_util(self, d: date, incluir: bool = False) -> date:
        """Primeiro dia útil após ``d`` (ou o próprio ``d``, se ``incluir``)."""
        if not incluir:
            d += timedelta(days=1)
        while not self.eh_util(d):
            d += timedelta(days=1)
        return d

    def somar_uteis(self, d: date, n: int) -> date:
        """Avança (n > 0) ou recua (n < 0) ``n`` dias úteis a partir de ``d``."""
        passo = 1 if n >= 0 else -1
        restantes = abs(n)
        while restantes:
            d += timedelta(days=passo)
            if self.eh_util(d):
                restantes -= 1
        return d

    def anterior_util(self, d: date) -> date:
        while not self.eh_util(d):
            d -= timedelta(days=1)
        return d


def calendario_para(cnj: str | None, uf: str, extras: list[date]) -> CalendarioForense:
    return CalendarioForense(uf=uf, extras=extras, federal=segmento(cnj) == "4")


# Marcos possíveis a partir dos quais o prazo é contado.
MARCOS = ("inicio_contagem", "publicacao", "disponibilizacao", "intimacao")


@dataclass
class Datas:
    fatal: date
    revisao: date
    lo: date


def calcular_fatal(
    cal: CalendarioForense,
    marco: str,
    data_marco: date,
    dias: int,
    uteis: bool = True,
) -> date:
    """Calcula o último dia do prazo.

    - ``disponibilizacao``: publicação = 1º dia útil seguinte (Lei 11.419/06,
      art. 4º, §3º); a contagem começa no 1º dia útil após a publicação.
    - ``publicacao`` / ``intimacao``: exclui o dia do começo (CPC, art. 224).
    - ``inicio_contagem``: a data informada já é o 1º dia do prazo (eproc).
    """
    if dias < 1:
        raise ValueError("prazo em dias deve ser positivo")
    if marco == "disponibilizacao":
        data_marco = cal.proximo_util(data_marco)
        marco = "publicacao"
    if marco in ("publicacao", "intimacao"):
        inicio = cal.proximo_util(data_marco)
    elif marco == "inicio_contagem":
        inicio = cal.proximo_util(data_marco, incluir=True)
    else:
        raise ValueError(f"marco desconhecido: {marco}")

    if uteis:
        return cal.somar_uteis(inicio, dias - 1)
    # Prazo em dias corridos: se terminar em dia não útil, prorroga (art. 224, §1º).
    return cal.proximo_util(inicio + timedelta(days=dias - 1), incluir=True)


def datas_internas(
    cal: CalendarioForense,
    fatal: date,
    antecedencia_lo: int,
    antecedencia_revisao: int,
    hoje: date | None = None,
) -> Datas:
    """Sugere datas de Prazo LO (executor) e Revisão a partir do fatal.

    Com ``hoje``, as sugestões nunca ficam no passado (prazos já curtos).
    """
    lo = cal.somar_uteis(fatal, -antecedencia_lo) if antecedencia_lo else fatal
    revisao = cal.somar_uteis(fatal, -antecedencia_revisao) if antecedencia_revisao else fatal
    if hoje:
        piso = min(cal.proximo_util(hoje, incluir=True), fatal)
        lo, revisao = max(lo, piso), max(revisao, piso)
    if revisao < lo:
        revisao = lo
    return Datas(fatal=fatal, revisao=revisao, lo=lo)


def _pascoa(ano: int) -> date:
    """Domingo de Páscoa (algoritmo de Meeus/Jones/Butcher)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)
