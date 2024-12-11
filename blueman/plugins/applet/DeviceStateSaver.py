#!/usr/bin/python3
"""
Module for saving the states of paired Bluetooth devices.
"""

from typing import Optional, Any
import logging
import os
import subprocess as sp

from blueman.plugins.AppletPlugin import AppletPlugin


class DeviceStateSaver(AppletPlugin):
    """
    Class for saving the states of paired Bluetooth devices when their paring status changes.

    Attributes:
        script_path (Optional[str]): Environment variable that indicates the path of the script that saves the paired states.
    """
    script_path: Optional[str] = os.getenv("ASTC_SAVE_SCRIPT")

    def on_load(self) -> None:
        """
        Called when Blueman is launched. (Called from BasePlugin class)
        """
        self._add_dbus_method("SaveDeviceState", (), "", self.save_device_state)

    def save_device_state(self) -> None:
        """
        Execute the save script.
        """
        if self.script_path is None:
            logging.debug("The states of paired devices couldn't be saved.")
            return

        try:
            result: sp.CompletedProcess = sp.run(['/usr/bin/python3', self.script_path], check=True)
            logging.debug(f"The states of paired devices are saved.")
        except sp.CalledProcessError as process_error:
            logging.debug(f"An error occured while saving the states of paired devices: {process_error}")
    
    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        """
        Called when the device property changed.
        
        Args:
            path (str): MAC address of the connected device.
            key (str): Name of the Bluez property.
            value (Any): Value of the Bluez property.
        """
        if key == "Paired":
            self.save_device_state()
    
    def on_device_removed(self, path: str) -> None:
        """
        Called when the device is removed.

        Args:
            path (str): MAC address of the connected device.
        """
        self.save_device_state()
            
