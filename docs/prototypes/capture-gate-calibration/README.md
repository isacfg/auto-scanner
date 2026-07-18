# Protótipo descartável — calibração dos gates de captura

Este protótipo responde: **como combinar sinais de geometria, movimento, nitidez,
exposição e clipping ao longo do tempo, separando os perfis com suporte e na mão,
sem transformar números ainda não medidos em fatos?**

Ele não acessa a câmera e não implementa o app. Os cenários são sintéticos e servem
para inspecionar a regra de decisão. Os números em `CaptureGatePrototype.swift` são
`capture-gates-v1-unvalidated`: defaults iniciais seguros, versionados e ajustáveis,
que só podem ser promovidos para um aparelho após o protocolo abaixo.

Execute em um terminal:

```sh
./docs/prototypes/capture-gate-calibration/CaptureGatePrototype.swift
```

## Contrato dos sinais

Cada amostra de preview carrega:

- `rectangleConfidence`, em 0...1;
- `rectangleAreaRatio`, área do quadrilátero dividida pela área do preview;
- `cornerJitter`, RMS do deslocamento dos quatro cantos após compensar escala e
  translação, dividido pela diagonal do quadrilátero;
- `rotationRate`, norma de `CMDeviceMotion.rotationRate`, em rad/s;
- `userAcceleration`, norma de `userAcceleration`, em g;
- `sharpnessRatio`, variância do Laplaciano do interior retificado, na mesma
  resolução e luminância normalizadas, dividida pela referência nítida do par
  aparelho/formato;
- `shadowClipRatio` e `highlightClipRatio`, frações de pixels de luminância
  normalizada respectivamente abaixo de 0,01 e acima de 0,99;
- estados booleanos da câmera (`focusAdjusting`, `exposureAdjusting`) e
  `severeObstruction`, vindo da heurística conservadora de obstrução.

A referência de nitidez é o percentil 90 dos frames manualmente rotulados como
nítidos no corpus de calibração do mesmo aparelho, formato de análise e câmera.
Até existir essa referência, o app usa o default versionado e registra
`calibrationStatus = unvalidated`; não aprende silenciosamente durante uma sessão.

Reflexo, sombra moderada e exposição imperfeita continuam warnings. Somente clipping
ou obstrução graves são rígidos, pois as heurísticas não distinguem de forma
confiável todo brilho real de conteúdo claro da fotografia.

## Regra temporal

Uma janela contém apenas amostras contíguas do mesmo candidato, lado e tentativa.
Qualquer troca de identidade, pausa, indisponibilidade da câmera ou intervalo maior
que 150 ms limpa a janela.

`automaticReady` ocorre quando:

1. a janela cobre pelo menos a duração do perfil e contém a quantidade mínima de
   amostras;
2. geometria, câmera disponível, saída pronta, ausência de captura em voo,
   obstrução grave e clipping grave passam em **todas** as amostras;
3. ao menos a proporção configurada das amostras passa simultaneamente em
   movimento, nitidez e exposição estável; e
4. a amostra mais recente também passa em todos os gates.

Essa combinação evita que um único frame antigo bom dispare depois de uma piora e
tolera um outlier de sensor sem zerar continuamente uma sequência na mão. O melhor
frame de preview ajuda a avaliar nitidez, mas o Original continua vindo de
`AVCapturePhotoOutput`.

## Defaults `capture-gates-v1-unvalidated`

Estes valores **não são medições de aparelhos reais**. São pontos de partida
deliberadamente conservadores para executar o protocolo, nunca valores finais de
produto.

| Gate | Com suporte | Na mão |
| --- | ---: | ---: |
| Duração da janela | 400 ms | 700 ms |
| Amostras mínimas | 8 | 14 |
| Proporção simultânea aprovada | 90% | 80% |
| Confiança do retângulo mínima | 0,85 | 0,85 |
| Área mínima no preview | 30% | 30% |
| Jitter máximo (diagonal) | 0,30% | 0,80% |
| Rotação máxima | 0,04 rad/s | 0,18 rad/s |
| Aceleração máxima | 0,02 g | 0,07 g |
| Razão de nitidez mínima | 0,72 | 0,82 |
| Clipping grave, cada extremo | 1,0% | 1,0% |

O perfil na mão tolera mais movimento, mas exige maior nitidez relativa e uma janela
mais longa. Foco ou exposição sendo ajustados nunca contam como amostra aprovada.
Geometria, clipping grave e obstrução grave não são relaxados pelo modo.

## Telemetria local

O protótipo de aparelho deve gravar JSON Lines apenas no container local do app,
com exportação explícita pelo usuário e exclusão por sessão. Nenhum frame ou foto é
necessário para calibrar os limiares numéricos.

Cada linha inclui: versão do schema e do perfil; modelo do aparelho; câmera e
formato; modo; identidade anônima da sessão/candidato/tentativa; timestamp monotônico;
todos os sinais brutos e derivados; resultado por gate; estado agregado; latência
desde colocação; razão do disparo; warnings; e rótulo manual posterior (`boa`,
`desfocada`, `movida`, `clipping`, `obstruída`, `bordas erradas`, `bloqueio falso`).
Configurações promovidas são armazenadas por modelo de aparelho e formato de análise,
nunca por usuário, e sempre carregam versão, data, tamanho do corpus e métricas.

## Protocolo obrigatório nos aparelhos pessoais

Nenhum perfil deixa o estado `unvalidated` sem este protocolo:

1. Fixar aparelho, lente, formato/resolução de análise, orientação e versão do SO.
   Desativar troca automática de lente durante a rodada.
2. Montar corpus de pelo menos 60 fotografias por aparelho: tamanhos, acabamentos,
   bordas claras/escuras, baixo contraste, desgaste e conteúdo naturalmente claro
   ou escuro. Usar ao menos três fundos e quatro condições de luz, incluindo uma
   condição deliberadamente ruim.
3. Para cada modo, registrar no mínimo 120 tentativas independentes, cobrindo
   sucessos normais e desafios intencionais de movimento, desfoque, clipping,
   reflexo, sombra, mão sobre a foto e borda parcialmente ausente. Separar 30% das
   fotografias antes do ajuste como conjunto final, sem reutilizá-las na escolha de
   limiares.
4. Rotular o still em resolução total sem olhar o resultado dos gates. Dois passes
   do proprietário em ordem aleatória; divergências são revistas uma vez. “Aceita”
   exige bordas corretas, texto/conteúdo legível quando presente, ausência de borrão
   visível em 100% e nenhuma perda grave por clipping ou obstrução.
5. Ajustar um gate por vez no conjunto de ajuste. Prioridade: zero aceites com falha
   grave; depois reduzir bloqueios falsos. Não otimizar apenas tempo médio.
6. Aprovar **com suporte** somente se nenhuma falha grave for aceita, pelo menos 95%
   das tentativas boas dispararem automaticamente, mediana desde colocação até
   disparo for no máximo 3 s e percentil 90 no máximo 5 s.
7. Aprovar **na mão** somente se nenhuma falha grave for aceita, pelo menos 90% das
   tentativas boas dispararem automaticamente e o percentil 90 for no máximo 8 s.
   A meta de 3–5 s não é imposta a esse perfil.
8. Rodar uma única vez o conjunto final congelado. Qualquer falha grave aceita
   reprova o perfil. Se uma meta falhar, registrar o motivo e manter
   `unvalidated`; não aliviar gates estruturais para obter velocidade.
9. Publicar a configuração como nova versão imutável, com métricas e identificação
   do aparelho/formato. Repetir o conjunto final após mudança de aparelho, lente,
   resolução da análise, algoritmo do sinal ou versão principal do SO.

O disparo manual de exceção continua seguindo a máquina de estados já decidida: pode
relaxar qualidade elegível, mas nunca disponibilidade, quadrilátero capturável,
movimento seguro, clipping/obstrução graves, retirada ou exclusão mútua.
