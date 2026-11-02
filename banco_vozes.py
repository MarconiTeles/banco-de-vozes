#!/usr/bin/env python3
"""Banco portátil; Git privado é a fonte de verdade. Sem dependências externas."""
import argparse
import contextlib
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid
import wave

ROOT = Path(__file__).resolve().parent
STATE = ROOT / '.state'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    os.replace(temporary, path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def asset(relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative:
        raise ValueError('Caminho não portátil: ' + relative)
    path = ROOT / path
    if path.is_symlink() or ROOT.resolve() not in path.resolve().parents or not path.is_file():
        raise ValueError('Arquivo ausente ou fora do banco: ' + relative)
    return path


TEXT_SUFFIXES = ('.json', '.md', '.py', '.txt')


def normalize_eol(repair=False):
    """`.gitattributes` fixa LF nos textos. Um checkout/editor Windows pode deixar CRLF no disco
    (visto em 01/11/2026 nos perfis airton-1-carioca-ugc-v1/v2/v3 do notebook): o Git mostra
    o arquivo limpo, mas o SHA dos bytes diverge do catálogo. Só reescreve em LF quando o
    conteúdo normalizado é exatamente o publicado (mesmo SHA); qualquer outra diferença falha."""
    catalog = json.loads((ROOT / 'catalog.json').read_bytes().replace(b'\r\n', b'\n').decode('utf-8-sig'))
    fixed = []
    for relative, digest in catalog['files_sha256'].items():
        if not relative.endswith(TEXT_SUFFIXES):
            continue
        path = asset(relative)
        raw = path.read_bytes()
        if b'\r\n' not in raw:
            continue
        lf = raw.replace(b'\r\n', b'\n')
        if hashlib.sha256(lf).hexdigest() != digest:
            raise RuntimeError('SHA divergente (além de CRLF): ' + relative)
        if repair:
            temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
            temporary.write_bytes(lf)
            os.replace(temporary, path)
        fixed.append(relative)
    raw = (ROOT / 'catalog.json').read_bytes()
    if b'\r\n' in raw and repair:
        temporary = ROOT / ('catalog.json.' + uuid.uuid4().hex + '.tmp')
        temporary.write_bytes(raw.replace(b'\r\n', b'\n'))
        os.replace(temporary, ROOT / 'catalog.json')
        fixed.append('catalog.json')
    return fixed


def verify():
    catalog = read(ROOT / 'catalog.json')
    for relative, digest in catalog['files_sha256'].items():
        if sha(asset(relative)) != digest:
            raise RuntimeError('SHA divergente: ' + relative + ' (se for só CRLF, `python banco_vozes.py sync` repara)')
    profiles = []
    seen = set()
    for relative in catalog['profiles']:
        if relative not in catalog['files_sha256']:
            raise ValueError('Perfil sem hash: ' + relative)
        v = read(asset(relative))
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', v['id']) or v['id'] in seen:
            raise ValueError('ID repetido ou inválido')
        seen.add(v['id'])
        if catalog['files_sha256'].get(v['reference']) != v['reference_sha256']:
            raise ValueError('Referência sem hash correspondente')
        for field in ('transcript', 'direction', 'authorized_by'):
            if not v[field].strip():
                raise ValueError('Campo obrigatório: ' + field)
        profiles.append(v)
    return profiles


def git(*args, check=True):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True,
                            text=True, encoding='utf-8', env=env, timeout=90)
    if not check:
        return result.stdout.strip()
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or 'Git falhou')
    return result.stdout.strip()


@contextlib.contextmanager
def locked():
    STATE.mkdir(exist_ok=True)
    with (STATE / 'sync.lock').open('a+b') as f:
        f.seek(0)
        f.write(b'0')
        f.flush()
        deadline = time.monotonic() + 45
        while True:
            try:
                f.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError('Sincronização já em andamento; trava preservada')
                time.sleep(0.25)
        try:
            yield
        finally:
            if os.name == 'nt':
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_UN)


def executar_runtime(cmd):
    """Roda o CLI do Drama e o encerra junto com este launcher, em erro ou sinal (Marconi, 02/11/2026: “tanto o drama
    quanto o davinci devem ser abertos quando usados e depois FECHADOS quando acabar o uso SEMPRE”). Windows: o filho
    entra num Job Object KILL_ON_JOB_CLOSE (morre se este processo morrer); POSIX: SIGTERM/SIGHUP/SIGINT são repassados."""
    import signal
    proc = subprocess.Popen(cmd)
    if os.name == 'nt':
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.CreateJobObjectW.restype = ctypes.c_void_p
            k.SetInformationJobObject.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
            k.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

            class BASIC(ctypes.Structure):
                _fields_ = [('a', ctypes.c_int64), ('b', ctypes.c_int64), ('LimitFlags', ctypes.c_uint32), ('c', ctypes.c_size_t),
                            ('d', ctypes.c_size_t), ('e', ctypes.c_uint32), ('f', ctypes.c_size_t), ('g', ctypes.c_uint32),
                            ('h', ctypes.c_uint32)]

            class EXT(ctypes.Structure):
                _fields_ = [('basic', BASIC), ('io', ctypes.c_uint64 * 6), ('i', ctypes.c_size_t), ('j', ctypes.c_size_t),
                            ('k', ctypes.c_size_t), ('l', ctypes.c_size_t)]
            job = k.CreateJobObjectW(None, None)
            e = EXT()
            e.basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not (job and k.SetInformationJobObject(job, 9, ctypes.byref(e), ctypes.sizeof(e))
                    and k.AssignProcessToJobObject(job, int(proc._handle))):
                raise OSError('Job Object recusado')
            executar_runtime.job = job  # o handle vive enquanto este processo vive
        except Exception as exc:
            print(json.dumps({'aviso': 'runtime fora do Job Object: ' + str(exc)}, ensure_ascii=False), file=sys.stderr)
    else:
        def repassar(sinal, _quadro):
            with contextlib.suppress(ProcessLookupError):
                proc.send_signal(sinal)
        for sinal in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            signal.signal(sinal, repassar)
    while True:
        try:
            return proc.wait()
        except KeyboardInterrupt:
            continue  # o sinal já foi repassado; espera o filho encerrar o motor e sair


def runtime_module(config):
    path = Path(config['runtime']).resolve(strict=True)
    spec = importlib.util.spec_from_file_location('drama_bank_runtime', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def machine():
    if not (STATE / 'machine.json').exists():
        if os.name == 'nt':
            runtime = Path(os.environ['LOCALAPPDATA']) / 'ULTRON/drama3/cli/drama_voice_windows.py'
        else:
            runtime = ROOT.parent / 'drama-voice/drama_voice.py'
        if not runtime.is_file():
            raise RuntimeError('Runtime ausente; execute configure --runtime CAMINHO --python PYTHON')
        write(STATE / 'machine.json', {'runtime': str(runtime.resolve()), 'python': sys.executable})
    config = read(STATE / 'machine.json')
    module = runtime_module(config)
    root = module.ROOT if os.name == 'nt' else module.storage(module.config())
    return config, Path(root)


def install(profiles):
    config, root = machine()
    for v in profiles:
        existing = root / 'voices' / v['id'] / 'voice.json'
        if existing.exists():
            old = read(existing)
            if any(old.get(k) != v[k] for k in ('id', 'reference_sha256', 'transcript', 'direction')):
                raise RuntimeError('ID já tem outra ficha; crie nova versão: ' + v['id'])
            if sha(Path(old['reference'])) != v['reference_sha256']:
                raise RuntimeError('Referência instalada divergiu: ' + v['id'])
            continue
        # Copy canonical WAV bytes. Re-encoding on each OS changes container
        # headers/encoder tags and would make the bank hashes machine-specific.
        module = runtime_module(config)
        c = None if os.name == 'nt' else module.config()
        local = module.WORK if os.name == 'nt' else module.execution_storage(c)
        guard = module.locked() if os.name == 'nt' else module.locked(local)
        with guard:
            target = existing.parent
            if target.exists():
                raise RuntimeError('Outro processo cadastrou a voz; repita a sincronização: ' + v['id'])
            folder = local / 'voice-registration' / (v['id'] + '-' + uuid.uuid4().hex)
            folder.mkdir(parents=True)
            reference = asset(v['reference'])
            shutil.copy2(reference, folder / 'reference.wav')
            shutil.copy2(reference, folder / 'original.wav')
            if sha(folder / 'reference.wav') != v['reference_sha256']:
                raise RuntimeError('Cópia interna divergente; área local preservada')
            with wave.open(str(reference)) as audio:
                if (audio.getnchannels(), audio.getframerate(), audio.getsampwidth()) != (1, 44100, 2):
                    raise RuntimeError('O banco exige referência WAV mono PCM16 44,1 kHz')
                duration = audio.getnframes() / audio.getframerate()
                if not 5 <= duration <= 30:
                    raise RuntimeError('Duração fora do contrato de referência')
            record = {k: v[k] for k in ('id', 'transcript', 'direction', 'authorized_by', 'created_at', 'authorization_scope')}
            record.update(source=str(reference), source_sha256=v['reference_sha256'],
                          reference=str(target / 'reference.wav'), reference_sha256=v['reference_sha256'],
                          reference_info={'duration': duration, 'sample_rate': 44100, 'channels': 1})
            write(folder / 'voice.json', record)
            if os.name == 'nt':
                target.parent.mkdir(parents=True, exist_ok=True)
                os.rename(folder, target)
            else:
                module.transfer_bundle(c, root, 'voices', v['id'], folder)
                shutil.rmtree(folder)
        installed = read(existing)
        if sha(Path(installed['reference'])) != v['reference_sha256']:
            raise RuntimeError('Importação alterou a referência: ' + v['id'])
    return str(root)


def sync():
    with locked():
        if git('status', '--porcelain'):
            raise RuntimeError('Banco tem alterações locais; faça commit/push antes de sincronizar')
        if git('branch', '--show-current') != 'main':
            raise RuntimeError('Sincronização exige branch main')
        git('fetch', 'origin', 'main')
        # Never create a merge commit or discard a local branch.
        git('merge', '--ff-only', 'origin/main')
        if git('rev-parse', 'HEAD') != git('rev-parse', 'origin/main'):
            raise RuntimeError('Há commits locais não publicados; faça push')
        if git('config', '--get', 'core.autocrlf', check=False) not in ('', 'false', 'input'):
            git('config', 'core.autocrlf', 'false')  # impede nova conversão para CRLF neste checkout
        repaired = normalize_eol(repair=True)
        profiles = verify()
        root = install(profiles)
        receipt = {'commit': git('rev-parse', 'HEAD'), 'voices': [v['id'] for v in profiles], 'eol_repaired': repaired,
                   'files_sha256': read(ROOT / 'catalog.json')['files_sha256'],
                   'installed_root': root, 'verified_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        write(STATE / 'receipt.json', receipt)
        return receipt


def export_voice(ident, display_name=None, source=None):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', ident):
        raise ValueError('ID inválido')
    _, data = machine()
    voice = read(data / 'voices' / ident / 'voice.json')
    digest = sha(Path(voice['reference']))
    if digest != voice['reference_sha256']:
        raise RuntimeError('Referência da voz divergiu')
    relative = 'references/' + digest + '.wav'
    dest = ROOT / relative
    dest.parent.mkdir(exist_ok=True)
    if dest.exists() and sha(dest) != digest:
        raise RuntimeError('Referência existente divergente')
    if not dest.exists():
        shutil.copy2(voice['reference'], dest)
    profile = {k: voice[k] for k in ('id', 'transcript', 'direction', 'authorized_by', 'reference_sha256', 'created_at')}
    profile.update(name=display_name or ident, reference=relative, language='pt-BR',
                   listening_verified=False, authorization_scope=voice.get('authorization_scope', 'Conforme autorização de origem.'))
    relprofile = 'voices/' + ident + '/profile.json'
    old = ROOT / relprofile
    if old.exists() and read(old) != profile:
        raise RuntimeError('Perfil existente é imutável; use outro ID')
    write(old, profile)
    catalog = read(ROOT / 'catalog.json')
    if relprofile not in catalog['profiles']:
        catalog['profiles'].append(relprofile)
    catalog['files_sha256'][relative] = digest
    catalog['files_sha256'][relprofile] = sha(old)
    if source:
        original = Path(source).resolve(strict=True)
        original_hash = sha(original)
        relsource = 'sources/' + original_hash + original.suffix.lower()
        output = ROOT / relsource
        output.parent.mkdir(exist_ok=True)
        if not output.exists():
            shutil.copy2(original, output)
        if sha(output) != original_hash:
            raise RuntimeError('Original divergiu na cópia')
        catalog['files_sha256'][relsource] = original_hash
        catalog.setdefault('sources', {})[ident] = {'file': relsource, 'original_filename': original.name}
    catalog['profiles'].sort()
    write(ROOT / 'catalog.json', catalog)
    verify()
    return profile


def publish(ident):
    with locked():
        if git('status', '--porcelain'):
            raise RuntimeError('Publique ou preserve as alterações locais antes de cadastrar outra voz')
        _, data = machine()
        v = read(data / 'voices' / ident / 'voice.json')
        original = data / 'voices' / ident / ('original' + Path(v['source']).suffix.lower())
        export_voice(ident, source=original if original.exists() else None)
        git('add', '--', 'catalog.json', 'references', 'voices', 'sources')
        if git('diff', '--cached', '--name-only'):
            git('commit', '-m', 'Adicionar referência vocal ' + ident)
        git('push', 'origin', 'main')
        return {'published_commit': git('rev-parse', 'HEAD'), 'voice': ident}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('verify', 'list', 'sync'):
        commands.add_parser(name)
    configure = commands.add_parser('configure')
    configure.add_argument('--runtime', required=True)
    configure.add_argument('--python', default=sys.executable)
    export = commands.add_parser('export')
    export.add_argument('--voice', required=True)
    export.add_argument('--name')
    export.add_argument('--source')
    run = commands.add_parser('run')
    run.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command == 'configure':
        write(STATE / 'machine.json', {'runtime': str(Path(args.runtime).resolve(strict=True)), 'python': args.python})
        result = {'voices': [v['id'] for v in verify()], 'installed_root': install(verify())}
    elif args.command in ('verify', 'list'):
        result = [{'id': v['id'], 'name': v['name'], 'reference_sha256': v['reference_sha256']} for v in verify()]
    elif args.command == 'export':
        result = export_voice(args.voice, args.name, args.source)
    elif args.command == 'sync':
        result = sync()
    else:
        try:
            sync()
        except Exception as exc:
            # Nunca operar (nem listar vozes) com um banco que não sincronizou: lista antiga sem
            # erro já enganou uma thread no notebook (01/11/2026).
            print(json.dumps({'error': 'Banco de vozes não sincronizou; nada foi executado: ' + str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 2
        config, _ = machine()
        code = executar_runtime([config['python'], config['runtime'], *args.args])
        if code == 0 and args.args and args.args[0] == 'voice-add':
            ident = args.args[args.args.index('--id') + 1]
            print(json.dumps(publish(ident)), file=sys.stderr)
        return code
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
