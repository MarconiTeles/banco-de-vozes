# Banco de vozes Minimal

Fonte de verdade privada de referências vocais autorizadas, compartilhada entre Mac e Windows por GitHub. O banco contém os áudios de referência, o sample original, transcrições, fichas e proveniência. Os pesos e o runtime continuam nas instalações locais do Drama; os WAVs gerados e seu histórico permanecem no SSD oficial.

| Voz | ID | Direção |
| --- | --- | --- |
| Manu | `manu-v1` | Ficha base, conversa viva e espontânea |
| Manu | `manu-indignada-v1` | Indignação bem-humorada de “isso é um absurdo”; mesma identidade vocal |

A marca Minimal se pronuncia **MÍnimal**, tônica inicial. Em texto para síntese, escrever `Mínimal`. A ficha de indignação é específica dessa versão; não muda a atuação padrão de todas as cenas.

## Sincronização

O comando instalado `drama-voice` busca `origin/main`, permite somente avanço rápido, confere hashes e importa os perfis na instalação local antes de operar. Um sincronizador nativo também executa a cada minuto. Máquinas conectadas convergem para o mesmo commit; não existe troca atômica simultânea entre máquinas offline. Nenhuma voz é usada pelo comando integrado sem uma sincronização bem-sucedida.

Alterações locais, commits não publicados ou divergências de ID impedem a sincronização, preservando o checkout e os perfis. Não há reset/clean/stash automático. Mesmo ID com outra referência ou direção é rejeitado; publicar um novo ID versionado.

```sh
python banco_vozes.py verify
python banco_vozes.py list
python banco_vozes.py configure --runtime /caminho/drama_voice.py --python /caminho/python
python banco_vozes.py sync
python banco_vozes.py run generate --voice manu-v1 --text-file /caminho/fala.txt --end-seconds 5
```

`configure` recebe o script nativo instalado: `drama_voice.py` no Mac ou `drama_voice_windows.py` no Windows. Os caminhos da máquina e o recibo ficam em `.state`, ignorado no Git. `catalog.json` e `voices/*/profile.json` usam apenas caminhos relativos e hashes compartilhados. Os perfis originais de cada runtime preservam seus caminhos próprios.

## Cadastro e atualização

Cadastros pelo `drama-voice voice-add` integrado são importados no runtime, exportados para este banco e publicados por commit/push. Falha de push é exibida e mantém o commit local recuperável; não conta como cadastro compartilhado. A próxima sincronização recusa esse estado até o push ser concluído. Não colocar tokens em URLs ou arquivos.

Para incorporar um perfil preexistente, usar `python banco_vozes.py export --voice ID --name Nome [--source ORIGINAL]`, revisar os arquivos, fazer commit e push. Alterações de catálogo/README/fichas também entram pelo Git. IDs já publicados são imutáveis. Não sobrescrever outro cadastro ou reaproveitar um ID para outra atuação.

As referências são deduplicadas por SHA-256. O sample integral autorizado fica em `sources`; os WAVs mono 44,1 kHz para condicionamento em `references`. A autorização de compartilhamento privado de Marconi e os hashes estão em `catalog.json`; a autorização da identidade está na ficha de cada voz. Este repositório não autoriza publicação pública dos clones.

## Verificação

`python -m unittest -v` testa integridade das referências, bloqueio de caminhos externos, preservação de perfis com ID conflitante e sincronização Git real com recusa de checkout alterado/divergente. O recibo local `.state/receipt.json` registra SHA do commit, hashes e horário. Conferir o mesmo SHA nas máquinas para afirmar paridade.

Integridade, ASR e direção escrita não comprovam timbre, pronúncia, sotaque ou naturalidade. Esses estados continuam separados de aprovação perceptiva.
