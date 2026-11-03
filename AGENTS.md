# Banco de vozes compartilhado

Este repositório privado é a fonte de verdade dos áudios de referência, transcrições, fichas, autorização e pronúncias. A implementação e os pesos do Drama são outro projeto. Não colocar pesos, caches, credenciais ou caminhos absolutos de uma máquina nos perfis portáteis.

Identidades, nesta ordem: Manu (`manu-v1`), Tio Phill (`tio-phill-v1`), Ester (`ester-v1`) e Airton 1 (`airton-1-v1`). Airton 1 é a voz cujo preset do DaVinci se chama Zebra; usar o nome Airton 1 nas novas solicitações e preservar Zebra apenas como proveniência. Variantes de atuação da Manu não são identidades adicionais. Confira `catalog.json`.

Antes de usar: `python banco_vozes.py sync`. Os launchers deste banco também sincronizam antes de operar: `~/.local/bin/drama-voice` no Mac e `drama-voice.cmd` no checkout do banco no Windows. Não usar o launcher Windows antigo do motor para contornar a sincronização. Instalação e alterações em cada perfil são verificadas por hash. Nunca substituir a referência ou direção de um ID existente; crie uma variante versionada. Preserve fontes e versões anteriores.

Cada cadastro feito pelo CLI integrado é exportado e publicado por commit/push. Fichas editadas diretamente neste repositório também precisam de commit/push antes da entrega. Atualização local sem origin não conta como banco compartilhado. Não usar reset/clean/stash automático nem sobrescrever um checkout com alterações. As máquinas fazem avanço rápido a cada minuto e antes de usar o banco; máquinas offline retomam a atualização quando conectadas. Comprovar paridade por SHA do Git e SHA dos áudios.

A marca Minimal se pronuncia **MÍnimal**, tônica na primeira sílaba. Usar `Mínimal` no texto para síntese, como grafia de pronúncia, e preservar a grafia comercial Minimal em materiais escritos. Tom de indignação é específico da variante Manu indignada; não aplicar a todas as vozes.

Português do Brasil; fala viva, corrida, espontânea, conectada, sem arrastar nem preencher duração. Fichas e texto literal prevalecem.

**Direção do Drama 3 (Marconi, 03/11/2026: “Formato oficial”):** a ficha `direction` documenta a identidade e **não vai mais ao modelo**; identidade, timbre e sotaque vêm do áudio de referência e da transcrição. Cada geração recebe só um estilo curto de atuação (`--style`, até 20 palavras, ideal 4 a 12), e o compilador põe `[language: pt] [audio tokens: N]`. Atuação muito diferente da referência pede uma referência nova (variante versionada), não uma ficha mais longa. Guia: `Compartilhados/drama-voice/DIRECAO-DRAMA3.md`. Hash/ASR não provam pronúncia, timbre, sotaque ou atuação. Não inventar escuta. Cadastro e sincronização não autorizam publicação de clones ou mensagens a terceiros.
