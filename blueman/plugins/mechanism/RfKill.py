import logging
import os
import subprocess as sp
import struct
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.plugins.applet.KillSwitch import RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL

if not os.path.exists('/dev/rfkill'):
    raise ImportError("Hardware kill switch not found")

class RfKill(MechanismPlugin):
    def on_load(self) -> None:
        self.parent.add_method("SetRfkillState", ("b",), "", self._set_rfkill_state, pass_sender=True)

    def _set_rfkill_state(self, state: bool, caller: str) -> None:
        """
        Enable/Disable Bluetooth.
        Called when the Bluetooth on/off button in the systray menu is clicked.

        Args:
            state (bool): Wheather the Bluetooth button of on or off is clicked.
            caller (str): Caller requesting permission to change the rfkill state.
        """
        try:
            if state:
                self.rfkill_bluetooth(state, caller)
                sp.check_call(['/usr/bin/sudo', '/usr/sbin/modprobe', 'btusb'])
                sp.check_call(['/usr/bin/systemctl', 'start', 'bluetooth.service'])
                logging.debug('Started Bluetooth service and unblocked Bluetooth adapter')
            else:
                sp.check_call(['/usr/bin/systemctl', 'stop', 'bluetooth.service'])
                sp.check_call(['/usr/bin/sudo', '/usr/sbin/modprobe', '-r', 'btusb'])
                self.rfkill_bluetooth(state, caller)
                logging.debug('Stopped Bluetooth service and blocked Bluetooth adapter')
        except sp.CalledProcessError as process_error:
            logging.error(f'An error occured while turning on/off Bluetooth: {process_error}')

    def rfkill_bluetooth(self, state: bool, caller: str) -> None:
        """
        Block/Unblock the Bluetooth adatper.

        Args:
            state (bool): Wheather the Bluetooth button of on or off is clicked.
            caller (str): Caller requesting permission to change the rfkill state.
        """
        self.confirm_authorization(caller, "org.blueman.rfkill.setstate")
        with open('/dev/rfkill', 'r+b', buffering=0) as dev:
            dev.write(struct.pack("IBBBB", 0, RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL, (0 if state else 1), 0))

        
