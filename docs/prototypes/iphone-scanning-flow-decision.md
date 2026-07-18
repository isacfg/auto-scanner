# Decisão do fluxo de digitalização no iPhone

Decisão produzida por [Prototipar o fluxo de digitalização no iPhone](https://github.com/isacfg/auto-scanner/issues/4). O [protótipo descartável](../../prototypes/iphone-scanning-flow/) compara três alternativas e não deve ser promovido a código de produção.

## Escolha

Adotar o **guia central contextual** da variante A. A interface mantém o preview quase inteiro, sobrepõe uma instrução principal curta na região inferior e usa a moldura da fotografia como indicador contínuo de prontidão. Aproveitar da variante B apenas um diagnóstico curto do gate que ainda impede a captura; não manter a coluna permanente de indicadores.

As alternativas foram avaliadas em viewport de iPhone:

- **A — Guia central:** melhor equilíbrio entre enquadramento, estado e próxima ação; vence.
- **B — HUD periférico:** parece rápida, mas espalha atenção, reduz a compreensão do verso e torna gates simultâneos ruidosos.
- **C — Próxima ação:** é a mais didática, porém o cartão ocupa câmera demais e transforma um ciclo repetitivo em uma sequência pesada.

## Contrato de interface

### Hierarquia persistente

1. Preview da câmera e moldura do quadrilátero dominam a tela.
2. Contador da sessão fica no topo, junto de pausa e ações secundárias.
3. Seletor **Com suporte / Na mão** fica visível, mas não interrompe o ciclo. Trocar o modo limpa prontidão acumulada e reavalia os gates.
4. Um painel inferior mostra apenas:
   - estado atual em até uma linha;
   - próxima ação física em até duas linhas;
   - controle de Verso da sessão;
   - ação excepcional, somente quando elegível.

### Feedback visual

- Moldura neutra: fotografia detectada, ainda em avaliação.
- Moldura verde com breve preenchimento progressivo: gates rígidos prontos e captura iminente. Não usar contagem regressiva numérica, pois prontidão pode regredir.
- Moldura âmbar e um diagnóstico acionável: espera prolongada por qualidade, por exemplo “Incline para reduzir o reflexo” ou “Segure mais firme”. Mostrar somente o gate prioritário; detalhes ficam em uma ação secundária.
- Flash discreto do thumbnail e banner curto “Frente capturada” ou “Verso capturado” apenas depois da confirmação atômica do lado, nunca no início de `capturePhoto`.
- Ao exigir retirada ou giro, substituir o texto por uma instrução imperativa e alterar a moldura para tracejada. Nenhuma nova captura fica armada até o latch físico ser satisfeito.

### Feedback sonoro e háptico

- Lado confirmado: um som curto, suave e distinto de obturador, acompanhado de uma háptica única firme. O par significa **ativo confirmado**, não apenas disparado.
- Photograph concluída: não emitir um segundo som se a Frente também concluir a Photograph; o contador e o thumbnail bastam. Quando há Verso, a confirmação do Verso já cumpre esse papel.
- Erro de confirmação/persistência: duas pulsações hápticas curtas e mensagem persistente; nenhum som de sucesso.
- Prontidão, warnings, retirada e troca de lado não produzem som. Isso evita fadiga numa sessão longa.
- Som respeita modo silencioso e preferência do sistema. Háptica pode ser desativada nas preferências; com ambos indisponíveis, o banner e o thumbnail continuam suficientes.

### Com suporte e na mão

Os modos compartilham estados, textos e sinais. Só mudam o perfil de gates e o diagnóstico mostrado:

- **Com suporte:** instrução inicial “Posicione a frente”; prioriza alinhamento e retirada da mão do quadro.
- **Na mão:** instrução inicial “Enquadre e segure”; comunica movimento e nitidez antes de outros warnings.

Não criar fluxos, telas ou cores diferentes por modo.

### Verso opcional

- O toggle “Capturar verso” é de sessão, desligado por padrão e permanece no painel inferior.
- Quando a Frente começa a captura, o valor aplicável à Photograph é congelado. Alterar o toggle depois afeta apenas a próxima Photograph e a interface deve dizer isso.
- Com Verso ligado, após confirmar a Frente a única instrução primária é “Retire e vire a mesma fotografia”. Depois da ausência estável, muda para “Posicione o verso”.
- Nesse intervalo ficam disponíveis **Pular verso** e, após ambos os lados confirmados, **Trocar lados** nas ações secundárias.

### Captura manual de exceção

- A ação não aparece inicialmente. Após espera contínua no mesmo `evaluating(side)`, mostrar “Capturar com avisos” abaixo do diagnóstico do gate.
- O primeiro toque abre uma confirmação compacta: “Aceitar reflexo/nitidez abaixo do ideal?”. O segundo confirma a solicitação; não usar um botão de obturador permanente.
- A ação relaxa somente warnings de qualidade elegíveis e entra no mesmo `capturing(side)` automático.
- Se não houver quadrilátero capturável, a câmera estiver indisponível, houver movimento inseguro, falha estrutural grave, captura em voo ou latch pendente, manter a ação desabilitada e explicar o requisito. Nunca aparentar que o toque foi aceito.

## Critérios de aceitação para implementação

- Sem ler instruções anteriores, a pessoa identifica em até um olhar o estado, a próxima ação física e se a captura será automática.
- A confirmação sensorial ocorre somente depois de Original, Master, warnings e metadados terem sido aceitos localmente.
- Uma pessoa pode percorrer Frente → retirar → Verso → retirar sem botão de captura e sem risco visual de associar lados incorretamente.
- O fallback manual só aparece após espera e comunica o warning aceito; não vira caminho principal nem ignora guardas estruturais.
- O fluxo permanece compreensível com som desligado, háptica desligada ou ambos.
- Dynamic Type, VoiceOver e Reduce Motion preservam estado e próxima ação; cor nunca é o único sinal.

## Lacuna deliberada

Este protótipo valida hierarquia e semântica do feedback, não calibra duração, limiares, intensidade háptica ou detectores. Esses valores exigem aparelho real e pertencem a [Calibrar os gates de captura em aparelhos reais](https://github.com/isacfg/auto-scanner/issues/11).
