#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>

from typing import TYPE_CHECKING, Optional

from .base import (
    MATCH_WINDOW_OPTION, ArgsType, Boss, MatchError, PayloadGetType,
    PayloadType, RCOptions, RemoteCommand, ResponseType, Window
)

if TYPE_CHECKING:
    from kitty.cli_stub import SignalChildRCOptions as CLIOptions


class SignalChild(RemoteCommand):

    '''
    signals: The signals, a list of names, such as :code:`SIGTERM`, :code:`SIGKILL`, :code:`SIGUSR1`, etc.
    match: Which windows to send the signals to
    '''

    short_desc = 'Send a signal to the foreground process in the specified windows'
    desc = (
        'Send one or more signals to the foreground process in the specified windows.'
        ' If you use the :option:`kitty @ signal-child --match` option'
        ' the signal will be sent for all matched windows. By default, only the active'
        ' window is affected. If you do not specify any signals, :code:`SIGINT` is sent by default.'
        ' You can also map this to a shortcut in :file:`kitty.conf`, for example::\n\n'
        '    map f1 signal_child SIGTERM'
    )
    options_spec = '''\
    ''' + '\n\n' + MATCH_WINDOW_OPTION
    argspec = '[SIGNAL_NAME ...]'

    def message_to_kitty(self, global_opts: RCOptions, opts: 'CLIOptions', args: ArgsType) -> PayloadType:
        return {'match': opts.match, 'signals': [x.upper() for x in args] or ['SIGINT']}

    def response_from_kitty(self, boss: Boss, window: Optional[Window], payload_get: PayloadGetType) -> ResponseType:
        import signal
        windows = [window or boss.active_window]
        match = payload_get('match')
        if match:
            windows = list(boss.match_windows(match))
            if not windows:
                raise MatchError(match)
        signals = tuple(getattr(signal, x) for x in payload_get('signals'))
        for window in windows:
            if window:
                window.signal_child(*signals)
        return None


signal_child = SignalChild()
