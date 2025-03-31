# pylint: disable=invalid-name
"""RfKill.py

This module handles enabling and disabling Bluetooth.
"""

import logging
import os
import subprocess as sp
import struct

from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.plugins.applet.KillSwitch import RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL

if not os.path.exists('/dev/rfkill'):
    raise ImportError("Hardware kill switch not found")


class RfKill(MechanismPlugin):
    """
    Handles enabling and disabling Bluetooth.
    """
    def on_load(self) -> None:
        self.parent.add_method("SetRfkillState", ("b",), "",
                               self._set_rfkill_state, pass_sender=True)

    def _set_rfkill_state(self, state: bool, caller: str) -> None:
        """
        Enables or disables Bluetooth.
        Called when the Bluetooth on/off button in the systray menu is clicked.

        When enabling Bluetooth:
            1. Add the kernel Bluetooth module
            2. Start the Bluetooth service
            3. Unblock the Bluetooth adapter
        When disabling Bluetooth:
            1. Block the Bluetooth adapter
            2. Remove the kernel Bluetooth module
            3. Stop the Bluetooth service

        Note:
            Adding the kernel Bluetooth module sometimes unblocks the Bluetooth adapter
            automaically.
            Adding the kernel Bluetooth module starts the Bluetooth service.

        Args:
            state (bool): True to enable Bluetooth, False to disable it.
            caller (str): Caller requesting permission to change the rfkill state.
        """
        try:
            if state:
                sp.check_call(['/usr/bin/sudo', '/usr/sbin/modprobe', 'btusb'])
                logging.debug('Kernel Bluetooth module is added, '
                              'Bluetooth service should start automatically if not already running')
                self.rfkill_bluetooth(state, caller)
            else:
                self.rfkill_bluetooth(state, caller)
                sp.check_call(['/usr/bin/sudo', '/usr/sbin/modprobe', '-r', 'btusb'])
                logging.debug('The kernel Bluetooth module is removed')
                sp.check_call(['/usr/bin/systemctl', 'stop', 'bluetooth.service'])
                logging.debug('The Bluetooth service is stoppped')
        except sp.CalledProcessError as err:
            logging.error('Failed to change Bluetooth state: %s', err)

    def rfkill_bluetooth(self, state: bool, caller: str) -> None:
        """
        Blocks or unblocks the Bluetooth adapter.

        Args:
            state (bool): True to unblock Bluetooth, False to block it.
            caller (str): Caller requesting permission to change the rfkill state.
        """
        self.confirm_authorization(caller, "org.blueman.rfkill.setstate")
        with open('/dev/rfkill', 'r+b', buffering=0) as dev:
            dev.write(struct.pack("IBBBB", 0, RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL,
                                  (0 if state else 1), 0))
        logging.debug('Bluetooth adapter is %s', 'unblocked' if state else 'blocked')
    