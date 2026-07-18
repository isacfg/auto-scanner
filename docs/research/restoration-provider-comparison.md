# Provedor de restauração para o MVP pessoal

Pesquisa concluída em 18 de julho de 2026. O objetivo é escolher um único preset inicial para restaurar o `Front Master` no app nativo para Mac, sem backend comercial e sem alterar o `Original` ou o `Master`.

## Decisão

Usar **Replicate** com **CodeFormer**, fixado na versão:

```text
sczhou/codeformer:cc4956dd26fa5a7185d5660cc9100fab1b8070a1d1654a8bb5eb6d443b020bb2
```

Preset inicial:

```json
{
  "codeformer_fidelity": 0.7,
  "background_enhance": true,
  "face_upsample": true,
  "upscale": 2
}
```

O valor `0.7` favorece a preservação da identidade em relação ao default `0.5`, sem ir ao extremo `1.0`, que tende a conservar também mais degradação. Esse é um ponto inicial a validar com fotografias reais; não é um resultado de benchmark próprio. O preset não coloriza automaticamente e sempre produz uma `Restoration` derivada.

## Comparação

| Critério | fal.ai | Replicate | Consequência para o MVP |
|---|---|---|---|
| Fidelidade | O endpoint dedicado `fal-ai/image-editing/photo-restoration` é generativo, pode remover imperfeições e adicionar cor, mas não expõe um controle de identidade. A fal também oferece CodeFormer com controle de fidelidade de `0.0` a `1.0`. | CodeFormer expõe `codeformer_fidelity` de `0.0` a `1.0`; valores maiores priorizam identidade. | CodeFormer é mais previsível que o endpoint generativo. Entre os dois hosts do mesmo modelo, a versão imutável da Replicate desempata. |
| Resolução | Photo Restoration escolhe `aspect_ratio`, mas sua página não documenta dimensões de saída. CodeFormer usa 2× por padrão e saída PNG. | CodeFormer oferece `upscale` inteiro e 2× por padrão, com `background_enhance` e `face_upsample`. | O preset 2× tem contrato claro. O app deve guardar as dimensões reais retornadas, sem prometer recuperação de detalhe inexistente. |
| Preço publicado | Photo Restoration: **US$ 0,04/imagem**. CodeFormer: **US$ 0,0021 por megapixel**; portanto uma entrada de 12 MP custa aproximadamente US$ 0,0252. | CodeFormer: aproximadamente **US$ 0,0028/execução**, variando conforme a entrada e o tempo de execução. | Replicate é substancialmente mais barata para masters de câmera com muitos megapixels. Preços devem ser lidos novamente antes da implementação. |
| Latência | A documentação do endpoint não publica uma latência típica verificável. A fila informa `queue_position` e, ao concluir, `metrics.inference_time`. | A página atual do CodeFormer informa conclusão típica em cerca de **3 s**; a resposta expõe `predict_time` e `total_time`. Cold start/fila podem aumentar o total. | Replicate oferece uma expectativa inicial mais útil, mas a UI deve tratar a operação como assíncrona. |
| Polling | A queue API retorna `request_id`, `status_url`, `response_url` e `cancel_url`; estados `IN_QUEUE`, `IN_PROGRESS` e `COMPLETED`. Também há SSE e webhook. | A criação retorna um prediction com `id` e `urls.get`; o app pode fazer `GET` até `succeeded`, `failed` ou `canceled`. Também há webhook. | Para um Mac sem servidor público, polling é a integração direta mais simples nos dois casos. Persistir o ID remoto permite retomar após reinício. |
| Cancelamento | `PUT` no `cancel_url`. Remove imediatamente se ainda estiver na fila; em processamento retorna `CANCELLATION_REQUESTED`, mas o modelo pode terminar se o runner não cooperar. | `POST /v1/predictions/{id}/cancel`, com estado terminal `canceled`; também aceita `Cancel-After` de 5 s a 24 h. | Replicate tem contrato terminal e deadline mais claro. Cancelar localmente não deve ser interpretado como garantia de custo zero. |
| Retenção | Por padrão guarda entradas e saídas. `X-Fal-Store-IO: 0` evita guardar payloads, mas arquivos enviados/gerados no CDN continuam sujeitos ao ciclo de vida de mídia e são publicamente acessíveis enquanto válidos. Há API para apagar payloads e arquivos de saída. | Predições criadas pela API têm inputs, outputs, arquivos e logs apagados automaticamente após **1 hora**, por padrão; as feitas pela interface web ficam indefinidamente. | Replicate tem default melhor para fotos pessoais. Baixar imediatamente para o armazenamento local/iCloud e nunca usar o playground com fotos reais. |
| Privacidade | Os termos dizem que conteúdo do cliente não é usado para treinar produtos/serviços, salvo modelos marcados como não prontos para enterprise, e alertam que modelos de terceiros podem receber o conteúdo. | A política trata a Replicate como processador/service provider em usos de cliente; a retenção curta da API reduz exposição, mas a foto ainda é processada na nuvem. | Nenhuma opção é local ou adequada a uma promessa de “foto nunca sai do dispositivo”. Exigir consentimento explícito antes do primeiro envio e registrar provedor/modelo/data/custo. |
| Integração direta no Mac | REST funciona, e uma chave de escopo `API` é menos privilegiada que `ADMIN`. A documentação recomenda proxy para aplicações cliente e alerta contra expor a chave. | REST usa bearer token e funciona em qualquer linguagem. A versão completa é obrigatória para modelos comunitários. | No MVP pessoal e de distribuição privada, guardar o token no Keychain e adicioná-lo apenas em memória ao header é aceitável. Não embutir segredo no bundle, logs, UserDefaults ou CloudKit. Para distribuição a terceiros, introduzir backend/proxy antes de ampliar o escopo. |
| Versionamento | Os endpoints públicos são identificados por slug; as páginas consultadas não documentam um digest imutável selecionável pelo chamador para `fal-ai/codeformer` ou Photo Restoration. A própria fal reserva o direito de atualizar materiais/serviços. | Modelos comunitários aceitam e exigem um ID completo de versão de 64 caracteres. `cc4956…` está marcado como a versão atual do CodeFormer. | A Replicate satisfaz diretamente o requisito do produto de registrar versão e torna o preset reproduzível. |

## Por que não escolher o endpoint Photo Restoration da fal

Ele é atraente como operação única e provavelmente corrige danos mais amplos que um restaurador facial. Porém, a própria descrição inclui colorização e sua API oferece `guidance_scale`, passos, seed e razão de aspecto: sinais de uma reconstrução generativa, não de uma transformação conservadora. Para fotografias familiares, inventar cor, textura ou traços sem um controle explícito de identidade é um risco maior que deixar parte do dano intacta. Ele também custa cerca de 14 vezes a execução típica publicada do CodeFormer na Replicate e não oferece pinning de versão documentado.

O CodeFormer também tem limite importante: é principalmente restauração facial. `background_enhance` usa Real-ESRGAN para o restante da imagem, mas não reconstrói de forma semanticamente confiável rasgos grandes ou áreas ausentes. Isso é aceitável para o preset inicial porque favorece fidelidade e reversibilidade. Se a validação com o acervo real mostrar que danos físicos amplos são o caso dominante, deve-se abrir uma decisão separada para um segundo preset generativo; não ampliar silenciosamente este preset.

## Contrato de integração recomendado

1. Ler o token Replicate do Keychain somente ao criar a requisição; nunca sincronizá-lo por iCloud/CloudKit.
2. Enviar o `Front Master` diretamente por HTTPS para uma prediction assíncrona usando exatamente o digest e os quatro parâmetros acima.
3. Persistir `prediction.id`, digest, preset, estado, data e custo estimado junto ao registro local da restauração.
4. Fazer polling por `urls.get` com backoff enquanto o app estiver ativo; ao reabrir, retomar pelo mesmo ID.
5. Ao cancelar, chamar `urls.cancel` e continuar consultando até um estado terminal. Um cancelamento solicitado não deve apagar o registro nem presumir reembolso.
6. Em `succeeded`, baixar o PNG imediatamente, validar MIME/dimensões, gravá-lo como nova `Restoration` e então permitir que a cópia remota expire após uma hora.
7. Exibir antes do primeiro uso que o Front Master será enviado à Replicate para processamento em nuvem. Não enviar o `Back` por padrão.

## Evidência e limitações

Não foi executada inferência paga: o repositório não fornece chaves fal/Replicate, e as consultas públicas de metadados das duas APIs responderam que autenticação era necessária. Portanto, qualidade visual e latência não foram medidas com o acervo do usuário. A recomendação usa contratos e métricas atuais publicados pelos provedores e deve passar por uma validação visual posterior com um conjunto pequeno, representativo e autorizado de fotos.

Fontes primárias consultadas:

- fal: [Photo Restoration e preço](https://fal.ai/models/fal-ai/image-editing/photo-restoration), [CodeFormer, fidelidade, resolução e preço](https://fal.ai/models/fal-ai/codeformer), [fila, polling e cancelamento](https://fal.ai/docs/documentation/model-apis/inference/queue), [retenção de dados](https://fal.ai/docs/documentation/model-apis/inference/payloads), [autenticação e escopos](https://fal.ai/docs/documentation/setting-up/authentication), [termos da API e uso de conteúdo](https://fal.ai/legal/api-services), [privacidade](https://fal.ai/legal/privacy-policy).
- Replicate: [CodeFormer e custo/latência](https://replicate.com/sczhou/codeformer), [versão fixada](https://replicate.com/sczhou/codeformer/versions/cc4956dd26fa5a7185d5660cc9100fab1b8070a1d1654a8bb5eb6d443b020bb2), [criação, polling e deadlines](https://replicate.com/docs/topics/predictions/create-a-prediction), [HTTP API e cancelamento](https://replicate.com/docs/reference/http/), [retenção de dados](https://replicate.com/docs/topics/predictions/data-retention/), [política de privacidade](https://replicate.com/privacy).

