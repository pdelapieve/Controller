"""Fluxo interativo: e-mails de publicações -> prazo -> Outlook + planilha."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from datetime import date, datetime, timezone
from pathlib import Path

from . import config as cfgmod
from .agenda import criar_eventos
from .email_outlook import Email, janela_inicial, listar, localizar_pasta, marcar_processado
from .extrator import ExtratorRegex, PrazoIdentificado, criar_extrator
from .graph import Graph
from .planilha import Planilha, Tarefa, data_da_aba, escolher_aba
from .prazos import calcular_fatal, calendario_para, datas_internas

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
    def __init__(self, caminho: Path):
        self.caminho = caminho
        self.dados = json.loads(caminho.read_text()) if caminho.exists() else {}
        self.dados.setdefault("processados", {})

    def processado(self, email_id: str) -> bool:
        return email_id in self.dados["processados"]

    def marcar(self, email_id: str, resumo: str) -> None:
        self.dados["processados"][email_id] = {"em": datetime.now().isoformat(timespec="seconds"), "resumo": resumo}
        self.caminho.write_text(json.dumps(self.dados, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- fluxo

def sugerir_fatal(p: PrazoIdentificado, cfg) -> tuple[date | None, list[str]]:
    avisos = list(p.avisos)
    if p.fatal_informado:
        return p.fatal_informado, avisos
    if not (p.prazo_dias and p.data_marco):
        avisos.append("Não foi possível calcular o fatal automaticamente.")
        return None, avisos
    cal = calendario_para(p.processo, cfg.uf, cfg.feriados_extras)
    fatal = calcular_fatal(cal, p.marco, p.data_marco, p.prazo_dias, p.uteis)
    if p.prazo_inferido:
        avisos.append(f"Prazo de {p.prazo_dias} dias deduzido (não constava do texto) - confira.")
    return fatal, avisos


def mostrar_prazo(n: int, total: int, p: PrazoIdentificado, fatal: date | None, avisos: list[str]) -> None:
    print(f"\n  ── Prazo {n}/{total} " + "─" * 50)
    marco = {"inicio_contagem": "início da contagem", "publicacao": "publicação",
             "disponibilizacao": "disponibilização", "intimacao": "intimação"}[p.marco]
    campos = [
        ("Processo", p.processo or "(não identificado)"),
        ("Órgão", p.orgao),
        ("Partes", p.partes),
        ("Publicação", p.ato),
        ("Providência", p.providencia),
        ("Prazo", f"{p.prazo_dias} dias {'úteis' if p.uteis else 'corridos'}" if p.prazo_dias else "?"),
        ("Marco", f"{marco} em {p.data_marco:%d/%m/%Y}" if p.data_marco else "?"),
        ("Fatal (sugerido)", f"{fatal:%d/%m/%Y} ({['seg','ter','qua','qui','sex','sáb','dom'][fatal.weekday()]})" if fatal else "?"),
        ("Observação", p.observacao),
    ]
    for k, v in campos:
        if v:
            print(textwrap.fill(v, 100, initial_indent=f"  {k:<17}", subsequent_indent=" " * 19))
    for a in avisos:
        print(f"  ⚠ {a}")


def montar_tarefa(p: PrazoIdentificado, fatal: date | None, cfg, existente: dict | None) -> Tarefa | None:
    equipe = list(cfg.equipe)
    print()
    executor = escolher_pessoa("Executor", equipe)
    revisor = escolher_pessoa("Revisor", equipe, opcional=True)

    cal = calendario_para(p.processo, cfg.uf, cfg.feriados_extras)
    fatal = perguntar_data("Fatal", fatal)
    if fatal:
        sug = datas_internas(cal, fatal, cfg.antecedencia_lo, cfg.antecedencia_revisao, hoje())
        lo_padrao, rev_padrao = sug.lo, (sug.revisao if revisor else None)
    else:
        lo_padrao = rev_padrao = None
    lo = perguntar_data("Prazo LO (executor)", lo_padrao)
    revisao = perguntar_data("Revisão", rev_padrao) if revisor else None

    existente = existente or {}
    if existente:
        print(f"  (Processo já consta na planilha: {existente.get('Cliente')} / {existente.get('Caso')})")
    cliente = perguntar("Cliente", existente.get("Cliente") or p.cliente)
    natureza = perguntar("Natureza", existente.get("Natureza") or "Contencioso")
    caso = perguntar("Caso", existente.get("Caso") or (p.processo or ""))
    providencia = perguntar("Providência", p.providencia)
    prioridade = perguntar(f"Prioridade ({'/'.join(PRIORIDADES)})", "Alta")
    observacoes = perguntar("Observações", "")

    tarefa = Tarefa(cliente, natureza, caso, providencia, lo, revisao, fatal, executor, revisor, prioridade,
                    observacoes=observacoes)
    print("\n  Resumo: " + " | ".join(
        f"{k}: {v:%d/%m/%Y}" if isinstance(v, date) else f"{k}: {v}"
        for k, v in tarefa.valores().items() if v))
    return tarefa if sim("  Confirmar agendamento?") else None


def processar_email(email: Email, extrator, cfg, g: Graph | None, plan: Planilha | None, aba: str,
                    abas_busca: list[str], simular: bool) -> bool:
    """Retorna True se o e-mail foi totalmente tratado (pode ser marcado como processado)."""
    print("\n" + "═" * 78)
    print(f"{email.recebido.astimezone():%d/%m/%Y %H:%M}  {email.remetente}")
    print(f"Assunto: {email.assunto}")
    try:
        prazos = extrator.extrair(email.assunto, email.texto, email.recebido)
    except Exception as e:  # falha da IA não deve interromper a fila
        print(f"  ⚠ Falha na identificação com IA ({e}); usando extrator simples.")
        prazos = ExtratorRegex().extrair(email.assunto, email.texto, email.recebido)

    if not prazos:
        print("  Nenhum prazo identificado neste e-mail.")
        return sim("  Marcar como processado?")

    tratado = True
    for n, p in enumerate(prazos, 1):
        fatal, avisos = sugerir_fatal(p, cfg)
        mostrar_prazo(n, len(prazos), p, fatal, avisos)
        acao = perguntar("  [A]gendar, [I]gnorar, [D]epois", "A").lower()[:1]
        if acao == "i":
            continue
        if acao == "d":
            tratado = False
            continue

        existente = plan.buscar_processo(abas_busca, p.processo) if (plan and p.processo) else None
        tarefa = montar_tarefa(p, fatal, cfg, existente)
        if not tarefa:
            tratado = False
            continue
        if simular:
            print(f'  (simulação) Seria incluída na aba "{aba}" e agendada no Outlook.')
            continue
        if plan.duplicada(aba, p.processo, tarefa.fatal) and not sim(
            "  ⚠ Já existe linha com este processo e o mesmo fatal na aba. Incluir mesmo assim?", False):
            continue
        linha = plan.incluir(aba, tarefa)
        print(f'  ✔ Planilha: aba "{aba}", linha {linha}.')
        convidados = [cfg.equipe.get(x, "") for x in (tarefa.executor, tarefa.revisor) if x] if cfg.convidar_equipe else []
        links = criar_eventos(g, tarefa, p.processo, p.ato, email.link, cfg.eventos, convidados,
                              cfg.lembrete_minutos, cfg.categoria_agenda)
        print(f"  ✔ Outlook: {len(links)} compromisso(s) criado(s).")
    return tratado


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="publicacoes_app", description=__doc__)
    ap.add_argument("-c", "--config", default="config.toml")
    ap.add_argument("--dias", type=int, help="buscar e-mails dos últimos N dias")
    ap.add_argument("--desde", help="buscar e-mails desde DD/MM/AAAA")
    ap.add_argument("--aba", help="nome da aba da planilha (padrão: semana corrente)")
    ap.add_argument("--simular", action="store_true", help="não grava nada (planilha, Outlook, estado)")
    ap.add_argument("--reprocessar", action="store_true", help="inclui e-mails já processados")
    args = ap.parse_args(argv)

    if not Path(args.config).exists():
        print(f"Arquivo {args.config} não encontrado. Copie config.example.toml para config.toml e ajuste.")
        return 1
    cfg = cfgmod.carregar(args.config)
    if not cfg.equipe:
        print("Cadastre a equipe na seção [equipe] do config.toml.")
        return 1

    g = Graph(cfg.client_id, cfg.tenant_id, cfg.token_cache)
    estado = Estado(cfg.arquivo_estado)
    extrator = criar_extrator(cfg.modelo)
    print(f"Identificação de prazos: {'Claude (' + cfg.modelo + ')' if not isinstance(extrator, ExtratorRegex) else 'extrator simples (sem ANTHROPIC_API_KEY)'}")

    if args.desde:
        desde = datetime.strptime(args.desde, "%d/%m/%Y").replace(tzinfo=timezone.utc)
    else:
        desde = janela_inicial(args.dias or cfg.dias_retroativos)

    pasta_id = localizar_pasta(g, cfg.pasta)
    emails = listar(g, pasta_id, desde, cfg.remetentes)
    if not args.reprocessar:
        emails = [e for e in emails
                  if not estado.processado(e.id) and cfg.categoria_processado not in e.categorias]
    print(f'{len(emails)} e-mail(s) a analisar na pasta "{cfg.pasta}" desde {desde.astimezone():%d/%m/%Y}.')
    if not emails:
        return 0

    with Planilha(g, cfg.sp_host, cfg.sp_site, cfg.sp_arquivo) as plan:
        abas = plan.abas()
        aba = args.aba or escolher_aba(abas, hoje())
        if not aba or aba not in abas:
            print(f"Aba da semana não encontrada (abas: {', '.join(abas[:5])}...). Use --aba.")
            return 1
        print(f'Planilha: {cfg.sp_arquivo} -> aba "{aba}"')
        # Abas recentes para reaproveitar Cliente/Caso de processos já cadastrados.
        abas_busca = sorted((a for a in abas if data_da_aba(a)), key=data_da_aba, reverse=True)[:6]

        for email in emails:
            tratado = processar_email(email, extrator, cfg, g, plan, aba, abas_busca, args.simular)
            if tratado and not args.simular:
                estado.marcar(email.id, email.assunto)
                try:
                    marcar_processado(g, email, cfg.categoria_processado)
                except Exception as e:
                    print(f"  ⚠ Não foi possível categorizar o e-mail no Outlook: {e}")
    print("\nConcluído.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
