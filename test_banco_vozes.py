import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import banco_vozes as b


class VoiceBankTests(unittest.TestCase):
    def test_current_samples_match_catalog_and_cannot_escape_repository(self):
        self.assertGreaterEqual(len(b.verify()), 2)
        with self.assertRaises(ValueError):
            b.asset('../outside.wav')
        with self.assertRaises(ValueError):
            b.asset('/tmp/outside.wav')
        with self.assertRaises(ValueError):
            b.asset('C:\\outside.wav')

    def test_changed_reference_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / 'ref.wav'
            asset.write_bytes(b'original')
            b.write(root / 'catalog.json', {'profiles': [], 'files_sha256': {'ref.wav': b.sha(asset)}})
            asset.write_bytes(b'tampered')
            with patch.object(b, 'ROOT', root), self.assertRaisesRegex(RuntimeError, 'SHA divergente'):
                b.verify()

    def test_installed_conflicting_direction_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'voices' / 'test-v1' / 'voice.json'
            old = {'id': 'test-v1', 'reference_sha256': 'abc', 'transcript': 'Olá', 'direction': 'Original'}
            b.write(path, old)
            incoming = dict(old, direction='Outra atuação')
            with patch.object(b, 'machine', return_value=({}, root)):
                with self.assertRaisesRegex(RuntimeError, 'outra ficha'):
                    b.install([incoming])
            self.assertEqual(b.read(path), old)

    def test_git_sync_fast_forwards_and_preserves_dirty_or_diverged_checkout(self):
        def cmd(*args):
            return subprocess.check_output(['git', *map(str, args)], stderr=subprocess.DEVNULL, text=True).strip()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            origin, publisher, consumer = (root / p for p in ('remote.git', 'publisher', 'consumer'))
            cmd('init', '--bare', origin)
            cmd('clone', origin, publisher)
            cmd('-C', publisher, 'checkout', '-b', 'main')
            for key, value in [('user.name', 'Test'), ('user.email', 'test@example.invalid')]:
                cmd('-C', publisher, 'config', key, value)
            (publisher / '.gitignore').write_text('.state/\n')
            b.write(publisher / 'catalog.json', {'profiles': [], 'files_sha256': {}})
            cmd('-C', publisher, 'add', '.')
            cmd('-C', publisher, 'commit', '-m', 'initial')
            cmd('-C', publisher, 'push', 'origin', 'main')
            cmd('clone', '-b', 'main', origin, consumer)
            with patch.object(b, 'ROOT', consumer), patch.object(b, 'STATE', consumer / '.state'), patch.object(b, 'install', return_value='test'):
                first = b.sync()['commit']
                (publisher / 'update.txt').write_text('update')
                cmd('-C', publisher, 'add', '.')
                cmd('-C', publisher, 'commit', '-m', 'update')
                cmd('-C', publisher, 'push', 'origin', 'main')
                self.assertNotEqual(b.sync()['commit'], first)
                (consumer / 'update.txt').write_text('local WIP')
                with self.assertRaisesRegex(RuntimeError, 'alterações locais'):
                    b.sync()
                self.assertEqual((consumer / 'update.txt').read_text(), 'local WIP')
                for key, value in [('user.name', 'Test'), ('user.email', 'test@example.invalid')]:
                    cmd('-C', consumer, 'config', key, value)
                cmd('-C', consumer, 'add', '.')
                cmd('-C', consumer, 'commit', '-m', 'local unpushed')
                local = cmd('-C', consumer, 'rev-parse', 'HEAD')
                with self.assertRaisesRegex(RuntimeError, 'não publicados'):
                    b.sync()
                self.assertEqual(cmd('-C', consumer, 'rev-parse', 'HEAD'), local)


if __name__ == '__main__':
    unittest.main()
