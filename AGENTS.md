# Banco de vozes compartilhado

Este repositório privado é a fonte de verdade dos áudios de referência, transcrições, fichas, autorização e pronúncias. A implementação e os pesos do Drama são outro projeto. Não colocar pesos, caches, credenciais ou caminhos absolutos de uma máquina nos perfis portáteis.

Antes de usar: `python banco_vozes.py sync`. O CLI instalado do Drama também sincroniza antes de operar. Instalação e alterações em cada perfil são verificadas por hash. Nunca substituir a referência ou direção de um ID existente; crie uma variante versionada. Preserve fontes e versões anteriores.

Cada cadastro feito pelo CLI integrado é exportado e publicado por commit/push. Fichas editadas diretamente neste repositório também precisam de commit/push antes da entrega. Atualização local sem origin não conta como banco compartilhado. Não usar reset/clean/stash automático nem sobrescrever um checkout com alterações. As máquinas fazem avanço rápido a cada minuto e antes de usar o banco; máquinas offline retomam a atualização quando conectadas. Comprovar paridade por SHA do Git e SHA dos áudios.

A marca Minimal se pronuncia **MÍnimal**, tônica na primeira sílaba. Usar `Mínimal` no texto para síntese, como grafia de pronúncia, e preservar a grafia comercial Minimal em materiais escritos. Tom de indignação é específico da variante Manu indignada; não aplicar a todas as vozes.

Português do Brasil; fala viva, corrida, espontânea, conectada, sem arrastar nem preencher duração. Fichas e texto literal prevalecem. Hash/ASR não provam pronúncia, timbre, sotaque ou atuação. Não inventar escuta. Cadastro e sincronização não autorizam publicação de clones ou mensagens a terceiros.
