"""Inclusão de tarefas na planilha de programação semanal (Excel no SharePoint)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .graph import Graph, q

ABA_RE = re.compile(r"^W\d+\s+(\d{2})(\d{2})(\d{4})$")
EPOCA_EXCEL = date(1899, 12, 30)
FORMATO_DATA = "dd/mm/yyyy"

# Cabeçalhos esperados (comparação sem acento/caixa).
COLUNAS = ("Cliente", "Natureza", "Caso", "Providência", "Prazo LO", "Revisão", "Fatal",
           "Executor", "Revisor", "Prioridade", "Status", "Observações")
COLUNAS_DATA = ("Prazo LO", "Revisão", "Fatal")


def _chave(texto: str) -> str:
    import unicodedata

    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t).strip().casefold()


def data_da_aba(nome: str) -> date | None:
    m = ABA_RE.match(nome.strip())
    if not m:
        return None
    dia, mes, ano = map(int, m.groups())
    try:
        return date(ano, mes, dia)
    except ValueError:
        return None


def escolher_aba(nomes: list[str], hoje: date) -> str | None:
    """Aba da semana corrente.

    Aos sábados e domingos considera a semana seguinte (a programação da
    semana costuma ser montada antes de segunda-feira). Se não houver aba
    para a semana, usa a aba mais recente anterior à data de referência.
    """
    ref = hoje + timedelta(days=7 - hoje.weekday()) if hoje.weekday() >= 5 else hoje
    inicio = ref - timedelta(days=ref.weekday())
    fim = inicio + timedelta(days=6)
    datadas = [(d, n) for n in nomes if (d := data_da_aba(n))]
    na_semana = [x for x in datadas if inicio <= x[0] <= fim]
    if na_semana:
        return min(na_semana)[1]
    anteriores = [x for x in datadas if x[0] <= ref]
    return max(anteriores)[1] if anteriores else None


def para_serial(d: date) -> int:
    return (d - EPOCA_EXCEL).days


def de_serial(valor) -> date | None:
    if isinstance(valor, (int, float)) and not isinstance(valor, bool) and valor > 0:
        return EPOCA_EXCEL + timedelta(days=int(valor))
    if isinstance(valor, str):
        try:
            return datetime.strptime(valor.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None
    return None


def coluna_letra(indice: int) -> str:
    letras = ""
    indice += 1
    while indice:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


@dataclass
class Tarefa:
    cliente: str
    natureza: str
    caso: str
    providencia: str
    lo: date | None
    revisao: date | None
    fatal: date | None
    executor: str
    revisor: str
    prioridade: str = "Alta"
    status: str = ""
    observacoes: str = ""

    def valores(self) -> dict[str, object]:
        return {
            "Cliente": self.cliente,
            "Natureza": self.natureza,
            "Caso": self.caso,
            "Providência": self.providencia,
            "Prazo LO": self.lo,
            "Revisão": self.revisao,
            "Fatal": self.fatal,
            "Executor": self.executor,
            "Revisor": self.revisor,
            "Prioridade": self.prioridade,
            "Status": self.status,
            "Observações": self.observacoes,
        }


def linha_de_insercao(linhas: list[list], idx_lo: int, lo: date | None) -> int:
    """Índice (0-based, contando o cabeçalho) onde inserir para manter a ordem por Prazo LO.

    Linhas sem data (``sine die``/vazias) ficam no fim, como na planilha.
    """
    if lo is None:
        ultimo = max((i for i, l in enumerate(linhas) if any(str(v).strip() for v in l)), default=0)
        return ultimo + 1
    for i, linha in enumerate(linhas[1:], start=1):
        atual = de_serial(linha[idx_lo]) if idx_lo < len(linha) else None
        if atual is None or atual > lo:
            return i
    return len(linhas)


def ajustar_formula(formula: str, linha_origem: int, linha_destino: int) -> str:
    """Troca referências relativas da linha de origem pela de destino (ex.: E7 -> E12)."""
    return re.sub(
        rf"(?<![A-Z$])(\$?[A-Z]{{1,3}}){linha_origem}(?![\d(])",
        lambda m: f"{m.group(1)}{linha_destino}",
        formula,
    )


class Planilha:
    def __init__(self, g: Graph, host: str, site: str, arquivo: str):
        self.g = g
        site_id = g.get(f"/sites/{host}:{site}")["id"]
        item = g.get(f"/sites/{site_id}/drive/root:/{q(arquivo).replace('%2F', '/')}")
        self.base = f"/drives/{item['parentReference']['driveId']}/items/{item['id']}/workbook"
        self.web_url = item.get("webUrl", "")
        self.sessao: str | None = None
        self._cache: dict[str, tuple[list[list], list[list]]] = {}

    def __enter__(self):
        r = self.g.post(f"{self.base}/createSession", {"persistChanges": True})
        self.sessao = r["id"]
        return self

    def __exit__(self, *exc):
        if self.sessao:
            try:
                self.g.post(f"{self.base}/closeSession", headers=self._h())
            finally:
                self.sessao = None

    def _h(self) -> dict:
        return {"workbook-session-id": self.sessao} if self.sessao else {}

    def abas(self) -> list[str]:
        r = self.g.get(f"{self.base}/worksheets", params={"$select": "name"}, headers=self._h())
        return [w["name"] for w in r["value"]]

    def _ws(self, aba: str) -> str:
        return f"{self.base}/worksheets/{q(aba)}"

    def ler(self, aba: str) -> tuple[list[list], list[list]]:
        """Valores e fórmulas da área usada (a partir de A1)."""
        if aba in self._cache:
            return self._cache[aba]
        r = self.g.get(
            f"{self._ws(aba)}/usedRange(valuesOnly=false)",
            params={"$select": "address,values,formulas"},
            headers=self._h(),
        )
        inicio = r["address"].split("!")[-1].split(":")[0]
        if inicio != "A1":
            raise ValueError(f'Aba "{aba}" não começa em A1 (área usada: {r["address"]}).')
        self._cache[aba] = (r["values"], r["formulas"])
        return self._cache[aba]

    def buscar_processo(self, abas: list[str], processo: str) -> dict[str, str] | None:
        """Procura o processo nas abas informadas e devolve Cliente/Natureza/Caso já usados."""
        alvo = re.sub(r"\D", "", processo)
        if len(alvo) < 10:
            return None
        for aba in abas:
            valores, _ = self.ler(aba)
            if not valores:
                continue
            cab = {_chave(c): i for i, c in enumerate(valores[0])}
            for linha in valores[1:]:
                if any(alvo in re.sub(r"\D", "", str(v)) for v in linha):
                    pega = lambda nome: str(linha[cab[_chave(nome)]]).strip() if _chave(nome) in cab else ""
                    return {"Cliente": pega("Cliente"), "Natureza": pega("Natureza"), "Caso": pega("Caso")}
        return None

    def duplicada(self, aba: str, processo: str | None, fatal: date | None) -> bool:
        if not processo or not fatal:
            return False
        alvo = re.sub(r"\D", "", processo)
        valores, _ = self.ler(aba)
        cab = {_chave(c): i for i, c in enumerate(valores[0])}
        i_fatal = cab.get(_chave("Fatal"))
        for linha in valores[1:]:
            if any(alvo in re.sub(r"\D", "", str(v)) for v in linha):
                if i_fatal is not None and de_serial(linha[i_fatal]) == fatal:
                    return True
        return False

    def incluir(self, aba: str, tarefa: Tarefa) -> int:
        """Insere a tarefa na posição ordenada por Prazo LO. Retorna o nº da linha no Excel."""
        self._cache.pop(aba, None)
        valores, formulas = self.ler(aba)
        cabecalho = [str(c) for c in valores[0]]
        cab = {_chave(c): i for i, c in enumerate(cabecalho)}
        faltando = [c for c in ("Cliente", "Prazo LO", "Executor") if _chave(c) not in cab]
        if faltando:
            raise ValueError(f'Aba "{aba}" sem as colunas {faltando}. Cabeçalho: {cabecalho}')

        idx = linha_de_insercao(valores, cab[_chave("Prazo LO")], tarefa.lo)
        linha_excel = idx + 1
        ultima_col = coluna_letra(len(cabecalho) - 1)

        # Linha-modelo para copiar fórmulas de colunas calculadas (ex.: "Vencimento").
        modelo_idx = next((i for i in range(1, len(formulas)) if any(str(f).startswith("=") for f in formulas[i])), None)

        nova_formula, novo_formato = [], []
        dados = {_chave(k): v for k, v in tarefa.valores().items()}
        for j, nome in enumerate(cabecalho):
            k = _chave(nome)
            valor = dados.get(k)
            formato = "General"
            if k in dados:
                if isinstance(valor, date):
                    valor, formato = para_serial(valor), FORMATO_DATA
                elif valor is None:
                    valor = ""
            elif modelo_idx is not None and str(formulas[modelo_idx][j]).startswith("="):
                # Linha do modelo pode deslocar após a inserção.
                origem = modelo_idx + 1
                valor = ajustar_formula(formulas[modelo_idx][j], origem, linha_excel)
            else:
                valor = ""
            nova_formula.append(valor)
            novo_formato.append(formato)

        endereco = f"A{linha_excel}:{ultima_col}{linha_excel}"
        h = self._h()
        self.g.post(f"{self._ws(aba)}/range(address='{endereco}')/insert", {"shift": "Down"}, headers=h)
        self.g.patch(
            f"{self._ws(aba)}/range(address='{endereco}')",
            {"formulas": [nova_formula], "numberFormat": [novo_formato]},
            headers=h,
        )
        self._cache.pop(aba, None)
        return linha_excel
