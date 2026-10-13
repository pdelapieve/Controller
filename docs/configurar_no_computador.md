# Configuração no computador da Betina (Claude Desktop / Cowork)

As tarefas agendadas que usam o Claude in Chrome rodam no Claude Desktop do
computador (Windows) e só podem ser criadas ou alteradas por lá. Abra uma
conversa do **Cowork nesse computador** e cole a mensagem abaixo, inteira.
O Claude de lá vai pedir sua aprovação para cada alteração.

---

````text
Preciso de duas alterações nas minhas tarefas agendadas. Peça minha aprovação antes de salvar cada uma e, ao final, me mostre como ficou.

1) ALTERE a tarefa agendada existente "Prazos do Mês no L.O." (não apague nem recrie; mantenha o horário atual, dias úteis às 17h). Substitua o texto (prompt) dela inteiramente por este:

<<<INÍCIO DO TEXTO 1>>>
Extraia as tarefas pendentes do Legal One (mês corrente e próximos 60 dias) e gere a planilha de controle.

Passo a passo:
1. Abra https://charneskiadvogados.novajus.com.br no navegador local (Claude in Chrome). A sessão normalmente já está autenticada como Pedro Delapieve; se pedir login manual, avise o usuário imediatamente e aguarde a confirmação antes de prosseguir, sem travar a tarefa.
2. Vá em Agenda > Compromissos e tarefas > aba "Avançada" (Pesquisa Avançada). Preencha "Data conclusão prevista" = Entre, do dia 01 do mês corrente até HOJE + 60 DIAS CORRIDOS, e Status = Pendente (marcar a caixa "Pendente" no lookup de Status).
3. Atalho que funciona: navegar direto para a visão de lista com os filtros na URL —
   /agenda/CompromissoTarefa/Search?IsSearchExecutedByUser=true&ShowAdvancedFilters=True&Status[0].Id=0&Status[0].Value=Pendente&TipoDtConclusao=0&DtConclusaoInicio=DD/MM/AAAA&DtConclusaoFim=DD/MM/AAAA&StatusSimples[0].Id=0&StatusSimples[0].Value=Pendente
   (datas URL-encoded; paginar com &Page=N até acabar). A visão de calendário mostra só as agendas exibidas — use sempre a visão de lista.
4. Para cada tarefa colete: ID, descrição completa (buscar em /agenda/tarefas/DetailsCompromissoTarefa/{id}, campo "Descrição", pois a grade trunca), tipo/subtipo da tarefa (mesma página de detalhes), data de conclusão prevista, vínculo (pasta, número do processo e cliente principal — cada um em campo separado) e o responsável — o envolvido marcado na coluna "Responsável" em /agenda/tarefas/DetailsEnvolvidos/{id}?renderOnlySection=True.
5. Classifique cada item comparando o vencimento com a data de hoje: Vencido (data passada), Vence Hoje, A Vencer (data futura).
6. Monte um .xlsx (fonte Arial) com a aba "Tarefas Pendentes" e as colunas exatas, nesta ordem: ID | Status | Vencimento | Responsável | Cliente | Processo | Pasta | Tipo | Tarefa.
   - ID = número da tarefa no L.O. (somente o número).
   - Vencimento = célula de DATA real (não texto), formato DD/MM/AAAA.
   - Processo = número do processo exatamente como no vínculo (padrão CNJ quando houver); Pasta = identificador da pasta; Cliente = cliente principal. Deixe a célula vazia quando a informação não existir — não junte campos.
   - Tipo = tipo/subtipo da tarefa como aparece no L.O. (é ele que indica se a tarefa é de execução ou de revisão).
   - Tarefa = descrição completa.
   Ordene por data, com cores por status, filtro e painéis congelados; e uma aba "Resumo" com contagens por status e por responsável (usando COUNTIF/COUNTIFS, não valores fixos). Rode o recálculo do skill xlsx antes de entregar.
7. Nomeie o arquivo Tarefas_Pendentes_LegalOne_<Mês>-<Ano>.xlsx (mês/ano de hoje), entregue com SendUserFile e salve também em C:\Users\Betina\Downloads via device_commit_files, substituindo o arquivo do mesmo nome (se a pasta não estiver conectada, peça acesso com device_request_folder_access). Este arquivo é lido pelo app de atribuição de prazos — mantenha exatamente o nome, a aba e as colunas acima.
8. Ao final, apresente um resumo em texto: quantos itens estão vencidos, quantos vencem hoje, quantos a vencer (separando os do mês corrente dos meses seguintes) e qual responsável concentra mais pendências.
<<<FIM DO TEXTO 1>>>

2) CRIE uma nova tarefa chamada "Andamentos de fluxo no L.O.", neste computador, SEM agendamento (vou rodar manualmente, depois de atribuir os prazos), com acesso ao Claude in Chrome e à pasta C:\Users\Betina\Downloads, com este texto:

<<<INÍCIO DO TEXTO 2>>>
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
<<<FIM DO TEXTO 2>>>

Não execute nenhuma das duas tarefas agora; só salve.
````
