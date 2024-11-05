#!/usr/bin/python3
"""
Module for saving the states of paired Bluetooth devices.
"""

from typing import Optional, Any
import logging
import os
import subprocess as sp

from blueman.plugins.AppletPlugin import AppletPlugin


class SavePairedStates(AppletPlugin):
    """
    Class for saving the states of paired Bluetooth devices when their paring status changes.

    Attributes:
        script_path (Optional[str]): Environment variable that indicates the path of the script that saves the paired states.
    """
    script_path: Optional[str] = os.getenv("ASTC_SAVE_SCRIPT")

    def save_paired_states(self) -> None:
        """
        Execute the save script.
        """
        if self.script_path is None:
            logging.debug("Environment variable is not set")
            return

        script_name: str = os.path.basename(self.script_path)

        try:
            result: sp.CompletedProcess = sp.run(['/usr/bin/python3', self.script_path], check=True)
            logging.debug(f"{script_name} is executed successfully")
        except sp.CalledProcessError as process_error:
            logging.debug(f"An error occured while executing the script: {process_error}")
    
    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        """
        Called when the device property changed.
        
        Args:
            path (str): MAC address of the connected device.
            key (str): Name of the Bluez property.
            value (Any): Value of the Bluez property.
        """
        if key == "Paired":
            self.save_paired_states()
    
    def on_device_removed(self, path: str) -> None:
        """
        Called when the device is removed.

        Args:
            path (str): MAC address of the connected device.
        """
        self.save_paired_states()
            
