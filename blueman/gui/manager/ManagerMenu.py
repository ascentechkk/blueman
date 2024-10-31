from gettext import gettext as _
import logging
from typing import Dict, Tuple, TYPE_CHECKING, Any, Optional, Sequence
from blueman.bluemantyping import ObjectPath

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.bluez.Manager import Manager
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.gui.CommonUi import show_about_dialog
from blueman.Constants import WEBSITE
from blueman.Functions import launch, adapter_path_to_name

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerMenu:
    def __init__(self, blueman: "Blueman"):
        self.blueman = blueman

        self.item_device = self.blueman.builder.get_widget("item_device", Gtk.MenuItem)

        self.device_menu: Optional[ManagerDeviceMenu] = None

        blueman.List.connect("device-selected", self.on_device_selected)

    def on_device_selected(self, _lst: ManagerDeviceList, device: Optional[Device], tree_iter: Gtk.TreeIter) -> None:
        if tree_iter and device:
            self.item_device.props.sensitive = True

            if self.device_menu is None:
                self.device_menu = ManagerDeviceMenu(self.blueman)
                self.item_device.set_submenu(self.device_menu)
            else:
                def idle() -> bool:
                    assert self.device_menu is not None  # https://github.com/python/mypy/issues/2608
                    self.device_menu.generate()
                    return False
                GLib.idle_add(idle, priority=GLib.PRIORITY_LOW)

        else:
            self.item_device.props.sensitive = False

    def _update_power(self) -> None:
        if self.device_menu is not None:
            self.device_menu.generate()
