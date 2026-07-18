# PROTÓTIPO DESCARTÁVEL — biblioteca e restauração no Mac

Pergunta: qual interface permite navegar por sessões, revisar frente e verso, corrigir Masters, selecionar lotes, confirmar custo, acompanhar a fila, comparar antes e depois e exportar com clareza no Mac?

Três variantes estruturalmente diferentes estão na mesma página por `?variant=A`, `?variant=B` e `?variant=C`. Todo o estado é fictício e vive apenas em memória; não há persistência, upload, cobrança ou exportação real.

## Executar

```sh
python3 -m http.server 4174 --directory prototypes/mac-library-restoration
```

Abra `http://localhost:4174/?variant=A`. Use as setas do seletor inferior ou do teclado para alternar variantes.

## Roteiro de avaliação

1. Troque de sessão e selecione fotografias na biblioteca.
2. Abra uma fotografia e alterne entre Frente e Verso.
3. Entre em **Corrigir Master**, altere a geometria simulada e salve uma nova revisão.
4. Ative **Selecionar lote**, escolha fotografias e avance até a confirmação de custo.
5. Confirme o lote e acompanhe tentativas independentes na fila.
6. Abra **Antes e depois** numa restauração concluída e mova o divisor.
7. Exporte uma seleção, escolhendo Frente ou Frente e Verso e a rendition da Frente.
8. Compare qual variante mantém contexto e deixa claro quando uma ação cria custo ou congela arquivos.

Este protótipo deve ser apagado depois que sua decisão for absorvida numa implementação. Ele não é base de código de produção.
