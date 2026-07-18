# Decisão da biblioteca e restauração no Mac

Decisão produzida por [Prototipar a biblioteca e restauração no Mac](https://github.com/isacfg/auto-scanner/issues/9). O [protótipo descartável](../../prototypes/mac-library-restoration/) compara três alternativas e não deve ser promovido a código de produção.

## Escolha

Adotar a **biblioteca com inspetor persistente** da variante A. Ela mantém sessões, seleção e estado global à esquerda; fotografias no centro; e o contexto da fotografia, Frente/Verso, correção, comparação e fila à direita. É a única alternativa em que todas as tarefas podem ser encadeadas sem perder a seleção ou transformar o produto numa sequência rígida.

Incorporar duas ideias das outras variantes sem adotar suas estruturas: os nomes explícitos das etapas da variante B dentro de modais/estados transitórios e a cronologia por fotografia da variante C dentro do inspetor.

- **A — Biblioteca + inspetor:** melhor densidade, contexto e liberdade de navegação; vence.
- **B — Fluxo por etapas:** comunica bem o processo, mas impõe ordem onde revisão, fila e exportação precisam coexistir.
- **C — Fotografia + histórico:** excelente para investigação individual, mas oculta sessões, lote e fila global cedo demais.

## Avaliação substituta

O avaliador percorreu no protótipo: troca de sessão; seleção de fotografias; Frente/Verso; criação simulada de nova revisão de Master; lote e confirmação de custo; fila com cancelamento independente; divisor Antes/Depois; e configuração de exportação. A variante A preservou contexto em todas as transições. Nenhuma ação simulada realizou upload, cobrança, persistência ou escrita de arquivo.

## Contrato de interface

### Sessões e biblioteca

- A barra lateral lista **Todas** e Capture Sessions em ordem recente, com contagens, além de atalhos para Fila e itens que precisam de atenção.
- A grade central mantém a ordem visível da sessão e mostra, sem depender de cor, presença de Verso, sincronização e seleção.
- Abrir uma Photograph não altera seleção de lote. Seleção é um modo explícito, com contagem, limpar e ação “Restaurar seleção…”.

### Frente, Verso e correção

- O inspetor alterna Frente e Verso da mesma Photograph sem navegar para outra tela. Verso ausente é mostrado como estado, não como imagem vazia.
- “Corrigir Master…” abre um editor focado de crop, rotação e perspectiva. Salvar declara que cria um novo Master do mesmo Original; nunca sugere sobrescrita.
- Ao salvar, a grade e o inspetor passam atomicamente ao novo Master. O anterior e suas Restorations continuam acessíveis na cronologia.

### Lote, custo e consentimento

- Apenas current Front Masters elegíveis entram na seleção; exclusões aparecem com motivo.
- Selecionar nunca inicia trabalho remoto. “Restaurar seleção…” abre a confirmação com provedor, quantidade, estimativas por item e total em USD, validade, preset e aviso de nuvem.
- Mudança de elegibilidade ou expiração exige recalcular e confirmar novamente. Somente a confirmação cria o Restoration Batch durável e suas Attempts em `queued`.

### Fila e histórico

- A fila global permanece visível no inspetor e tem uma visão completa pelo atalho lateral. A ordem é FIFO; apenas uma tentativa ativa é apresentada por vez.
- Cada linha representa uma Restoration Attempt e expõe estado, fotografia, custo estimado/real quando conhecido e apenas comandos válidos. Falha, cancelamento ou atenção necessária em uma tentativa não bloqueiam as demais.
- O histórico por fotografia mostra todas as Attempts, inclusive falhas, cancelamentos e retries, sem chamar uma Restoration de “mais recente” ou “melhor”.

### Antes e depois

- “Antes e depois” abre uma comparação grande com divisor, identificando explicitamente o Master fonte exato e a Restoration escolhida.
- Metadados essenciais ficam visíveis: provedor, versão imutável do modelo, preset, data e custo real ou desconhecido.
- Comparar não muda o current Master nem escolhe automaticamente uma Export Rendition.

### Exportação

- “Exportar…” é independente da restauração e abre uma revisão final da seleção congelável.
- Para cada Photograph, a pessoa escolhe Frente somente ou Frente e Verso e escolhe explicitamente o current Front Master ou uma Restoration elegível. O default é o Master.
- Falta de Back Master é resolvida antes da escrita por excluir a Photograph ou mudar para Frente somente.
- A confirmação resume quantidade de imagens, renditions e destino; depois congela UUIDs/digests e inicia a criação atômica do Export Package. Nunca sobrescreve pacote existente nem apresenta arquivo parcial como sucesso.

## Critérios de aceitação para implementação

- É possível navegar entre sessões e fotografias sem perder seleção de lote ou esconder fila ativa.
- Frente, Verso, Master corrente e linhagem histórica nunca são confundidos por rótulos ou posição.
- Nenhum upload ou custo ocorre antes de confirmação válida e explícita.
- A fila representa Attempts independentes e continua compreensível após falha, cancelamento, reinício ou `submissionUnknown`.
- Antes/Depois sempre identifica o Master fonte exato.
- Exportação exige escolha explícita de lados e rendition, identifica inelegibilidade antes de escrever e reflete o contrato de pacote atômico.
- VoiceOver, navegação por teclado, contraste e Dynamic Type preservam seleção, estado, custo e ações; cor não é o único indicador.

## Limite do protótipo

O protótipo valida arquitetura de informação e sequência de decisões. Não valida SwiftUI, desempenho com bibliotecas grandes, edição geométrica real, chamadas Replicate, sincronização CloudKit ou escrita no Finder; esses pontos pertencem à implementação futura e não autorizam reutilizar o código descartável.
