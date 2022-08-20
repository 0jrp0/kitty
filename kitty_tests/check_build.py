#!/usr/bin/env python
# License: GPLv3 Copyright: 2021, Kovid Goyal <kovid at kovidgoyal.net>


import os
import sys
import unittest
from functools import partial

from . import BaseTest


class TestBuild(BaseTest):

    def test_exe(self) -> None:
        from kitty.constants import kitty_exe
        exe = kitty_exe()
        self.assertTrue(os.access(exe, os.X_OK))
        self.assertTrue(os.path.isfile(exe))
        self.assertIn('kitty', os.path.basename(exe))

    def test_loading_extensions(self) -> None:
        import kitty.fast_data_types as fdt
        from kittens.choose import subseq_matcher
        from kittens.diff import diff_speedup
        from kittens.transfer import rsync
        from kittens.unicode_input import unicode_names
        del fdt, unicode_names, subseq_matcher, diff_speedup, rsync

    def test_loading_shaders(self) -> None:
        from kitty.utils import load_shaders
        for name in 'cell border bgimage tint blit graphics'.split():
            load_shaders(name)

    def test_glfw_modules(self) -> None:
        from kitty.constants import glfw_path, is_macos
        linux_backends = ['x11']
        if not self.is_ci:
            linux_backends.append('wayland')
        modules = ['cocoa'] if is_macos else linux_backends
        for name in modules:
            path = glfw_path(name)
            self.assertTrue(os.path.isfile(path), f'{path} is not a file')
            self.assertTrue(os.access(path, os.X_OK), f'{path} is not executable')

    def test_all_kitten_names(self) -> None:
        from kittens.runner import all_kitten_names
        names = all_kitten_names()
        self.assertIn('diff', names)
        self.assertIn('hints', names)
        self.assertGreater(len(names), 8)

    def test_filesystem_locations(self) -> None:
        from kitty.constants import (
            local_docs, logo_png_file, shell_integration_dir, terminfo_dir
        )
        zsh = os.path.join(shell_integration_dir, 'zsh')
        self.assertTrue(os.path.isdir(terminfo_dir), f'Terminfo dir: {terminfo_dir}')
        self.assertTrue(os.path.exists(logo_png_file), f'Logo file: {logo_png_file}')
        self.assertTrue(os.path.exists(zsh), f'Shell integration: {zsh}')
        self.assertTrue(os.access(os.path.join(shell_integration_dir, 'ssh', 'askpass.py'), os.X_OK))
        if getattr(sys, 'frozen', False):
            self.assertTrue(os.path.isdir(local_docs()), f'Local docs: {local_docs()}')

    def test_ca_certificates(self):
        import ssl
        if not getattr(sys, 'frozen', False):
            self.skipTest('CA certificates are only tested on frozen builds')
        c = ssl.create_default_context()
        self.assertGreater(c.cert_store_stats()['x509_ca'], 2)

    def test_pygments(self):
        if not getattr(sys, 'frozen', False):
            self.skipTest('Pygments is only tested on frozen builds')
        import pygments
        del pygments

    def test_docs_url(self):
        from kitty.utils import docs_url
        from kitty.constants import website_url

        def run_tests(p, base, suffix='.html'):
            def t(x, e):
                self.ae(p(x), base + e)
            t('', 'index.html' if suffix == '.html' else '')
            t('conf', f'conf{suffix}')
            t('kittens/ssh#frag', f'kittens/ssh{suffix}#frag')
            t('#ref=confloc', f'conf{suffix}#confloc')
            t('#ref=conf-kitty-fonts', f'conf{suffix}#conf-kitty-fonts')
            t('#ref=conf-kitten-ssh-xxx', f'kittens/ssh{suffix}#conf-kitten-ssh-xxx')
            t('#ref=at_close_tab', f'remote-control{suffix}#at_close-tab')
            t('#ref=action-copy', f'actions{suffix}#copy')

        run_tests(partial(docs_url, local_docs_root='/docs'), 'file:///docs/')
        w = website_url()
        run_tests(partial(docs_url, local_docs_root=None), w, '/')


def main() -> None:
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestBuild)
    r = unittest.TextTestRunner(verbosity=4)
    result = r.run(tests)
    if result.errors or result.failures:
        raise SystemExit(1)
