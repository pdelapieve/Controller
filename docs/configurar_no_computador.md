# Configuração no computador da rotina (Claude Desktop / Cowork)

As tarefas que usam o Claude in Chrome rodam no Claude Desktop do computador
e só podem ser criadas ou alteradas por lá. Abra uma conversa do **Cowork
nesse computador** e cole a mensagem abaixo, inteira.

O dia a dia fica assim: no celular, a página **Atribuição de Prazos**
(https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY) lê a planilha do L.O. no
seu OneDrive e você escolhe executor e revisor; no computador, a tarefa
"Aplicar atribuições do celular" grava na Programação, no Outlook e no L.O.

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

2) CRIE uma nova tarefa chamada "Aplicar atribuições do celular", neste computador, agendada para dias úteis às 18h (e que eu também possa rodar manualmente), com acesso ao Claude in Chrome, com este texto:

<<<INÍCIO DO TEXTO 2>>>
Aplique no computador as atribuições de prazo feitas pelo celular.

FONTE: a página https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY, coleção "atribuicoes". Leia-a com a ferramenta ArtifactData (action "list", collection "atribuicoes"). Se essa ferramenta não estiver disponível, abra a página no Chrome, vá na aba "Atribuídos" e leia os cartões marcados "Pendente no computador".
Cada atribuição traz: cliente, natureza, caso, providencia, prioridade, observacoes, processo, pasta, executor, revisor, lo, revisao, fatal (datas AAAA-MM-DD), andamento_texto e três marcadores: programacao, agenda, andamento (true = já feito).

Considere só as atribuições com algum marcador false. Mostre a lista e PEÇA CONFIRMAÇÃO antes de gravar qualquer coisa. Depois, para cada uma:

1. PROGRAMAÇÃO (se programacao = false): abra no Chrome, no Excel para a Web, https://charneskiadvogados.sharepoint.com/sites/CharneskiAdvogados_Drive2/Documentos%20Partilhados/JOBS/Programa%C3%A7%C3%A3o%202026.xlsx . Use a PRIMEIRA aba (semana corrente, padrão "W## ddmmaaaa"). Se já existir linha com o mesmo processo e o mesmo Fatal, não duplique — só marque como feito. Senão, insira uma linha na posição que mantém a ordem por "Prazo LO" (linhas "sine die" ou sem data ficam no fim) e preencha: Cliente, Natureza, Caso, Providência, Prazo LO, Revisão, Fatal (DD/MM/AAAA), Executor, Revisor, Prioridade, Status vazio, Observações. Na coluna Vencimento copie a fórmula da linha de cima (ajustando a linha). Confira que a linha ficou certa.
2. OUTLOOK (se agenda = false): no Outlook na Web (Chrome), crie dois compromissos de dia inteiro, marcados como "livre": "[Prazo LO] <cliente> - <providência> (<processo>)" na data lo e "[FATAL] <cliente> - <providência> (<processo>)" na data fatal, com executor, revisor e as três datas no corpo. Sem convidados.
3. ANDAMENTO NO L.O. (se andamento = false): em https://charneskiadvogados.novajus.com.br abra o processo pela pasta (campo pasta, ex.: RAUL-JUD-AO-01; se vazio, pelo número do processo) e confira no cabeçalho que número e partes batem. Se não baterem, não lance e registre a divergência. Senão: aba "Andamentos" → "Adicionar", tipo "Andamento", data de hoje, descrição exatamente igual a andamento_texto (ex.: "PEDRO - Novo Fluxo: Executor: Danieli, Revisor: Pedro."). Antes, veja se o mesmo texto já foi lançado hoje na pasta; se foi, não duplique. Não altere tarefas, responsáveis nem prazos.
4. Depois de cada passo concluído, marque o marcador correspondente como true: com ArtifactData (action "update", collection "atribuicoes", doc_id da atribuição, data {"programacao": true} etc., passando o if_version lido) ou, pela página no Chrome, tocando no botão "Programação", "Outlook" ou "Andamento L.O." do cartão.

Ao final, responda com um resumo: o que foi aplicado, o que falhou e por quê.
<<<FIM DO TEXTO 2>>>

Não execute nenhuma das duas tarefas agora; só salve.
````
