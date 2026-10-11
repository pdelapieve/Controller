from datetime import date, datetime, timezone

from publicacoes_app.email_outlook import html_para_texto
from publicacoes_app.extrator import ExtratorRegex
from publicacoes_app.planilha import (
    ajustar_formula,
    coluna_letra,
    de_serial,
    escolher_aba,
    linha_de_insercao,
    para_serial,
)
from publicacoes_app.prazos import (
    CalendarioForense,
    calcular_fatal,
    calendario_para,
    datas_internas,
    normalizar_cnj,
)

RS = CalendarioForense(uf="RS")


def test_cnj():
    assert normalizar_cnj("CS 5149190-50.2024.8.21.0001 - Ótica") == "5149190-50.2024.8.21.0001"
    assert normalizar_cnj("52112058420268210001") == "5211205-84.2026.8.21.0001"
    assert normalizar_cnj("sem número") is None


def test_disponibilizacao_vira_publicacao_no_proximo_dia_util():
    # WebJur: disponibilizado sexta 09/10/2026; 12/10 é feriado -> publicação 13/10.
    assert RS.proximo_util(date(2026, 10, 9)) == date(2026, 10, 13)


def test_eproc_inicio_da_contagem():
    # Prazo de 5 dias com contagem iniciada em 07/10/2026 (caso Lécio x Ótica Gravataí).
    fatal = calcular_fatal(RS, "inicio_contagem", date(2026, 10, 7), 5)
    assert fatal == date(2026, 10, 14)


def test_publicacao_exclui_dia_do_comeco_e_pula_feriados():
    # Publicado em 13/10; 15 dias úteis; 02/11 é Finados.
    fatal = calcular_fatal(RS, "publicacao", date(2026, 10, 13), 15)
    assert fatal == date(2026, 11, 4)
    # Pela disponibilização, o resultado tem de ser o mesmo.
    assert calcular_fatal(RS, "disponibilizacao", date(2026, 10, 9), 15) == fatal


def test_recesso_forense_suspende_prazo():
    fatal = calcular_fatal(RS, "publicacao", date(2026, 12, 18), 5)
    assert fatal == date(2027, 1, 27)  # 21, 22, 25, 26, 27/01


def test_feriados_justica_federal():
    federal = calendario_para("5013571-67.2025.4.04.7100", "RS", [])
    estadual = calendario_para("5149190-50.2024.8.21.0001", "RS", [])
    quinta_santa = date(2026, 4, 2)
    assert not federal.eh_util(quinta_santa)
    assert estadual.eh_util(quinta_santa)
    assert not estadual.eh_util(date(2026, 6, 4))  # Corpus Christi


def test_prazo_corrido_prorroga_para_dia_util():
    # 10 dias corridos a partir de 01/10 (qui) -> termina 11/10 (dom) -> prorroga p/ 13/10.
    assert calcular_fatal(RS, "publicacao", date(2026, 10, 1), 10, uteis=False) == date(2026, 10, 13)


def test_datas_internas():
    d = datas_internas(RS, date(2026, 10, 20), antecedencia_lo=3, antecedencia_revisao=1)
    assert d.lo == date(2026, 10, 15)
    assert d.revisao == date(2026, 10, 19)
    # Prazo curto: sugestões não ficam no passado.
    d = datas_internas(RS, date(2026, 10, 14), 3, 1, hoje=date(2026, 10, 11))
    assert d.lo == date(2026, 10, 13) and d.revisao == date(2026, 10, 13)


def test_escolher_aba():
    abas = ["W41 13102026", "W40 05102026", "W39 28092026", "Contencioso"]
    assert escolher_aba(abas, date(2026, 10, 7)) == "W40 05102026"
    # Domingo: já considera a semana seguinte.
    assert escolher_aba(abas, date(2026, 10, 11)) == "W41 13102026"
    assert escolher_aba(abas, date(2026, 10, 16)) == "W41 13102026"
    # Semana sem aba ainda: usa a mais recente.
    assert escolher_aba(abas, date(2026, 10, 21)) == "W41 13102026"


def test_serial_excel():
    assert para_serial(date(2026, 10, 13)) == 46308
    assert de_serial(46308) == date(2026, 10, 13)
    assert de_serial("13/10/2026") == date(2026, 10, 13)
    assert de_serial("sine die") is None
    assert coluna_letra(12) == "M" and coluna_letra(26) == "AA"


def test_linha_de_insercao_ordena_por_prazo_lo():
    s = para_serial
    linhas = [
        ["Cliente", "Prazo LO"],
        ["A", s(date(2026, 10, 9))],
        ["B", s(date(2026, 10, 13))],
        ["C", s(date(2026, 10, 15))],
        ["D", "sine die"],
        ["E", ""],
    ]
    assert linha_de_insercao(linhas, 1, date(2026, 10, 13)) == 3
    assert linha_de_insercao(linhas, 1, date(2026, 10, 1)) == 1
    assert linha_de_insercao(linhas, 1, date(2026, 12, 1)) == 4
    assert linha_de_insercao(linhas, 1, None) == 6


def test_ajustar_formula():
    f = '=IF(K2="Concluído","",IF(AND(ISNUMBER(G2),NETWORKDAYS(TODAY(),G2)-1=2),"D-2",IF(E2<TODAY(),"VENCIDO","")))'
    novo = ajustar_formula(f, 2, 17)
    assert "K17" in novo and "G17" in novo and "E17" in novo
    assert "2)" not in novo.replace("=2", "")
    assert '"D-2"' in novo
    assert ajustar_formula("=LOG10(A10)", 10, 11) == "=LOG10(A11)"


WEBJUR = """
<b>Publicação: 1</b><br/><b>Data de Disponibilização:</b> 09/10/2026
<div><b>Data de Publicação:</b> 13/10/2026 </div>
<div><b>Local: </b>DJEN - TJRS - 8ª Vara da Fazenda Pública do Foro Central da Comarca de Porto Alegre</div>
<div>Intimação<br/>Ato ordinatório<br/>PROCESSO: 5211205-84.2026.8.21.0001 - CUMPRIMENTO DE SENTENcA</div>
"""

EPROC = """Prezados, bom dia.
Prazo em d-2.
178 02/10/2026 17:26:50 Expedida/certificada a intimação eletrônica
Prazo: 5 dias Status:ABERTO
Data inicial da contagem do prazo: 07/10/2026 00:00:00"""

RECEBIDO = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)


def test_extrator_regex_webjur():
    texto = html_para_texto(WEBJUR)
    [p] = ExtratorRegex().extrair("Public 1. UFs 5.", texto, RECEBIDO)
    assert p.processo == "5211205-84.2026.8.21.0001"
    assert p.marco == "publicacao" and p.data_marco == date(2026, 10, 13)
    assert p.prazo_inferido
    assert "8ª Vara da Fazenda" in p.orgao


def test_extrator_regex_eproc():
    assunto = "Processo 5149190-50.2024.8.21.0001 TJRS - Prazo em d-2 para Contrarrazoar Embargos"
    [p] = ExtratorRegex().extrair(assunto, EPROC, RECEBIDO)
    assert p.processo == "5149190-50.2024.8.21.0001"
    assert p.prazo_dias == 5 and not p.prazo_inferido
    assert p.marco == "inicio_contagem" and p.data_marco == date(2026, 10, 7)


def test_extrator_regex_ignora_confirmacao():
    assert ExtratorRegex().extrair("RE: Publicações", "Prezados,\nPrazo já agendado.\nAtenciosamente", RECEBIDO) == []


class _FakeGraph:
    def __init__(self):
        self.posts = []

    def post(self, caminho, json=None, **kw):
        self.posts.append((caminho, json))
        return {"webLink": "https://outlook/evento"}


class _FakePlanilha:
    def __init__(self):
        self.incluidas = []

    def buscar_processo(self, abas, processo):
        return {"Cliente": "Lécio José de Barros Filho", "Natureza": "Contencioso",
                "Caso": "CS 5149190-50.2024.8.21.0001 - Ótica Gravataí"}

    def duplicada(self, aba, processo, fatal):
        return False

    def incluir(self, aba, tarefa):
        self.incluidas.append((aba, tarefa))
        return 10


def test_fluxo_interativo(monkeypatch, tmp_path):
    from publicacoes_app import cli
    from publicacoes_app.config import Config
    from publicacoes_app.email_outlook import Email

    cfg = Config(client_id="x", tenant_id="y", uf="RS", equipe={"Pedro": "p@x", "Danieli": ""},
                 eventos=["lo", "fatal"], base_dir=tmp_path)
    email = Email(id="1", assunto="Processo 5149190-50.2024.8.21.0001 - Contrarrazoar Embargos",
                  remetente="controladoria@x", recebido=RECEBIDO, texto=EPROC, categorias=[], link="")
    respostas = iter([
        "A",            # agendar
        "2",            # executor: Danieli
        "1",            # revisor: Pedro
        "",             # fatal sugerido (14/10/2026)
        "",             # LO sugerido
        "",             # revisão sugerida
        "", "", "",     # cliente / natureza / caso vindos da planilha
        "Contrarrazões aos Embargos de Declaração",
        "", "",         # prioridade / observações
        "s",            # confirmar
    ])
    monkeypatch.setattr("builtins.input", lambda _="": next(respostas))
    monkeypatch.setattr(cli, "hoje", lambda: date(2026, 10, 7))
    g, plan = _FakeGraph(), _FakePlanilha()

    assert cli.processar_email(email, ExtratorRegex(), cfg, g, plan, "W41 13102026", [], simular=False)

    [(aba, t)] = plan.incluidas
    assert aba == "W41 13102026"
    assert (t.executor, t.revisor) == ("Danieli", "Pedro")
    assert t.fatal == date(2026, 10, 14)
    assert t.lo == date(2026, 10, 8) and t.revisao == date(2026, 10, 13)
    assert t.cliente == "Lécio José de Barros Filho"
    eventos = [j for c, j in g.posts if c == "/me/events"]
    assert [e["start"]["dateTime"][:10] for e in eventos] == ["2026-10-08", "2026-10-14"]
    assert eventos[1]["subject"].startswith("[FATAL] Lécio")
    assert eventos[0]["attendees"] == []
