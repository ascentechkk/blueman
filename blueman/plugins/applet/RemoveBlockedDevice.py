#!/usr/bin/python3
"""
Handles removing blocked devices.
"""

import logging
from typing import Any

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin


class RemoveBlockedDevice(AppletPlugin):
    """
    Handles removing blocked devices.
    """
    def on_adapter_property_changed(self, path: str, _key: str, _value: Any) -> None:
        """
        Called when a device property is changed.

        Args:
            path (str): The MAC address of the adapter.
            _key (str): The property that has changed.
            _value (Any): The value of the propety.
        """
        self.adapter: Adapter = Adapter(obj_path=path)

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        """
        Called when a device property is changed.

        Args:
            path (str): The MAC address of the device.
            key (str): The property that has changed.
            value (Any): The value of the propety.
        """
        if key == 'Connected' and not value and self.parent.is_device_blocked(path):
            device: Device = Device(obj_path=path)
            self.adapter.remove_device(device)
            logging.debug(f"Blocked device removed: {device}")
