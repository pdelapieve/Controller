# Configuração no computador da rotina (Claude Desktop / Cowork)

As tarefas que usam o Claude in Chrome rodam no Claude Desktop do computador
e só podem ser criadas ou alteradas por lá. Abra uma conversa do **Cowork
nesse computador** e cole a mensagem abaixo, inteira.

Como fica o dia a dia:
- **No computador:** rode a tarefa "Atribuir prazos". Ela lista os prazos
  novos, pergunta executor e revisor e grava na hora na Programação, no
  Outlook e no L.O. (e aplica o que você tiver atribuído pelo celular).
- **No celular:** a página **Atribuição de Prazos**
  (https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY) para escolher executor e
  revisor de qualquer lugar.
- **Às 18h:** "Aplicar atribuições do celular" grava o que ficou pendente do
  celular, para os dias em que você não rodar a tarefa no computador.

---

````text
Preciso de quatro alterações nas minhas tarefas agendadas. Peça minha aprovação antes de salvar cada uma e, ao final, me mostre como ficou.

1) ALTERE a tarefa agendada existente "Prazos do Mês no L.O." (não apague nem recrie; mantenha o horário atual, dias úteis às 17h). Substitua o texto (prompt) dela inteiramente por este, e dê a ela acesso às pastas C:\Users\Betina\Downloads e C:\Users\Betina\OneDrive - Charneski Advogados (1):

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
7. Nomeie o arquivo Tarefas_Pendentes_LegalOne_<Mês>-<Ano>.xlsx (mês/ano de hoje), entregue com SendUserFile e salve via device_commit_files, substituindo o arquivo do mesmo nome, em DOIS lugares: (a) C:\Users\Betina\Downloads e (b) a RAIZ do OneDrive de pedro@charneski.com.br — a pasta C:\Users\Betina\OneDrive - Charneski Advogados (1) (a mesma que contém a subpasta Snapshot), não numa subpasta. Se uma pasta não estiver conectada, peça acesso com device_request_folder_access. A cópia da raiz do OneDrive é a que a página "Atribuição de Prazos" do celular lê — mantenha exatamente o nome, a aba e as colunas acima, e confira ao final que o arquivo da raiz do OneDrive ficou com a data de hoje.
8. Ao final, apresente um resumo em texto: quantos itens estão vencidos, quantos vencem hoje, quantos a vencer (separando os do mês corrente dos meses seguintes) e qual responsável concentra mais pendências.
<<<FIM DO TEXTO 1>>>

2) CRIE uma nova tarefa chamada "Atribuir prazos", neste computador, SEM agendamento (eu rodo manualmente), com acesso ao Claude in Chrome e às pastas C:\Users\Betina\Downloads e C:\Users\Betina\OneDrive - Charneski Advogados (1), com este texto:

<<<INÍCIO DO TEXTO 2>>>
Vamos atribuir executor e revisor aos prazos do Legal One e aplicar as atribuições. Fale em português, de forma objetiva.

REGISTRO DE ATRIBUIÇÕES: a página https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY, coleções "atribuicoes" e "ignoradas". Leia e grave com a ferramenta ArtifactData. Se ela não estiver disponível, use a própria página no Chrome (aba "Atribuídos" para ler; botões "Atribuir"/"Ignorar" e os botões de status para gravar).
Cada atribuição tem: tarefas (lista de IDs das tarefas do L.O.), cliente, natureza, caso, providencia, prioridade, observacoes, processo, pasta, executor, revisor, lo, revisao, fatal (AAAA-MM-DD), andamento_texto, criado (data/hora ISO) e os marcadores programacao, agenda, andamento (true = já feito). Em "ignoradas", o id do documento é o ID da tarefa do L.O.

PASSO 1 — PENDÊNCIAS DO CELULAR
Liste as atribuições com algum marcador false (feitas pelo celular e ainda não aplicadas). Elas entram no PASSO 4 junto com as novas.

PASSO 2 — PRAZOS NOVOS
1. Leia a planilha mais recente "Tarefas_Pendentes_LegalOne_<Mês>-<Ano>.xlsx" (pasta C:\Users\Betina\Downloads ou a raiz do OneDrive de pedro@charneski.com.br), aba "Tarefas Pendentes".
2. Para cada linha identifique: vencimento, responsável, cliente, processo, pasta (no formato antigo vêm juntos em "Cliente/Processo": "Cliente • Nº <processo> • Pasta: <pasta>") e a descrição. Papel: "(executor)" ou "(revisor)" na descrição (às vezes falta um parêntese); "Acompanhamento CJ" = tarefa da controladoria; sem marcação = outra.
3. Agrupe por prazo: mesma pasta (ou processo, ou cliente quando "sem vínculo") e mesma descrição desconsiderando "(executor)/(revisor)" → junte a tarefa do executor com a do revisor. Associe a cada grupo a tarefa "Acompanhamento CJ" da mesma pasta, com o mesmo evento ("Eventos 54 a 56", "ID 401620105"…) e data igual ou posterior à última do grupo, se houver.
4. Datas sugeridas: Prazo LO = data da tarefa do executor; Revisão = data da tarefa do revisor; FATAL = data do Acompanhamento CJ (ou, sem ele, a do revisor; sem esta, a do executor) + 2 DIAS ÚTEIS. Dias úteis: sem sábados, domingos, feriados nacionais, 20/09 (RS), Carnaval (seg e ter), Sexta-feira Santa, Corpus Christi, recesso de 20/12 a 20/01 e, para processos da Justiça Federal (dígito J = 4 no número CNJ), quarta e quinta santas, 11/08, 01/11 e 08/12; também 28/10/2026.
5. Retire os grupos cujas tarefas já estejam em "atribuicoes" (campo tarefas) ou em "ignoradas", e os com fatal vencido há mais de 5 dias úteis. Se uma tarefa não tiver ID na planilha, o registro do celular usa um ID calculado; nesse caso compare por processo/pasta + descrição + datas.
6. Leia a primeira aba da Programação (https://charneskiadvogados.sharepoint.com/sites/CharneskiAdvogados_Drive2/Documentos%20Partilhados/JOBS/Programa%C3%A7%C3%A3o%202026.xlsx) e marque os grupos cujo processo já aparece lá com o mesmo Fatal ("já na Programação").

PASSO 3 — PERGUNTAR
Mostre uma tabela numerada, ordenada pelo fatal: nº | Cliente | Providência (curta) | Pasta | Prazo LO | Revisão | Fatal | Responsáveis atuais no L.O. | observação (já na Programação, fatal em até 3 dias etc.).
Equipe: Pedro, Heron, Tiago, Lorenzo, Danieli, Arthur.
Peça executor e revisor de cada item, aceitando respostas em lote (ex.: "1 Danieli/Pedro; 2 Pedro/Tiago; 3 ignorar; 4 Arthur sem revisor") e ajustes de data. Itens que eu não mencionar ficam para depois (não grave nada sobre eles).
Para cada item confirmado, monte a atribuição: andamento_texto = "PEDRO - Novo Fluxo: Executor: <executor>, Revisor: <revisor>." (sem revisor: "PEDRO - Novo Fluxo: Executor: <executor>."); cliente/natureza/caso: os da Programação, se o processo já estiver lá, senão os do L.O. com natureza "Contencioso"; providência = descrição sem o papel; prioridade "Alta", salvo se eu disser outra.
Mostre o resumo final (itens a gravar + pendências do celular) e PEÇA CONFIRMAÇÃO.

PASSO 4 — GRAVAR (para cada atribuição confirmada e cada pendência do celular)
a. Registro: grave/atualize a atribuição em "atribuicoes" (doc_id = o primeiro ID de tarefas). Itens ignorados: um documento por ID de tarefa em "ignoradas".
b. PROGRAMAÇÃO (se programacao = false): no Excel para a Web, primeira aba. Se já houver linha com o mesmo processo e Fatal, não duplique. Senão, insira uma linha mantendo a ordem por "Prazo LO" (linhas "sine die"/sem data no fim) e preencha Cliente, Natureza, Caso, Providência, Prazo LO, Revisão, Fatal (DD/MM/AAAA), Executor, Revisor, Prioridade, Status vazio, Observações; na coluna Vencimento copie a fórmula da linha de cima. Confira a linha.
c. OUTLOOK (se agenda = false): no Outlook na Web, dois compromissos de dia inteiro, "livre", sem convidados: "[Prazo LO] <cliente> - <providência> (<processo>)" na data do Prazo LO e "[FATAL] <cliente> - <providência> (<processo>)" no fatal, com executor, revisor e as três datas no corpo.
d. L.O. (se andamento = false): em https://charneskiadvogados.novajus.com.br abra o processo pela pasta (ou pelo número), confira número e partes no cabeçalho (se não baterem, não lance e me avise), veja se o mesmo texto já foi lançado hoje (não duplique) e lance: aba "Andamentos" → "Adicionar", tipo "Andamento", data de hoje, descrição = andamento_texto. Não altere tarefas, responsáveis nem prazos.
e. Após cada passo concluído, marque o respectivo marcador como true no registro (ArtifactData "update" com o if_version lido, ou o botão na página).

Ao final: resumo do que foi gravado, do que falhou (e por quê) e do que ficou para depois.
<<<FIM DO TEXTO 2>>>

3) CRIE uma nova tarefa chamada "Aplicar atribuições do celular", neste computador, agendada para dias úteis às 18h (e que eu também possa rodar manualmente), com acesso ao Claude in Chrome, com este texto:

<<<INÍCIO DO TEXTO 3>>>
Aplique no computador as atribuições de prazo feitas pelo celular.

FONTE: a página https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY, coleção "atribuicoes". Leia-a com a ferramenta ArtifactData (action "list", collection "atribuicoes"). Se essa ferramenta não estiver disponível, abra a página no Chrome, vá na aba "Atribuídos" e leia os cartões marcados "Pendente no computador".
Cada atribuição traz: cliente, natureza, caso, providencia, prioridade, observacoes, processo, pasta, executor, revisor, lo, revisao, fatal (datas AAAA-MM-DD), andamento_texto e três marcadores: programacao, agenda, andamento (true = já feito).

Considere só as atribuições com algum marcador false. Mostre a lista e PEÇA CONFIRMAÇÃO antes de gravar qualquer coisa. Depois, para cada uma:

1. PROGRAMAÇÃO (se programacao = false): abra no Chrome, no Excel para a Web, https://charneskiadvogados.sharepoint.com/sites/CharneskiAdvogados_Drive2/Documentos%20Partilhados/JOBS/Programa%C3%A7%C3%A3o%202026.xlsx . Use a PRIMEIRA aba (semana corrente, padrão "W## ddmmaaaa"). Se já existir linha com o mesmo processo e o mesmo Fatal, não duplique — só marque como feito. Senão, insira uma linha na posição que mantém a ordem por "Prazo LO" (linhas "sine die" ou sem data ficam no fim) e preencha: Cliente, Natureza, Caso, Providência, Prazo LO, Revisão, Fatal (DD/MM/AAAA), Executor, Revisor, Prioridade, Status vazio, Observações. Na coluna Vencimento copie a fórmula da linha de cima (ajustando a linha). Confira que a linha ficou certa.
2. OUTLOOK (se agenda = false): no Outlook na Web (Chrome), crie dois compromissos de dia inteiro, marcados como "livre": "[Prazo LO] <cliente> - <providência> (<processo>)" na data lo e "[FATAL] <cliente> - <providência> (<processo>)" na data fatal, com executor, revisor e as três datas no corpo. Sem convidados.
3. ANDAMENTO NO L.O. (se andamento = false): em https://charneskiadvogados.novajus.com.br abra o processo pela pasta (campo pasta, ex.: RAUL-JUD-AO-01; se vazio, pelo número do processo) e confira no cabeçalho que número e partes batem. Se não baterem, não lance e registre a divergência. Senão: aba "Andamentos" → "Adicionar", tipo "Andamento", data de hoje, descrição exatamente igual a andamento_texto (ex.: "PEDRO - Novo Fluxo: Executor: Danieli, Revisor: Pedro."). Antes, veja se o mesmo texto já foi lançado hoje na pasta; se foi, não duplique. Não altere tarefas, responsáveis nem prazos.
4. Depois de cada passo concluído, marque o marcador correspondente como true: com ArtifactData (action "update", collection "atribuicoes", doc_id da atribuição, data {"programacao": true} etc., passando o if_version lido) ou, pela página no Chrome, tocando no botão "Programação", "Outlook" ou "Andamento L.O." do cartão.

Ao final, responda com um resumo: o que foi aplicado, o que falhou e por quê.
<<<FIM DO TEXTO 3>>>

4) DESATIVE a tarefa "Andamentos de fluxo no L.O." (ela procura um arquivo Atribuicoes_<data>.xlsx que não é mais gerado; a tarefa 3 substitui ela).

Não execute nenhuma das tarefas agora; só salve.
````
