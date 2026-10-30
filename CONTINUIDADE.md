# Continuidade — 30/10/2026

Marconi determinou: “o banco de voz deve ser um projeto commitado no github para estar presente e ser atualizado ao mesmo tempo em todas as maquinas.”

## Publicado e configurado

Repositório independente e privado: https://github.com/MarconiTeles/banco-de-vozes, branch `main`. Publicação e privacidade verificadas pela CLI do GitHub. Código validado no commit `0f6f795d86cf06ac2507b9fa3893e134a57f57e6`; documentação posterior também segue por commit/push.

Samples portáteis: original integral `VOICE MANU.mp3` em `sources`, SHA `d2f4316f0367d668d8f03ac1cc5cf5782bccd7ef450cdda8fa4a5431b3875e20`; referência WAV 10,95 s em `references`, SHA `daf5927fa4a5ffb8d301e0f30d2a55e01e1adc2c67832912ff02d9eeef1e6ccf`. Fichas `manu-v1`, `manu-indignada-v1` (histórica) e `manu-indignada-v2` (direção enxuta). Nenhum peso/runtime/credencial foi adicionado ao Git. WIP do motor `Compartilhados/drama-voice` foi preservado sem commit de trabalho alheio.

Mac: checkout `Compartilhados/banco-de-vozes`, cadastrado no T3 com autoPull ativo. `~/.local/bin/drama-voice` aponta ao launcher versionado; ligação anterior preservada em `~/.local/bin/drama-voice.before-voice-bank`. LaunchAgent novo `com.minimal.voice-bank-sync`, por minuto, executou com exit 0 e recibo em `.state/receipt.json`; os três perfis instalados coincidem por hash. O comando `drama-voice voices` foi executado pelo novo launcher com sucesso. Geração, pesos e arquivo externo continuam nos locais autorizados do Drama.

Windows: clone concluído pelo T3 em `C:\Users\MarconiReis\Projects\MacBook\banco-de-vozes`, projeto “Banco de vozes”, autoPull ativo confirmado por releitura das configurações. Launcher portátil `drama-voice.cmd` sincroniza, descobre o motor nativo e importa as referências no primeiro uso. Scripts de sincronizar/importar e conferir referências estão no projeto T3. O motor antigo não foi sobrescrito.

Limite de prova Windows: não houve execução do importador nem leitura do SHA do checkout após os pushes posteriores. O canal administrativo de comandos `127.0.0.1:13775` retornou `UND_ERR_HEADERS_TIMEOUT`; não foi reiniciado nem alterado. Clonagem, cadastro e autoPull pelo T3 funcionaram. Não apresentar essas confirmações como prova de geração Windows ou paridade observada do último SHA. O sincronismo antes do uso está no launcher versionado; checkout alterado, diver­gência ou falha de rede são explícitos, sem reset/clean/stash.

## Verificação do banco

Cinco testes locais passaram: hash adulterado recusado; caminhos externos recusados; ficha conflitante preservada; Git real com avanço rápido e recusa de WIP/commits não publicados; importação mantém bytes exatos do WAV sem recodificação. Mac/origin e recibo do sincronizador estavam no mesmo SHA `0f6f795d86cf06ac2507b9fa3893e134a57f57e6` antes desta documentação.

## Direção e tentativas do voiceover

Correção literal de Marconi: “a pronuncia de minimal é MÍnimal. e deixe o tom dela mais de \"isso é um absurdo\". e adeque a copy.” Pronúncia tônica inicial é regra da marca; indignação bem-humorada é direção desta cena. Não chamar pronúncia/tom de verificados por ASR.

Primeira revisão, job `1e25efbe5fdafcb7190ff073`: rejeitada. O modelo recitou instruções em lugar da copy. ASR e rejeição preservados na pasta `verification` do job no SSD oficial. Segunda tentativa, `13dbec49ccb40a50f4c15248`: rejeitada. O ASR detectou repetição do trecho central; wrapper marcou risco de limite, embora o log do runtime informe `reached_limit:false` com 511 frames. O arquivo e o log permanecem arquivados. Não entregar essas tentativas como revisões corretas. A copy foi encurtada e uma nova receita/seed foi iniciada após examinar as falhas; resultado será registrado nesta sessão.

Resultado entregue: job `8343b8e7f9ddbf71a8ebbc28`, `manu-indignada-v2`, seed 321, 8,8236 s, WAV mono 44,1 kHz. Áudio no SSD oficial em `drama3/jobs/8343b8e7f9ddbf71a8ebbc28/audio.wav`, SHA `cccb552c1764cd3c23f01fbe2b97a0754c53a4548e04f532363f44b20eb4683d`. Geração em 157,59 s, arquivo externo verificado. ASR recuperou a copy inteira sem repetições/instruções; normalizadas caixa, pontuação e a grafia MÍnimal/Minimal da marca. Texto: “Isso é um absurdo! Dei uma camiseta MÍnimal pro meu namorado e ele virou modelo de espelho. Agora sai todo confiante. E o pior? Ficou lindo mesmo.” ASR/report final e rejeições estão em `verification` de seus jobs. Sem escuta; pronúncia, timbre, sotaque e atuação não certificados. Nenhum vídeo alterado ou conteúdo publicado no Ultron nesta tarefa de áudio.

## Memória externa

Busca no Segundo Cérebro funcionou e encontrou a pronúncia Mínimal já registrada em produção anterior. `registrar_decisao` para a correção desta sessão retornou `Error executing tool registrar_decisao`. `resolver_projeto` e `registrar_report` não estão expostos. Este arquivo é handoff local pendente de ingestão, não recibo de gravação canônica. Resolver o projeto pelo repositório real e usar chave `banco-de-vozes:20261030:github-bootstrap` ao consolidar.

A tentativa de criar/atualizar o estado do novo projeto via `atualizar_projeto`, com esse repositório e chave estável, também retornou `Error executing tool atualizar_projeto`. A continuidade está versionada neste arquivo; não há gravação canônica confirmada no Segundo Cérebro.
