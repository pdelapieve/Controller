"""Leitura do arquivo de configuração (TOML)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class Config:
    client_id: str
    tenant_id: str
    lo_pasta: str = r"C:\Users\Betina\Downloads"
    lo_padrao: str = "Tarefas_Pendentes_LegalOne_*.xlsx"
    d_menos: int = 2
    ignorar_vencidas_ha_dias: int = 7
    atrib_pasta: str = r"C:\Users\Betina\Downloads"
    atrib_modelo: str = ""
    atrib_autor: str = "PEDRO"
    sp_host: str = ""
    sp_site: str = ""
    sp_arquivo: str = ""
    uf: str = ""
    antecedencia_lo: int = 3
    antecedencia_revisao: int = 1
    feriados_extras: list[date] = field(default_factory=list)
    eventos: list[str] = field(default_factory=lambda: ["lo", "fatal"])
    convidar_equipe: bool = False
    lembrete_minutos: int = 1080
    categoria_agenda: str = "Prazos"
    equipe: dict[str, str] = field(default_factory=dict)
    base_dir: Path = Path(".")

    @property
    def token_cache(self) -> Path:
        return self.base_dir / ".token_cache.json"

    @property
    def arquivo_estado(self) -> Path:
        return self.base_dir / ".estado.json"


def carregar(caminho: str | Path) -> Config:
    caminho = Path(caminho)
    with caminho.open("rb") as f:
        raw = tomllib.load(f)

    ms = raw.get("microsoft", {})
    lo = raw.get("legalone", {})
    at = raw.get("atribuicoes", {})
    pl = raw.get("planilha", {})
    pz = raw.get("prazos", {})
    ag = raw.get("agenda", {})

    eventos = [e.lower() for e in ag.get("eventos", ["lo", "fatal"])]
    invalidos = set(eventos) - {"lo", "revisao", "fatal"}
    if invalidos:
        raise ValueError(f"agenda.eventos inválidos: {sorted(invalidos)}")

    return Config(
        client_id=ms["client_id"],
        tenant_id=ms["tenant_id"],
        lo_pasta=lo.get("pasta", Config.lo_pasta),
        lo_padrao=lo.get("padrao", Config.lo_padrao),
        d_menos=int(lo.get("d_menos", 2)),
        ignorar_vencidas_ha_dias=int(lo.get("ignorar_vencidas_ha_dias", 7)),
        atrib_pasta=at.get("pasta", lo.get("pasta", Config.atrib_pasta)),
        atrib_modelo=at.get("modelo_texto", ""),
        atrib_autor=at.get("autor", "PEDRO"),
        sp_host=pl["host"],
        sp_site=pl["site"],
        sp_arquivo=pl["arquivo"],
        uf=pz.get("uf", ""),
        antecedencia_lo=int(pz.get("antecedencia_lo", 3)),
        antecedencia_revisao=int(pz.get("antecedencia_revisao", 1)),
        feriados_extras=[date.fromisoformat(d) for d in pz.get("feriados_extras", [])],
        eventos=eventos,
        convidar_equipe=bool(ag.get("convidar_equipe", False)),
        lembrete_minutos=int(ag.get("lembrete_minutos", 1080)),
        categoria_agenda=ag.get("categoria", "Prazos"),
        equipe=dict(raw.get("equipe", {})),
        base_dir=caminho.resolve().parent,
    )
