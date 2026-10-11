"""Fluxo interativo: tarefas do L.O. -> executor/revisor -> Outlook + Programação + atribuições."""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from datetime import date, datetime, timedelta
from pathlib import Path

from . import atribuicoes
from . import config as cfgmod
from .agenda import criar_eventos
from .graph import Graph
from .legalone import Demanda, agrupar, ler_tarefas, localizar_arquivo
from .planilha import Planilha, Tarefa, data_da_aba, escolher_aba
from .prazos import CalendarioForense, calendario_para, datas_internas

PRIORIDADES = ("Alta", "Média", "Baixa", "Acompanhamento")


def hoje() -> date:
    return date.today()


# ---------------------------------------------------------------- entrada

def perguntar(texto: str, padrao: str = "") -> str:
    sufixo = f" [{padrao}]" if padrao else ""
    try:
        resposta = input(f"{texto}{sufixo}: ").strip()
    except EOFError:
        raise SystemExit("\nEncerrado.")
    return resposta or padrao


def perguntar_data(texto: str, padrao: date | None, obrigatoria: bool = False) -> date | None:
    while True:
        valor = perguntar(texto + " (DD/MM/AAAA, '-' p/ vazio)", f"{padrao:%d/%m/%Y}" if padrao else "")
        if valor in ("", "-"):
            if obrigatoria:
                print("  Informe uma data.")
                continue
            return None
        try:
            return datetime.strptime(valor, "%d/%m/%Y").date()
        except ValueError:
            print("  Data inválida.")


def escolher_pessoa(papel: str, equipe: list[str], padrao: str = "", opcional: bool = False) -> str:
    opcoes = "  ".join(f"{i}) {n}" for i, n in enumerate(equipe, 1))
    print(f"  {opcoes}" + ("   (Enter = ninguém)" if opcional and not padrao else ""))
    while True:
        valor = perguntar(f"{papel}", padrao)
        if valor.isdigit() and 1 <= int(valor) <= len(equipe):
            return equipe[int(valor) - 1]
        if valor or opcional:
            return valor
        print(f"  Informe o {papel.lower()}.")


def sim(texto: str, padrao: bool = True) -> bool:
    valor = perguntar(texto + (" (S/n)" if padrao else " (s/N)")).lower()
    return padrao if not valor else valor.startswith("s")


# ---------------------------------------------------------------- estado

class Estado:
    """IDs de tarefas do L.O. já tratadas (atribuídas ou ignoradas)."""

    def __init__(self, caminho: Path):
        self.caminho = caminho
        self.dados = json.loads(caminho.read_text()) if caminho.exists() else {}
        self.dados.setdefault("tarefas_lo", {})

    def tratada(self, d: Demanda) -> bool:
        return all(i in self.dados["tarefas_lo"] for i in d.ids)

    def marcar(self, d: Demanda, acao: str) -> None:
        agora = datetime.now().isoformat(timespec="seconds")
        for i in d.ids:
            self.dados["tarefas_lo"][i] = {"em": agora, "acao": acao, "processo": d.principal.processo or ""}
        self.caminho.write_text(json.dumps(self.dados, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- fluxo

def _d(x: date | None) -> str:
    return f"{x:%d/%m/%Y}" if x else "-"


def mostrar_demanda(n: int, total: int, d: Demanda, ja_consta: bool) -> None:
    p = d.principal
    print(f"\n── {n}/{total} " + "─" * 66)
    campos = [
        ("Cliente", p.cliente),
        ("Processo", p.processo or ""),
        ("Pasta L.O.", p.pasta),
        ("Tarefa", p.descricao),
        ("Tipo", p.tipo),
    ]
    if d.executor:
        campos.append(("Tarefa executor", f"{_d(d.executor.vencimento)} - resp. atual: {d.executor.responsavel or '-'} (ID {d.executor.id})"))
    if d.revisor:
        campos.append(("Tarefa revisor", f"{_d(d.revisor.vencimento)} - resp. atual: {d.revisor.responsavel or '-'} (ID {d.revisor.id})"))
    campos.append(("Fatal (D+2)", f"{_d(d.fatal)} ({['seg','ter','qua','qui','sex','sáb','dom'][d.fatal.weekday()]})"))
    for k, v in campos:
        if v:
            print(textwrap.fill(str(v), 100, initial_indent=f"  {k:<16}", subsequent_indent=" " * 18))
    for a in d.avisos:
        print(f"  ⚠ {a}")
    if ja_consta:
        print("  ⚠ Este processo já está na aba da semana com o mesmo fatal.")


def montar_tarefa(d: Demanda, cfg, cal: CalendarioForense, existente: dict | None) -> Tarefa | None:
    equipe = list(cfg.equipe)
    print()
    executor = escolher_pessoa("Executor", equipe)
    revisor = escolher_pessoa("Revisor", equipe, opcional=True)

    fatal = perguntar_data("Fatal", d.fatal)
    sug = datas_internas(cal, fatal, cfg.antecedencia_lo, cfg.antecedencia_revisao, hoje()) if fatal else None
    lo = perguntar_data("Prazo LO (executor)", d.lo or (sug.lo if sug else None))
    revisao = perguntar_data("Revisão", d.revisao or (sug.revisao if sug else None)) if revisor else None

    p = d.principal
    existente = existente or {}
    if existente:
        print(f"  (Processo já consta na Programação: {existente.get('Cliente')} / {existente.get('Caso')})")
    cliente = perguntar("Cliente", existente.get("Cliente") or p.cliente)
    natureza = perguntar("Natureza", existente.get("Natureza") or "Contencioso")
    caso = perguntar("Caso", existente.get("Caso") or (p.processo or p.pasta))
    providencia = perguntar("Providência", (d.executor or p).descricao[:150])
    prioridade = perguntar(f"Prioridade ({'/'.join(PRIORIDADES)})", "Alta")
    observacoes = perguntar("Observações", "")

    tarefa = Tarefa(cliente, natureza, caso, providencia, lo, revisao, fatal, executor, revisor, prioridade,
                    observacoes=observacoes)
    print("\n  Resumo: " + " | ".join(
        f"{k}: {v:%d/%m/%Y}" if isinstance(v, date) else f"{k}: {v}"
        for k, v in tarefa.valores().items() if v))
    return tarefa if sim("  Confirmar?") else None


def registrar_atribuicao(caminho: str, d: Demanda, t: Tarefa, modelo: str, autor: str) -> None:
    a = atribuicoes.Atribuicao(
        cliente=t.cliente,
        processo=d.principal.processo or "",
        pasta=d.principal.pasta,
        providencia=t.providencia,
        executor=t.executor,
        lo=t.lo,
        revisor=t.revisor,
        revisao=t.revisao,
        fatal=t.fatal,
        id_executor=d.executor.id if d.executor else "",
        responsavel_executor=d.executor.responsavel if d.executor else "",
        id_revisor=d.revisor.id if d.revisor else "",
        responsavel_revisor=d.revisor.responsavel if d.revisor else "",
    )
    while True:
        try:
            atribuicoes.registrar(caminho, a, modelo or atribuicoes.MODELO_PADRAO, autor)
            return
        except PermissionError:
            if not sim(f"  ⚠ Não consegui gravar {caminho} (aberto no Excel?). Feche o arquivo e tente de novo"):
                print("  ⚠ Atribuição NÃO registrada na planilha do dia - anote manualmente.")
                return


def processar_demanda(n: int, total: int, d: Demanda, cfg, g, plan, aba: str, abas_busca: list[str],
                      estado: Estado, caminho_atrib: str, simular: bool) -> str:
    """Retorna 'atribuida', 'ignorada' ou 'adiada'."""
    p = d.principal
    ja_consta = plan.duplicada(aba, p.processo, d.fatal)
    mostrar_demanda(n, total, d, ja_consta)
    acao = perguntar("  [A]tribuir, [I]gnorar, [D]epois", "I" if ja_consta else "A").lower()[:1]
    if acao == "d":
        return "adiada"
    if acao == "i":
        if not simular:
            estado.marcar(d, "ignorada")
        return "ignorada"

    cal = calendario_para(p.processo, cfg.uf, cfg.feriados_extras)
    existente = plan.buscar_processo(abas_busca, p.processo) if p.processo else None
    tarefa = montar_tarefa(d, cfg, cal, existente)
    if not tarefa:
        return "adiada"
    if simular:
        print(f'  (simulação) Seria incluída na aba "{aba}", agendada no Outlook e registrada em {caminho_atrib}.')
        return "atribuida"

    linha = plan.incluir(aba, tarefa)
    print(f'  ✔ Programação: aba "{aba}", linha {linha}.')
    convidados = [cfg.equipe.get(x, "") for x in (tarefa.executor, tarefa.revisor) if x] if cfg.convidar_equipe else []
    links = criar_eventos(g, tarefa, p.processo, "Legal One", cfg.eventos, convidados,
                          cfg.lembrete_minutos, cfg.categoria_agenda)
    print(f"  ✔ Outlook: {len(links)} compromisso(s).")
    registrar_atribuicao(caminho_atrib, d, tarefa, cfg.atrib_modelo, cfg.atrib_autor)
    print("  ✔ Atribuição registrada para o andamento no L.O.")
    estado.marcar(d, "atribuida")
    return "atribuida"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="publicacoes_app", description=__doc__)
    ap.add_argument("-c", "--config", default="config.toml")
    ap.add_argument("--arquivo", help="planilha do L.O. (padrão: a mais recente na pasta configurada)")
    ap.add_argument("--aba", help="aba da Programação (padrão: semana corrente)")
    ap.add_argument("--todas", action="store_true", help="inclui tarefas já tratadas e vencidas há mais tempo")
    ap.add_argument("--simular", action="store_true", help="não grava nada (Programação, Outlook, atribuições, estado)")
    args = ap.parse_args(argv)

    if not Path(args.config).exists():
        print(f"Arquivo {args.config} não encontrado. Copie config.example.toml para config.toml e ajuste.")
        return 1
    cfg = cfgmod.carregar(args.config)
    if not cfg.equipe:
        print("Cadastre a equipe na seção [equipe] do config.toml.")
        return 1

    arquivo = args.arquivo or localizar_arquivo(cfg.lo_pasta, cfg.lo_padrao)
    if not arquivo or not os.path.exists(arquivo):
        print(f'Planilha do L.O. não encontrada em "{cfg.lo_pasta}" ({cfg.lo_padrao}).')
        return 1
    gerado = datetime.fromtimestamp(os.path.getmtime(arquivo))
    print(f"Planilha do L.O.: {arquivo} (gerada em {gerado:%d/%m/%Y %H:%M})")

    cal = CalendarioForense(uf=cfg.uf, extras=cfg.feriados_extras)
    demandas = agrupar(ler_tarefas(arquivo), cal, cfg.d_menos)
    estado = Estado(cfg.arquivo_estado)
    if not args.todas:
        corte = hoje() - timedelta(days=cfg.ignorar_vencidas_ha_dias)
        demandas = [d for d in demandas if not estado.tratada(d) and d.fatal >= corte]
    print(f"{len(demandas)} prazo(s) a atribuir.")
    if not demandas:
        return 0

    caminho_atrib = atribuicoes.caminho_do_dia(cfg.atrib_pasta, hoje())
    g = Graph(cfg.client_id, cfg.tenant_id, cfg.token_cache)
    contagem = {"atribuida": 0, "ignorada": 0, "adiada": 0}
    with Planilha(g, cfg.sp_host, cfg.sp_site, cfg.sp_arquivo) as plan:
        abas = plan.abas()
        aba = args.aba or escolher_aba(abas, hoje())
        if not aba or aba not in abas:
            print(f"Aba da semana não encontrada (abas: {', '.join(abas[:5])}...). Use --aba.")
            return 1
        print(f'Programação: {cfg.sp_arquivo} -> aba "{aba}"')
        abas_busca = sorted((a for a in abas if data_da_aba(a)), key=data_da_aba, reverse=True)[:6]

        for n, d in enumerate(demandas, 1):
            r = processar_demanda(n, len(demandas), d, cfg, g, plan, aba, abas_busca, estado,
                                  caminho_atrib, args.simular)
            contagem[r] += 1

    print(f"\nConcluído: {contagem['atribuida']} atribuída(s), {contagem['ignorada']} ignorada(s), "
          f"{contagem['adiada']} para depois.")
    if contagem["atribuida"] and not args.simular:
        print(f"Atribuições do dia: {caminho_atrib}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
