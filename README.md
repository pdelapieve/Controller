# Controller – atribuição de prazos do Legal One

App de linha de comando que:

1. lê a planilha gerada todo dia útil pela rotina **"Prazos do Mês no L.O."**
   (`Tarefas_Pendentes_LegalOne_<Mês>-<Ano>.xlsx`, em `C:\Users\Betina\Downloads`);
2. junta, para cada prazo, a tarefa do **executor** e a do **revisor** cadastradas
   pela controladoria e calcula o **fatal** (conclusão da tarefa do revisor = D-2
   do fatal, em dias úteis forenses);
3. **pergunta quem será o executor e o revisor** (datas, cliente, caso,
   providência e prioridade podem ser ajustados);
4. cria os compromissos no **calendário do Outlook** (por padrão: Prazo LO e Fatal);
5. inclui a linha na **`JOBS/Programação 2026.xlsx`**, na **aba da semana
   corrente**, em ordem de Prazo LO, copiando a fórmula da coluna *Vencimento*;
6. registra a atribuição em **`Atribuicoes_<AAAA-MM-DD>.xlsx`** – a planilha do
   dia com pasta, processo, executor, revisor, datas, IDs das tarefas no L.O. e o
   **texto do andamento** pronto para lançar na pasta do processo
   (`PEDRO - Novo Fluxo: Executor: X, Revisor: Y.`).

Nada é gravado sem confirmação. Prazos já tratados (atribuídos ou ignorados)
não voltam nas execuções seguintes; prazos que já estão na aba da semana com o
mesmo fatal vêm com "Ignorar" como resposta padrão.

```
── 3/12 ──────────────────────────────────────────────────────────────────
  Cliente         Lécio José de Barros Filho
  Processo        5149190-50.2024.8.21.0001
  Pasta L.O.      1234
  Tarefa          Contrarrazões aos Embargos de Declaração
  Tarefa executor 13/10/2026 - resp. atual: Tiago Coster (ID 101)
  Tarefa revisor  15/10/2026 - resp. atual: Tiago Coster (ID 102)
  Fatal (D+2)     19/10/2026 (seg)
  [A]tribuir, [I]gnorar, [D]epois [A]:
  1) Pedro  2) Heron  3) Tiago  4) Lorenzo  5) Danieli  6) Arthur
Executor: 5
Revisor: 1
...
  ✔ Programação: aba "W41 13102026", linha 10.
  ✔ Outlook: 2 compromisso(s).
  ✔ Atribuição registrada para o andamento no L.O.
```

## Configuração no Claude Desktop

As rotinas que usam o Claude in Chrome (extração do L.O. e lançamento dos
andamentos) só podem ser criadas ou alteradas no computador onde rodam. Cole a
mensagem de [`docs/configurar_no_computador.md`](docs/configurar_no_computador.md)
numa conversa do Cowork nesse computador.

## Rotina do L.O.

O app lê o formato atual da planilha, mas funciona melhor com a versão
atualizada da rotina (período até hoje + 60 dias, colunas separadas com ID,
Processo, Pasta e Tipo). O texto para colar na tarefa agendada do Claude
Desktop está em [`docs/rotina_prazos_do_mes_LO.md`](docs/rotina_prazos_do_mes_LO.md).

## Andamentos no L.O.

A planilha `Atribuicoes_<data>.xlsx` é o resumo do dia para a controladoria.
O texto do andamento segue o padrão do escritório
(`PEDRO - Novo Fluxo: Executor: Danieli, Revisor: Pedro.`). Para lançá-los
automaticamente pelo Claude in Chrome, use a tarefa descrita em
[`docs/rotina_andamentos_LO.md`](docs/rotina_andamentos_LO.md).

## Instalação

Requer Python 3.11+, no computador onde a rotina salva a planilha do L.O.

```bash
python -m venv .venv
.venv\Scripts\activate             # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy config.example.toml config.toml
```

Edite o `config.toml` (IDs do app da Microsoft, equipe, pastas).

### Registro do app no Microsoft Entra ID (uma vez)

O app acessa seu calendário e o SharePoint **em seu nome** (permissões delegadas).

1. <https://entra.microsoft.com> → *Identidade* → *Aplicativos* → *Registros de aplicativo* → **Novo registro**
   (nome `Controller Prazos`, *somente esta organização*).
2. Copie **ID do aplicativo (cliente)** e **ID do diretório (locatário)** para `[microsoft]` no `config.toml`.
3. *Autenticação* → **Permitir fluxos de clientes públicos = Sim**.
4. *Permissões de API* → *Microsoft Graph* → *Permissões delegadas*:
   `Calendars.ReadWrite`, `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `User.Read`
   → **Conceder consentimento do administrador**.

No primeiro uso o app mostra um código para <https://microsoft.com/devicelogin>.
O token fica em `.token_cache.json` (não versionado).

## Uso

```bash
python -m publicacoes_app               # planilha do L.O. mais recente
python -m publicacoes_app --simular     # mostra tudo, não grava nada
python -m publicacoes_app --arquivo "C:\...\Tarefas_Pendentes_LegalOne_Outubro-2026.xlsx"
python -m publicacoes_app --aba "W41 13102026"
python -m publicacoes_app --todas       # inclui prazos já tratados e vencidos há mais tempo
```

Para cada prazo: **A** atribui, **I** ignora (não volta mais), **D** deixa para depois.

### Regras de datas

- **Fatal** = conclusão da tarefa do revisor no L.O. + 2 dias úteis
  (sem tarefa de revisor, usa a do executor e avisa).
- **Prazo LO** e **Revisão** = datas das tarefas do executor e do revisor no L.O.
- Dias úteis: sem fins de semana, feriados nacionais e do RS, Carnaval,
  Corpus Christi, feriados da Justiça Federal (processos J=4) e recesso de
  20/12 a 20/01. Pontos facultativos vão em `prazos.feriados_extras`.

### Aba da semana

Abas no padrão `W<nº> DDMMAAAA`. Usa a aba cuja data cai na semana corrente;
aos sábados e domingos, a da semana seguinte; se não existir, a mais recente.

## Testes

```bash
pip install pytest
python -m pytest
```
