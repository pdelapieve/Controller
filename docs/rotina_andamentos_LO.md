# Lançamento dos andamentos de atribuição no L.O. (proposta)

Depois de rodar o app, a planilha `Atribuicoes_<AAAA-MM-DD>.xlsx` (em
`C:\Users\Betina\Downloads`) traz, para cada prazo atribuído: pasta,
processo, executor, revisor, datas, IDs das tarefas no L.O. e o **texto do
andamento** pronto. A coluna "Andamento lançado" começa como "Não".

O lançamento no L.O. pode ser feito de duas formas:

1. **Manual** – a controladoria (ou você) abre cada pasta e cola o texto da
   coluna "Texto do andamento".
2. **Automático, com o Claude in Chrome** – uma tarefa no Claude Desktop, do
   mesmo jeito que a rotina "Prazos do Mês no L.O.", com o texto abaixo.
   Rode-a sob demanda (sem agendamento) até confiar no resultado.

Antes de usar a opção 2, preencha os dois itens marcados com `<<…>>`:
o **tipo de andamento** que a controladoria usa para atribuições e se o
andamento deve **notificar** alguém (ex.: o usuário "Controladoria").

---

```text
Lance no Legal One os andamentos de atribuição de executor e revisor registrados hoje.

1. Leia C:\Users\Betina\Downloads\Atribuicoes_<data de hoje AAAA-MM-DD>.xlsx (aba "Atribuições"). Considere só as linhas com "Andamento lançado" = "Não". Se o arquivo não existir ou não houver linhas pendentes, informe e encerre.
2. Mostre a lista (Cliente, Processo, Pasta, Executor, Revisor, Fatal) e PEÇA CONFIRMAÇÃO antes de lançar qualquer andamento.
3. Abra https://charneskiadvogados.novajus.com.br no navegador local (Claude in Chrome). Se pedir login, avise e aguarde.
4. Para cada linha confirmada:
   a. Localize a pasta pelo campo "Pasta L.O." (ou, se vazio, pelo número do processo) e confira que o cliente e o processo batem com a planilha. Se não bater, NÃO lance — registre a divergência e passe para a próxima.
   b. Na pasta, crie um andamento do tipo <<TIPO DE ANDAMENTO USADO PELA CONTROLADORIA>>, com a data de hoje e a descrição igual à coluna "Texto do andamento". <<Notificar: Controladoria / não notificar>>.
   c. Não altere tarefas, responsáveis nem prazos – apenas crie o andamento. A controladoria faz a redistribuição das tarefas a partir dele.
   d. Confira que o andamento aparece na lista de andamentos da pasta.
5. Atualize a planilha: "Andamento lançado" = "Sim" nas linhas lançadas (salve o arquivo no mesmo lugar). Se o arquivo estiver aberto e não puder ser salvo, informe quais linhas foram lançadas.
6. Responda com um resumo: quantos andamentos lançados, quais falharam e por quê.
```
