import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'launcher'))
import bbport_coop as coop
import bbport_paths as paths
import bbport_launcher_win as core


class ProfileLayoutTests(unittest.TestCase):
    def test_offline_client_is_verified_in_place_and_damage_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            port = Path(temp) / 'install'
            source = port / 'coop/client'
            source.mkdir(parents=True)
            (source / 'bbsc.dll').write_bytes(b'mod')
            (source / 'bundle.json').write_text(json.dumps({'version': 'test', 'files': {
                'bbsc.dll': hashlib.sha256(b'mod').hexdigest()}}))
            with patch.object(coop, 'port_dir', return_value=port), patch.dict(os.environ, {'APPDATA': temp}):
                with patch('urllib.request.urlopen', side_effect=AssertionError('Network used')):
                    self.assertEqual(coop.download('client'), 'test')
                    self.assertFalse(coop.coop_dir().exists())
                    (source / 'bbsc.dll').write_bytes(b'broken')
                    with self.assertRaises(coop.CoopError):
                        coop.download('client')

    def test_profile_import_keeps_saves_host_database_and_existing_settings(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'APPDATA': temp, 'LOCALAPPDATA': temp}):
            port = Path(temp) / 'install'
            (port / 'user/savedata').mkdir(parents=True)
            (port / 'user/savedata/save').write_bytes(b'save')
            (port / 'bbport.ini').write_text('preset=3')
            old = Path(temp) / 'bbport-coop/shadnet-bbport/db'
            old.mkdir(parents=True)
            (old / 'accounts.db').write_bytes(b'accounts')
            root = paths.profile_dir()
            root.mkdir()
            (root / 'bbport.ini').write_text('preset=1')
            paths.initialize(port)
            self.assertEqual((root / 'bbport.ini').read_text(), 'preset=1')
            self.assertEqual((root / 'user/savedata/save').read_bytes(), b'save')
            self.assertEqual((root / 'coop/server/db/accounts.db').read_bytes(), b'accounts')
            paths.initialize(port)
            self.assertTrue((root / 'profile-layout-v2').exists())

    def test_host_keeps_both_servers_database_and_logs_in_profile(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'APPDATA': temp}):
            port = Path(temp) / 'install'
            folder = port / 'coop/server/server'
            folder.mkdir(parents=True)
            for name in ('shadnet.cfg', 'worlds.cfg', 'scoreboards.cfg'):
                (folder / name).write_text('default')
            process = Mock()
            process.poll.return_value = None
            with patch.object(coop, 'port_dir', return_value=port), \
                    patch.object(coop, 'end_leftovers'), patch.object(coop.time, 'sleep'), \
                    patch.object(coop.subprocess, 'Popen', return_value=process) as start:
                host = coop.Host()
                host.start('127.0.0.1')
                shadnet, game = start.call_args_list
                self.assertEqual(Path(shadnet.args[0][0]), folder / 'shadnet.exe')
                self.assertEqual(shadnet.kwargs['cwd'], coop.coop_dir() / 'server')
                self.assertEqual(shadnet.kwargs['env']['BBSC_SERVER_DATA_DIR'], str(coop.coop_dir() / 'server'))
                args = game.args[0]
                self.assertEqual(Path(args[args.index('--data') + 1]), coop.coop_dir() / 'server/online-data.json')
                self.assertEqual(game.kwargs['cwd'], coop.coop_dir() / 'server')
                for call in (shadnet, game):
                    call.kwargs['stdout'].close()

    def test_game_uses_one_profile_and_upstream_graphics_defaults(self):
        env = core.game_environment(dict(core.APP_DEFAULTS))
        self.assertEqual(Path(env['BB_DATA_DIR']), core.CONFIG_DIR)
        self.assertEqual(Path(env['BB_CONFIG']), core.CONFIG_DIR / 'bbport.ini')
        self.assertEqual(Path(env['BB_USER_DIR']), core.CONFIG_DIR / 'user')
        self.assertEqual(Path(env['BB_MODS_DIR']), core.PORT_DIR / 'mods')
        self.assertEqual(core.INI_DEFAULTS['skip_intro'], '1')
        self.assertEqual(core.INI_DEFAULTS['upscaler'], 'dlss')
        self.assertEqual(core.INI_DEFAULTS['preset'], '2')
        self.assertRegex(core.INI_DEFAULTS['output_res'], r'^\d+x\d+$')


if __name__ == '__main__':
    unittest.main()
