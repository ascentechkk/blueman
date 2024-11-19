#!/usr/bin/python3
"""
Handles the systray menu for each device.
"""

import logging
from gettext import gettext as _
from typing import Any, Callable, cast, List, TYPE_CHECKING

from blueman.bluez.Device import Device
from blueman.bluez.errors import BluezDBusException
from blueman.plugins.AppletPlugin import AppletPlugin

if TYPE_CHECKING:
    from blueman.plugins.applet.Menu import Menu, SubmenuItemDict

class SystrayDeviceMenu(AppletPlugin):
    """
    Handles the systray menu for each device.

    Attributes:
        allowed_classes (List[str]): A list of devices classes to add a device menu.
        allowed_appearances (List[str]): A list of devices appearances to add a device menu.
    """
    allowed_classes: List[str] = [
        0x000540, # Mouse
        0x000580, # Keyboard
        0x0005c0, # Combo Mouse/Keyboard
    ]

    allowed_appearances: List[str] = [
        0x03c1, # Mouse
        0x03c2, # Keyboard
    ]

    def on_load(self) -> None:
        """
        Called when Blueman is launched.
        """
        self.paired_devices: List[str] = []
        self.menu: 'Menu' = self.parent.Plugins.Menu
        self.add_device_menu()

    def on_unload(self) -> None:
        """
        Called when this plugin is unloaded.
        Might be unnecessary since the plugin menu became uninteractable in GUI.
        """
        self.menu.unregister(self)

    def on_device_created(self, _path: str) -> None:
        """
        Called when a device is found.

        Args:
            _path (str): The MAC address of the found device.
        """
        self.add_device_menu()

    def on_device_removed(self, _path: str) -> None:
        """
        Called when a device is removed.

        Args:
            _path (str): The MAC address of the removed device.
        """
        self.add_device_menu()

    def on_adapter_added(self, _path: str) -> None:
        """
        Called when an adapter is found.

        Args:
            _path (str): The MAC address of the found adapter.
        """
        self.add_device_menu()

    def on_adapter_removed(self, _path: str) -> None:
        """
        Called when an adapter is removed.

        Args:
            _path (str): The MAC address of the remove adapter.
        """
        self.add_device_menu()

    def on_device_property_changed(self, _path: str, key: str, _value: Any) -> None:
        """
        Called when a device property is changed.

        Args:
            _path (str): The MAC address of the device.
            key (str): The property that has changed.
            _value (Any): The value of the propety.
        """
        if key == 'Connected':
            self.add_device_menu()

    def generate_device_menu(self, device: Device) -> List['SubmenuItemDict']:
        """
        Generate a device menu for each paired device.

        Args:
            device (Device): A Bluetooth device.

        Returns:
            items (List['SubmenuItemDict']): A list of sub device menu.
        """
        items: List['SubmenuItemDict'] = []
        uuid: str = "00000000-0000-0000-0000-000000000000" 

        def connect_reply() -> None:
            logging.debug("Connected successfully")

        def connect_err(reason: BluezDBusException) -> None:
            logging.debug(f"Failed to connect: {reason}")

        def disconnect_reply() -> None:
            logging.debug("Disconnected successfully")

        def disconnect_err(reason: BluezDBusException) -> None:
            logging.debug(f"Failed to disconnect: {reason}")


        items.append({
            "text": _("Connect") if not device["Connected"] else _("Disconnect"),
            "markup": True,
            "icon_name": "bluetooth-symbolic" if not device["Connected"] else "bluetooth-disabled-symbolic",
            "sensitive": True,
            "callback": cast(
                Callable[[], None],
                lambda dev=device: self.parent.Plugins.DBusService.connect_service(
                    dev.get_object_path(),
                    uuid,
                    connect_reply,
                    connect_err
                )
            ) if not device["Connected"]
            else cast(
                Callable[[], None],
                lambda dev=device: self.parent.Plugins.DBusService._disconnect_service(
                    dev.get_object_path(),
                    uuid,
                    0,
                    disconnect_reply,
                    disconnect_err
                )
            ),
            "tooltip": "",
        })
        
        return items

    def add_device_menu(self) -> None:
        """
        Add a device menu for each paired device.
        """
        self.menu.unregister(self)
        devices: List[Device] = self.parent.Manager.get_devices()
        for idx, device in enumerate(devices):
            if not device['Paired'] and not device['Connected']:
                continue
            
            if not self.get_allowed_device(device) and device['Connected']:
                continue

            self.menu.add(
                self,
                (3, idx),
                text=device['Alias'],
                icon_name=device['Icon'],
                submenu_function=lambda dev=device: self.generate_device_menu(dev)
            )

    def get_allowed_device(self, device: Device) -> bool:
        """
        Check if wheather to add a device menu.

        Args:
            device (Device): A Bluetooth device.
        
        Returns:
            bool: True for adding a device menu, False otherwise.
        """
        klass: int = device["Class"] & 0xfff
        appearance: int = device["Appearance"]

        if klass in self.allowed_classes:
            return True

        if appearance in self.allowed_appearances:
            return True

        return False

    