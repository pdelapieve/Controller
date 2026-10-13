# Tarefa "Atribuir prazos" (computador da rotina, interativa)

Rodada manualmente no Claude Desktop do computador da rotina. Faz numa
conversa o mesmo que a página do celular, e já grava na Programação, no
Outlook e no L.O. Usa o mesmo registro de atribuições da página
**Atribuição de Prazos** (https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY),
então o que foi atribuído num lugar não reaparece no outro.

```text
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
```
