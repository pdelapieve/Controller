# Lançamento dos andamentos de ajuste de fluxo no L.O.

Depois de rodar o app, a planilha `Atribuicoes_<AAAA-MM-DD>.xlsx` (em
`C:\Users\Betina\Downloads`) traz, para cada prazo atribuído, a pasta (ex.:
`RAUL-JUD-AO-01`), o processo, executor, revisor, datas, IDs das tarefas no
L.O. e o **texto do andamento** no padrão do escritório:

```
PEDRO - Novo Fluxo: Executor: Danieli, Revisor: Pedro.
```

A controladoria lê o andamento, redistribui as tarefas e responde na própria
pasta ("Controladoria: Ciente. Fluxo readequado.").

O lançamento pode ser:

1. **Manual** – abrir a pasta → aba **Andamentos** → **Adicionar** → tipo
   *Andamento* → colar o texto da coluna "Texto do andamento".
2. **Automático, com o Claude in Chrome** – uma tarefa no Claude Desktop do
   computador que já roda a rotina "Prazos do Mês no L.O.", com o texto
   abaixo. Sugestão: deixá-la **sem agendamento** e rodar sob demanda nas
   primeiras semanas, conferindo o resultado.

---

```text
Lance no Legal One os andamentos de ajuste de fluxo (novo executor/revisor) registrados hoje.

1. Leia C:\Users\Betina\Downloads\Atribuicoes_<data de hoje AAAA-MM-DD>.xlsx (aba "Atribuições"). Considere só as linhas com "Andamento lançado" = "Não". Se o arquivo não existir ou não houver linhas pendentes, informe e encerre.
2. Mostre a lista (Pasta L.O., Cliente, Processo, Executor, Revisor, Fatal, Texto do andamento) e PEÇA CONFIRMAÇÃO antes de lançar qualquer andamento.
3. Abra https://charneskiadvogados.novajus.com.br no navegador local (Claude in Chrome). A sessão normalmente já está autenticada como Pedro Delapieve; se pedir login, avise e aguarde.
4. Para cada linha confirmada:
   a. Abra o processo pela pasta (coluna "Pasta L.O.", ex.: RAUL-JUD-AO-01); se estiver vazia, pesquise pelo número do processo. Confira no cabeçalho "Visualizando processo" que o Número e as Partes batem com o Processo e o Cliente da planilha. Se não bater, NÃO lance — registre a divergência e passe para a próxima.
   b. Antes de lançar, olhe os andamentos mais recentes da pasta: se já existir um andamento com o mesmo texto lançado hoje, não duplique — apenas marque como lançado.
   c. Vá na aba "Andamentos" → botão "Adicionar". Tipo: "Andamento". Data: hoje. Descrição: exatamente o texto da coluna "Texto do andamento" (ex.: "PEDRO - Novo Fluxo: Executor: Danieli, Revisor: Pedro."). Não preencha outros campos além dos obrigatórios e salve.
   d. Não altere tarefas, responsáveis nem prazos — apenas crie o andamento. A controladoria faz a redistribuição a partir dele.
   e. Confira que o andamento aparece no topo da lista de andamentos da pasta.
5. Atualize a planilha: "Andamento lançado" = "Sim" nas linhas lançadas e salve no mesmo lugar (use o skill xlsx). Se o arquivo estiver aberto e não puder ser salvo, informe quais linhas foram lançadas.
6. Responda com um resumo: quantos andamentos lançados, quais pastas e quais falharam e por quê.
```
