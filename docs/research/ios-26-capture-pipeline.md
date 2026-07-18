# Pipeline de captura automática no iOS 26

Pesquisa para [Validar a pipeline de captura no iOS 26](https://github.com/isacfg/auto-scanner/issues/2).

## Decisão

O MVP deve usar uma sessão de captura própria baseada em AVFoundation. A mesma sessão fornece frames de preview para análise em tempo real e uma saída de fotografia para o arquivo Original em resolução total.

O `VNDocumentCameraViewController` não deve ser usado: ele apresenta uma interface pronta orientada a páginas e exige que a pessoa toque na câmera e depois salve ou cancele. Isso contradiz a captura contínua e sem botão do Auto Scanner.

## Componentes da pipeline

1. `AVCaptureSession` com câmera traseira grande-angular, `AVCaptureVideoDataOutput`, `AVCapturePhotoOutput` e `AVCaptureVideoPreviewLayer`.
2. Frames de análise em YCbCr, descartando atrasados, numa fila serial fora da main thread.
3. `Vision.DetectRectanglesRequest` para adquirir um único quadrilátero dominante, restringindo tamanho, proporção, confiança e tolerância angular ao domínio de fotos impressas.
4. `Vision.TrackRectangleRequest` entre novas detecções para acompanhar os quatro cantos com menor custo. Refazer a detecção periodicamente e sempre que a confiança cair.
5. `CMDeviceMotion` para medir `rotationRate` e `userAcceleration`, combinado com o deslocamento dos quatro cantos entre frames. Nenhum dos dois sinais isoladamente é suficiente.
6. Estado de foco e exposição do `AVCaptureDevice`, mais métricas de pixels do interior do quadrilátero.
7. `AVCapturePhotoOutput.capturePhoto` somente quando os gates rígidos passarem e `captureReadiness` permitir resposta rápida. Começar com `photoQualityPrioritization = .balanced` para perseguir a meta de 3–5 segundos sem sacrificar o Original pela configuração `.speed`.
8. Detectar novamente os quatro cantos no still de resolução total. Gerar o Master com `CIPerspectiveCorrection`; não reutilizar cegamente coordenadas do preview, pois crop, orientação e resolução podem diferir.

## Gates de captura

### Rígidos

- um quadrilátero dominante está presente, com confiança e área mínimas;
- os cantos permanecem dentro da janela de estabilidade por vários frames;
- movimento óptico e movimento do aparelho permanecem abaixo dos limiares do modo atual;
- câmera não está ajustando foco ou exposição;
- nitidez relativa supera o piso calibrado para o aparelho e a escala analisada;
- saída de foto está pronta;
- não há clipping ou obstrução classificada como grave.

Falha em gate rígido mantém a câmera aguardando. Após o tempo definido pela futura máquina de estados, aparece o disparo manual de exceção; ele não deve ignorar uma câmera indisponível, mas pode aceitar warnings de qualidade.

### Warnings

- reflexo moderado;
- sombra moderada;
- exposição imperfeita sem perda grave de detalhe;
- nitidez aceitável, mas abaixo do alvo preferencial.

Warnings não bloqueiam a captura. Eles acompanham a Photograph para revisão no iPhone e no Mac.

## Nitidez e melhor frame

A Apple publica uma implementação de referência que usa variância do Laplaciano com Accelerate/vImage e vDSP para ordenar uma sequência pela nitidez. O Auto Scanner deve aplicar essa métrica a previews reduzidos e normalizados, usando uma pequena janela móvel para validar estabilidade e escolher o melhor candidato de análise.

O Original deve vir de `AVCapturePhotoOutput`, não de um frame reduzido do preview. Se testes mostrarem que uma única captura still perde o instante mais nítido no modo na mão, a solução deve ser avaliada no protótipo com captura responsiva ou bracket suportado pelo aparelho; não antecipar uma rajada permanente no MVP.

## Reflexo, sombra e obstrução

Não há, nas APIs públicas encontradas, um detector genérico de reflexo em fotografia impressa. Implementar um score próprio apenas dentro do quadrilátero, combinando:

- proporção e agrupamento espacial de pixels próximos da saturação;
- baixa cromaticidade nas regiões muito claras;
- perda local de textura;
- histogramas de luminância;
- persistência ou deslocamento do highlight em frames consecutivos.

Esse score deve produzir warning ou falha grave somente em extremos calibrados. Ele não pode prometer detectar todo reflexo, especialmente quando o brilho encobre uma área clara da própria fotografia. Sombra e possível mão/obstrução também exigem heurísticas ou um modelo local futuro; no MVP, devem seguir a mesma política conservadora.

## Modos de captura

Os dois modos usam a mesma pipeline e estados, mas perfis de calibração diferentes:

- **Com suporte:** dá maior peso à estabilidade dos cantos e pode exigir uma janela curta e rigorosa. Core Motion confirma que o telefone continua parado.
- **Na mão:** combina Core Motion com rastreamento óptico, tolera micro movimento e exige nitidez confirmada antes do disparo. A janela pode ser maior.

Os limiares numéricos não devem ser inventados na especificação. Devem ser medidos no protótipo em aparelhos reais, com telemetria local dos sinais e um conjunto representativo de fotos, fundos e iluminação.

## Garantias realistas

- É realista detectar e acompanhar uma foto retangular isolada sobre fundo contrastante, esperar estabilidade, capturar em resolução total e produzir um recorte com perspectiva corrigida.
- É realista bloquear movimento/foco claramente ruins e sinalizar exposição, sombra ou brilho suspeitos.
- Não é realista garantir bordas perfeitas em foto sem contraste com o fundo, nem detectar todo reflexo ou dano usando apenas APIs nativas.
- A meta de uma foto a cada 3–5 segundos com suporte é plausível, mas só vira critério confirmado depois de medições no protótipo e nos aparelhos pessoais alvo.

## Fontes primárias

- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [Photo quality prioritization](https://developer.apple.com/documentation/avfoundation/avcapturephotosettings/photoqualityprioritization)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [DetectRectanglesRequest](https://developer.apple.com/documentation/vision/detectrectanglesrequest)
- [TrackRectangleRequest](https://developer.apple.com/documentation/vision/trackrectanglerequest)
- [Tracking multiple objects or rectangles in video](https://developer.apple.com/documentation/vision/tracking-multiple-objects-or-rectangles-in-video)
- [CIPerspectiveCorrection](https://developer.apple.com/documentation/coreimage/ciperspectivecorrection)
- [Capture-device focus](https://developer.apple.com/documentation/avfoundation/capture-device-focus)
- [Capture-device exposure](https://developer.apple.com/documentation/avfoundation/capture-device-exposure)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [Finding the sharpest image in a sequence](https://developer.apple.com/documentation/accelerate/finding-the-sharpest-image-in-a-sequence-of-captured-images)
- [VNDocumentCameraViewController](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)

