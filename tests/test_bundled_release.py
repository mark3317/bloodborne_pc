import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'launcher'))
import bbport_bundle
import bbport_coop
import bbport_launcher_win as core


class BundleTests(unittest.TestCase):
    def test_offline_install_preserves_every_player_journal_and_host_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, target = root / 'payload', root / 'installed'
            files = {'bbsc/bbsc.dll': b'new mod', 'server/shadnet.cfg': b'default'}
            for name, data in files.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            (source / 'bundle.json').write_text(json.dumps({'version': '1.0.0', 'source': 'pinned',
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}))
            kept = ('bbsc/bell-pending/hunter.bin', 'bbsc/guest-items/hunter.bin',
                    'bbsc/shared-progress/hunter.bin', 'bbsc/own-world/hunter.bin',
                    'server/shadnet.cfg', 'server/db/accounts.db')
            for name in kept:
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'player data')
            with patch('urllib.request.urlopen', side_effect=AssertionError('Network used')):
                self.assertEqual(bbport_bundle.install(source, target), '1.0.0')
                bbport_bundle.install(source, target)
            for name in kept:
                self.assertEqual((target / name).read_bytes(), b'player data')
            self.assertEqual((target / 'bbsc/bbsc.dll').read_bytes(), b'new mod')
            (source / 'bbsc/bbsc.dll').write_bytes(b'corrupt')
            with self.assertRaises(ValueError):
                bbport_bundle.install(source, target)
            self.assertEqual((target / 'bbsc/bbsc.dll').read_bytes(), b'new mod')

    def test_stable_updates_ignore_preview_and_upstream_tags(self):
        for tag in ('qml-launcher-preview-99', 'v1.0.1-rc1', 'v1.0.0', 'v0.9.9'):
            self.assertFalse(core.release_is_newer(tag))
        self.assertTrue(core.release_is_newer('v1.0.1'))
        self.assertIn('/mark3317/bbgl/', core.RELEASES_API)

    def test_settings_reach_mod_environment_and_cheat_is_available(self):
        settings = dict(core.APP_DEFAULTS, bbsc_shared_progress=False, bbsc_scale_enemy_hp=75)
        environment = core.game_environment(settings)
        self.assertEqual(environment['SHADPS4_BBSC_SHARED_PROGRESS'], '0')
        self.assertEqual(environment['BBSC_SCALE_ENEMY_HP'], '75')
        self.assertIn('cheat_one_hit_kill', core.INI_DEFAULTS)
        self.assertEqual(core.INI_DEFAULTS['cheat_one_hit_kill'], '0')


if __name__ == '__main__':
    unittest.main()
