# Controller – agendamento de prazos das publicações

App de linha de comando que:

1. lê os e-mails da pasta **Publicações** do Outlook (WebJur/DJEN, Legal One/Datacloud, controladoria);
2. identifica, para cada publicação, o processo, a providência e o **prazo** – e calcula o **fatal** em dias úteis (CPC arts. 219, 220 e 224; feriados nacionais, estaduais, forenses e da Justiça Federal; recesso de 20/12 a 20/01);
3. **pergunta quem será o executor e o revisor** (e permite ajustar datas, cliente, caso, providência, prioridade e observações);
4. cria os compromissos no **calendário do Outlook** (por padrão: Prazo LO e Fatal);
5. inclui a linha na planilha **`JOBS/Programação 2026.xlsx`**, na **aba da semana corrente** (`W41 13102026` etc.), na posição ordenada pelo Prazo LO, copiando a fórmula da coluna *Vencimento*.

Nada é gravado sem confirmação. E-mails tratados recebem a categoria
"Prazo agendado (app)" no Outlook e não voltam na próxima execução.

```
══════════════════════════════════════════════════════════════════════════════
09/10/2026 07:24  controladoria@charneski.com.br
Assunto: Processo 5149190-50.2024.8.21.0001 TJRS 1 grau - Lécio José x Ótica Gravataí - ...

  ── Prazo 1/1 ──────────────────────────────────────────────────
  Processo         5149190-50.2024.8.21.0001
  Providência      Contrarrazões aos Embargos de Declaração
  Prazo            5 dias úteis
  Marco            início da contagem em 07/10/2026
  Fatal (sugerido) 14/10/2026 (qua)
  [A]gendar, [I]gnorar, [D]epois [A]:
  1) Pedro  2) Heron  3) Tiago  4) Lorenzo  5) Danieli  6) Arthur
Executor: 5
Revisor: 1
Fatal (DD/MM/AAAA, '-' p/ vazio) [14/10/2026]:
Prazo LO (executor) (DD/MM/AAAA, '-' p/ vazio) [13/10/2026]:
...
  ✔ Planilha: aba "W41 13102026", linha 10.
  ✔ Outlook: 2 compromisso(s) criado(s).
```

## Instalação

Requer Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config.example.toml config.toml # Windows: copy config.example.toml config.toml
```

Edite o `config.toml` (IDs do app da Microsoft, equipe, antecedências, etc.).

### Registro do app no Microsoft Entra ID (uma vez)

O app acessa seu e-mail, calendário e o SharePoint **em seu nome** (permissões delegadas).

1. Acesse <https://entra.microsoft.com> → *Identidade* → *Aplicativos* → *Registros de aplicativo* → **Novo registro**.
   - Nome: `Controller Prazos`; tipo de conta: *somente esta organização*. Registrar.
2. Copie **ID do aplicativo (cliente)** e **ID do diretório (locatário)** para `[microsoft]` no `config.toml`.
3. *Autenticação* → **Permitir fluxos de clientes públicos = Sim** → Salvar.
4. *Permissões de API* → *Adicionar* → *Microsoft Graph* → *Permissões delegadas*:
   `Mail.ReadWrite`, `Calendars.ReadWrite`, `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `User.Read`.
   Depois clique em **Conceder consentimento do administrador** (precisa de um admin do tenant).

No primeiro uso o app mostra um código e o endereço <https://microsoft.com/devicelogin>;
faça login com sua conta. O token fica em `.token_cache.json` (não versionado).

### Identificação dos prazos com IA (recomendado)

Com a variável `ANTHROPIC_API_KEY` definida, o app usa o Claude para ler a
publicação, identificar a providência cabível e o prazo (inclusive o prazo
legal quando o texto não traz o número de dias). Sem a chave, usa um
extrator simples por expressões regulares, que acha processo, "Prazo: N dias"
e as datas de publicação/início da contagem, mas sugere 15 dias quando o
prazo não consta do texto.

```bash
export ANTHROPIC_API_KEY=...   # Windows: set ANTHROPIC_API_KEY=...
```

## Uso

```bash
python -m publicacoes_app                 # e-mails dos últimos 3 dias (config)
python -m publicacoes_app --dias 7
python -m publicacoes_app --desde 01/10/2026
python -m publicacoes_app --aba "W40 05102026"
python -m publicacoes_app --simular       # não grava nada; bom para testar
```

Para cada prazo: **A** agenda, **I** ignora (ex.: mera ciência), **D** deixa
para depois (o e-mail volta na próxima execução).

### Como a aba da semana é escolhida

As abas seguem o padrão `W<nº> DDMMAAAA`. O app usa a aba cuja data cai na
semana corrente (segunda a domingo); aos sábados e domingos considera a
semana seguinte. Se a aba da semana ainda não existir, usa a mais recente –
ou informe `--aba`.

### Datas sugeridas

- **Fatal**: informado no texto, ou calculado a partir do marco
  (disponibilização → publicação no dia útil seguinte → contagem a partir do
  dia útil seguinte; no eproc, a "data inicial da contagem" já é o 1º dia).
- **Prazo LO** = fatal − `antecedencia_lo` dias úteis (padrão 3).
- **Revisão** = fatal − `antecedencia_revisao` dias úteis (padrão 1).
- Nenhuma sugestão fica no passado.

O cálculo é uma estimativa: **sempre confira o fatal**. Feriados municipais,
pontos facultativos e suspensões por portaria devem ir em
`prazos.feriados_extras`.

## Testes

```bash
pip install pytest
python -m pytest
```
