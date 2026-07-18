# Protótipo descartável — fluxo de digitalização no iPhone

Pergunta: qual interface e combinação de feedback visual, sonoro e háptico tornam o fluxo sem botão compreensível e rápido nos modos com suporte e na mão, incluindo verso opcional e fallback manual?

Três variantes estruturalmente diferentes estão disponíveis na mesma página por `?variant=A`, `?variant=B` e `?variant=C`. O protótipo usa apenas estado em memória e não acessa câmera nem persiste fotografias.

## Executar

```sh
python3 -m http.server 4173 --directory prototypes/iphone-scanning-flow
```

Abra `http://localhost:4173/?variant=A`. Use as setas do seletor inferior ou do teclado para alternar variantes.

## Roteiro de avaliação

1. Alterne entre **Com suporte** e **Na mão**.
2. Ative **Capturar verso**, inicie a simulação e percorra Frente → retirar → Verso.
3. Em **Aguardando qualidade**, espere o fallback manual aparecer ou use **Mostrar fallback**.
4. Confirme que o disparo manual comunica que aceita avisos, mas ainda exige enquadramento e segurança.
5. Compare se o estado atual, a próxima ação física e a confirmação da captura são percebidos sem leitura demorada.

Este código deve ser apagado após a decisão ser registrada no ticket; não é base de implementação.
