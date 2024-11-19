from gettext import gettext as _
import logging
from typing import TYPE_CHECKING, Callable, Tuple, Optional
from blueman.bluemantyping import ObjectPath

import gi

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerToolbar:
    def __init__(self, blueman: "Blueman") -> None:
        self.blueman = blueman

        self.blueman.List.connect("device-selected", self.on_device_selected)
        self.blueman.List.connect("device-property-changed", self.on_device_propery_changed)
        self.blueman.List.connect("adapter-changed", self.on_adapter_changed)
        self.blueman.List.connect("adapter-property-changed", self.on_adapter_property_changed)

        self.b_search = blueman.builder.get_widget("b_search", Gtk.ToolButton)
        self.b_search.connect("clicked", lambda button: blueman.inquiry())

        self.on_adapter_changed(blueman.List, blueman.List.get_adapter_path())

    def on_adapter_property_changed(self, _lst: ManagerDeviceList, adapter: Adapter,
                                    key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if key == "Discovering" or key == "Powered":
            self._update_buttons(adapter)

    def on_adapter_changed(self, _lst: ManagerDeviceList, adapter_path: Optional[ObjectPath]) -> None:
        logging.debug(f"toolbar adapter {adapter_path}")
        self._update_buttons(None if adapter_path is None else Adapter(obj_path=adapter_path))

    def on_device_selected(
        self,
        dev_list: ManagerDeviceList,
        device: Optional[Device],
        _tree_iter: Gtk.TreeIter,
    ) -> None:
        self._update_buttons(dev_list.Adapter)

    def _update_buttons(self, adapter: Optional[Adapter]) -> None:
        powered = adapter is not None and adapter["Powered"]
        self.b_search.props.sensitive = powered and not (adapter and adapter["Discovering"])           

    def on_device_propery_changed(self, dev_list: ManagerDeviceList, device: Device, tree_iter: Gtk.TreeIter,
                                  key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if dev_list.compare(tree_iter, dev_list.selected()):
            if key == "Trusted" or key == "Paired" or key == "UUIDs" or key == "Connected":
                self.on_device_selected(dev_list, device, tree_iter)
