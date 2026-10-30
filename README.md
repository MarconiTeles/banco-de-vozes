# Banco de vozes Minimal

Fonte de verdade privada de referências vocais autorizadas, compartilhada entre Mac e Windows por GitHub. O banco contém os áudios de referência, o sample original, transcrições, fichas e proveniência. Os pesos e o runtime continuam nas instalações locais do Drama; os WAVs gerados e seu histórico permanecem no SSD oficial.

| Ordem | Voz | ID padrão | Origem |
| --- | --- | --- | --- |
| 1 | Manu | `manu-v1` | Sample VOICE MANU.mp3 autorizado por Marconi |
| 2 | Tio Phill | `tio-phill-v1` | WAV existente do DaVinci Voice Convert, preset TIO PHILL |
| 3 | Ester | `ester-v1` | WAV existente do DaVinci Voice Convert, preset Ester |
| 4 | Airton 1 | `airton-1-v1` | WAV existente do DaVinci Voice Convert, preset ZEBRA; renomeado por Marconi |

A variante de atuação da Manu em indignação bem-humorada é `manu-indignada-v2`, com direção enxuta. Variantes não contam como identidades adicionais; a ordem das identidades está em `catalog.json`.

`manu-indignada-v1` permanece no histórico. Sua primeira geração leu instruções; preferir v2 para a direção solicitada. A primeira tentativa de revisão não foi entregue como voiceover correto.

A marca Minimal se pronuncia **MÍnimal**, tônica inicial. Em texto para síntese, escrever `Mínimal`. A ficha de indignação é específica dessa versão; não muda a atuação padrão de todas as cenas.

## Sincronização

Os launchers `drama-voice` (Mac) e `drama-voice.cmd` (Windows) deste repositório buscam `origin/main`, permitem somente avanço rápido, conferem hashes e importam os perfis na instalação local antes de operar. O projeto está cadastrado no T3 do Mac e Windows com autoPull habilitado. No Mac, há também um sincronizador nativo por minuto. Máquinas conectadas convergem para o mesmo commit; não existe troca atômica simultânea entre máquinas offline. Nenhuma voz é usada pelos launchers deste banco sem uma sincronização bem-sucedida.

Alterações locais, commits não publicados ou divergências de ID impedem a sincronização, preservando o checkout e os perfis. Não há reset/clean/stash automático. Mesmo ID com outra referência ou direção é rejeitado; publicar um novo ID versionado.

```sh
python banco_vozes.py verify
python banco_vozes.py list
python banco_vozes.py configure --runtime /caminho/drama_voice.py --python /caminho/python
python banco_vozes.py sync
python banco_vozes.py run generate --voice manu-v1 --text-file /caminho/fala.txt --end-seconds 5
```

`configure` recebe o script nativo instalado: `drama_voice.py` no Mac ou `drama_voice_windows.py` no Windows. Os caminhos da máquina e o recibo ficam em `.state`, ignorado no Git. `catalog.json` e `voices/*/profile.json` usam apenas caminhos relativos e hashes compartilhados. Os perfis originais de cada runtime preservam seus caminhos próprios.

Os launchers descobrem automaticamente a instalação padrão se ainda não existir configuração local. No Windows, usar `C:\Users\MarconiReis\Projects\MacBook\banco-de-vozes\drama-voice.cmd`; no Mac, o comando `~/.local/bin/drama-voice` aponta ao launcher do banco. O motor continua separado e com os mesmos pesos, backend e locais de geração/arquivo.

## Cadastro e atualização

Cadastros pelo `drama-voice voice-add` integrado são importados no runtime, exportados para este banco e publicados por commit/push. Falha de push é exibida e mantém o commit local recuperável; não conta como cadastro compartilhado. A próxima sincronização recusa esse estado até o push ser concluído. Não colocar tokens em URLs ou arquivos.

Para incorporar um perfil preexistente, usar `python banco_vozes.py export --voice ID --name Nome [--source ORIGINAL]`, revisar os arquivos, fazer commit e push. Alterações de catálogo/README/fichas também entram pelo Git. IDs já publicados são imutáveis. Não sobrescrever outro cadastro ou reaproveitar um ID para outra atuação.

As referências são deduplicadas por SHA-256. O sample integral autorizado fica em `sources`; os WAVs mono 44,1 kHz para condicionamento em `references`. A autorização de compartilhamento privado de Marconi e os hashes estão em `catalog.json`; a autorização da identidade está na ficha de cada voz. Este repositório não autoriza publicação pública dos clones.

## Verificação

`python -m unittest -v` testa integridade das referências, bloqueio de caminhos externos, preservação de perfis com ID conflitante e sincronização Git real com recusa de checkout alterado/divergente. O recibo local `.state/receipt.json` registra SHA do commit, hashes e horário. Conferir o mesmo SHA nas máquinas para afirmar paridade.

Integridade, ASR e direção escrita não comprovam timbre, pronúncia, sotaque ou naturalidade. Esses estados continuam separados de aprovação perceptiva.

## Referências do DaVinci — 30/10/2026

Tio Phill, Ester e Airton 1 foram cadastrados a partir de WAVs já existentes na pasta VoiceConvert do DaVinci. Os presets `.drvox` não são áudios importáveis pelo Drama; os arquivos originais de treinamento desses presets não foram recuperados. As referências usadas são saídas convertidas pelo DaVinci, com o preset identificado pelo nome do arquivo e metadados de origem, sem afirmar uma ligação criptográfica entre preset e som.

Os WAVs completos de origem estão preservados em `sources`, e a cópia de condicionamento é PCM16 mono 44,1 kHz em `references`. As durações são 5,005 s (Tio Phill), 8 s (Ester) e 6,5065 s (Airton 1), dentro do contrato de 5–30 s do Drama. Não houve emenda, alongamento ou mudança de pitch/velocidade. Ficha, ASR, nome/hash do preset e proveniência estão em `voices/ID`. Os presets e os projetos do DaVinci permanecem intactos. Nenhuma geração de teste do Drama ou escuta foi feita nesses novos cadastros.
