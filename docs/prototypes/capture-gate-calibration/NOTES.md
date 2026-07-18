# Veredito

O modelo de janela é adequado como especificação inicial: gates estruturais passam
em todas as amostras, sinais ruidosos passam por proporção e a amostra mais recente
precisa estar boa. Isso preserva segurança sem fazer um outlier isolado reiniciar o
perfil na mão.

Os limiares permanecem `capture-gates-v1-unvalidated`. Eles não foram medidos em
aparelhos físicos nesta investigação e não devem ser descritos como calibrados. A
decisão durável é o contrato de sinais, a regra temporal, a separação dos perfis, a
telemetria local e o protocolo de promoção documentados no README.

O shell de terminal é descartável depois que a implementação real incorporar esse
contrato. Ele não deve ser enviado no app.
