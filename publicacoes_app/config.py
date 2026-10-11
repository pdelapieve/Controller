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
    pasta: str = "Publicações"
    dias_retroativos: int = 3
    remetentes: list[str] = field(default_factory=list)
    categoria_processado: str = ""
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
    modelo: str = "claude-opus-5-5"
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
    em = raw.get("email", {})
    pl = raw.get("planilha", {})
    pz = raw.get("prazos", {})
    ag = raw.get("agenda", {})
    ia = raw.get("ia", {})

    eventos = [e.lower() for e in ag.get("eventos", ["lo", "fatal"])]
    invalidos = set(eventos) - {"lo", "revisao", "fatal"}
    if invalidos:
        raise ValueError(f"agenda.eventos inválidos: {sorted(invalidos)}")

    return Config(
        client_id=ms["client_id"],
        tenant_id=ms["tenant_id"],
        pasta=em.get("pasta", "Publicações"),
        dias_retroativos=int(em.get("dias_retroativos", 3)),
        remetentes=[r.lower() for r in em.get("remetentes", [])],
        categoria_processado=em.get("categoria_processado", ""),
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
        modelo=ia.get("modelo", "claude-opus-5-5"),
        equipe=dict(raw.get("equipe", {})),
        base_dir=caminho.resolve().parent,
    )
