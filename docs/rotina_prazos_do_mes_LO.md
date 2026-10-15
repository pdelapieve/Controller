# Rotina "Prazos do Mês no L.O." – texto atualizado

Cole o texto abaixo no lugar do prompt atual da tarefa agendada, no Claude
Desktop do computador onde ela roda (Tarefas agendadas → "Prazos do Mês no
L.O." → Editar). Mudanças em relação ao texto anterior:

- período: do dia 01 do mês corrente até **hoje + 60 dias** (antes: só o mês corrente);
- colunas separadas: `ID | Status | Vencimento | Responsável | Cliente | Processo | Pasta | Tipo | Tarefa`;
- coleta do **tipo/subtipo** da tarefa (distingue execução de revisão);
- o arquivo continua em `C:\Users\Betina\Downloads`, com o mesmo nome.

O app também lê o formato antigo (Cliente/Processo numa coluna só, sem ID),
mas aí a separação entre tarefa do executor e do revisor depende de a
palavra "revisão" aparecer na descrição.

---

```text
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
```
