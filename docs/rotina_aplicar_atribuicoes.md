# Tarefa "Aplicar atribuições do celular" (computador da rotina)

As atribuições feitas no celular, na página **Atribuição de Prazos**
(https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY), ficam guardadas na própria
página. O conector do Microsoft 365 desta conta só tem permissão de leitura,
então quem grava na Programação, no Outlook e no L.O. é esta tarefa, pelo
Claude in Chrome, no computador da rotina.

```text
Aplique no computador as atribuições de prazo feitas pelo celular.

FONTE: a página https://claude.ai/artifact/CepueKNa5EUT6FYxjoCyTY, coleção "atribuicoes". Leia-a com a ferramenta ArtifactData (action "list", collection "atribuicoes"). Se essa ferramenta não estiver disponível, abra a página no Chrome, vá na aba "Atribuídos" e leia os cartões marcados "Pendente no computador".
Cada atribuição traz: cliente, natureza, caso, providencia, prioridade, observacoes, processo, pasta, executor, revisor, lo, revisao, fatal (datas AAAA-MM-DD), andamento_texto e três marcadores: programacao, agenda, andamento (true = já feito).

Considere só as atribuições com algum marcador false. Mostre a lista e PEÇA CONFIRMAÇÃO antes de gravar qualquer coisa. Depois, para cada uma:

1. PROGRAMAÇÃO (se programacao = false): abra no Chrome, no Excel para a Web, https://charneskiadvogados.sharepoint.com/sites/CharneskiAdvogados_Drive2/Documentos%20Partilhados/JOBS/Programa%C3%A7%C3%A3o%202026.xlsx . Use a PRIMEIRA aba (semana corrente, padrão "W## ddmmaaaa"). Se já existir linha com o mesmo processo e o mesmo Fatal, não duplique — só marque como feito. Senão, insira uma linha na posição que mantém a ordem por "Prazo LO" (linhas "sine die" ou sem data ficam no fim) e preencha: Cliente, Natureza, Caso, Providência, Prazo LO, Revisão, Fatal (DD/MM/AAAA), Executor, Revisor, Prioridade, Status vazio, Observações. Na coluna Vencimento copie a fórmula da linha de cima (ajustando a linha). Confira que a linha ficou certa.
2. OUTLOOK (se agenda = false): no Outlook na Web (Chrome), crie dois compromissos de dia inteiro, marcados como "livre": "[Prazo LO] <cliente> - <providência> (<processo>)" na data lo e "[FATAL] <cliente> - <providência> (<processo>)" na data fatal, com executor, revisor e as três datas no corpo. Sem convidados.
3. ANDAMENTO NO L.O. (se andamento = false): em https://charneskiadvogados.novajus.com.br abra o processo pela pasta (campo pasta, ex.: RAUL-JUD-AO-01; se vazio, pelo número do processo) e confira no cabeçalho que número e partes batem. Se não baterem, não lance e registre a divergência. Senão: aba "Andamentos" → "Adicionar", tipo "Andamento", data de hoje, descrição exatamente igual a andamento_texto (ex.: "PEDRO - Novo Fluxo: Executor: Danieli, Revisor: Pedro."). Antes, veja se o mesmo texto já foi lançado hoje na pasta; se foi, não duplique. Não altere tarefas, responsáveis nem prazos.
4. Depois de cada passo concluído, marque o marcador correspondente como true: com ArtifactData (action "update", collection "atribuicoes", doc_id da atribuição, data {"programacao": true} etc., passando o if_version lido) ou, pela página no Chrome, tocando no botão "Programação", "Outlook" ou "Andamento L.O." do cartão.

Ao final, responda com um resumo: o que foi aplicado, o que falhou e por quê.
```
