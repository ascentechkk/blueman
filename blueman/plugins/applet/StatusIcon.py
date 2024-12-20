from gettext import gettext as _
from operator import itemgetter
from typing import Optional, Tuple, List, Callable, Union, Any
import logging

from gi.repository import GObject, GLib, Gio
from blueman.Functions import launch
from blueman.gui.Notification import Notification, _NotificationBubble, _NotificationDialog
from blueman.main.DBusProxies import ManagerService
from blueman.main.PluginManager import PluginManager
from blueman.plugins.AppletPlugin import AppletPlugin


class StatusIconImplementationProvider:
    def on_query_status_icon_implementation(self) -> Tuple[str, int]:
        return "GtkStatusIcon", 0


class StatusIconVisibilityHandler:
    def on_query_force_status_icon_visibility(self) -> bool:
        return False


class StatusIconProvider:
    def on_status_icon_query_icon(self) -> Optional[str]:
        return None


class StatusIcon(AppletPlugin, GObject.GObject):
    __icon__ = "bluetooth-symbolic"
    __depends__ = ["Menu"]

    visible = None

    visibility_timeout: Optional[int] = None

    __gsettings__ = {
        "schema": "org.blueman.plugins.statusicon",
        "path": None
    }

    __options__ = {
        "toggle-manager-onclick": {
            "type": bool,
            "default": False,
            "name": _("Toggle the manager on clicking the system tray icon"),
            "desc": _("Clicking the system tray icon will toggle the manager instead of focusing on it.")
        }
    }

    _implementations = None

    def on_load(self) -> None:
        GObject.GObject.__init__(self)
        self._tooltip_title = _("Bluetooth Enabled")
        self._tooltip_text = ""

        self.notification: Optional[Union[_NotificationBubble, _NotificationDialog]] = None

        self.general_config = Gio.Settings(schema_id="org.blueman.general")
        self.general_config.connect("changed::symbolic-status-icons", self.on_symbolic_config_change)

        self.query_visibility(emit=False)

        self.parent.Plugins.connect('plugin-loaded', self._on_plugins_changed)
        self.parent.Plugins.connect('plugin-unloaded', self._on_plugins_changed)

        self._add_dbus_method("GetVisibility", (), "b", lambda: self.visible)
        self._add_dbus_signal("VisibilityChanged", "b")
        self._add_dbus_signal("ToolTipTitleChanged", "s")
        self._add_dbus_signal("ToolTipTextChanged", "s")
        self._add_dbus_method("GetToolTipTitle", (), "s", lambda: self._tooltip_title)
        self._add_dbus_method("GetToolTipText", (), "s", lambda: self._tooltip_text)
        self._add_dbus_signal("IconNameChanged", "s")
        self._add_dbus_method("GetStatusIconImplementations", (), "as", self._get_status_icon_implementations)
        self._add_dbus_method("GetIconName", (), "s", self._get_icon_name)
        self._add_dbus_method("Activate", (), "", self.launch_blueman_manager)
        self._add_dbus_method("ActivateBluetoothAndManager", (), "", self.activate_bluetooth_and_manager, is_async=True)

    def activate_bluetooth_and_manager(self, ok: Callable[[Any], None],
                                       err: Callable[[Exception], None]) -> None:
        def on_button_clicked(action: str):
            if action == 'yes':
                ok()
                self.parent.Plugins.PowerManager.request_power_state(True)
                self.launch_blueman_manager()
            else:
                err(Exception('Bluetooth activation cancelled'))
                logging.debug('Bluetooth activation cancelled')
        
        actions: List[Tuple(str, str)] = [('yes', _('Yes')), ('no', _('No'))]
        self.notification = Notification('', _('Bluetooth is off. Would you like to turn it on?'), 0, actions, on_button_clicked, icon_name='blueman')
        self.notification.show()

    def launch_blueman_manager(self) -> None:
        """
        Opens the Bluetooth window
        """
        m: ManagerService = ManagerService()
        if m.get_name_owner() and self.get_option("toggle-manager-onclick"):
            m.quit()
        else:
            m.activate()

    def query_visibility(self, delay_hiding: bool = False, emit: bool = True) -> None:
        self.set_visible(True, emit)

    def on_visibility_timeout(self) -> bool:
        assert self.visibility_timeout is not None
        GLib.source_remove(self.visibility_timeout)
        self.visibility_timeout = None
        self.query_visibility()
        return False

    def set_visible(self, visible: bool, emit: bool) -> None:
        self.visible = visible
        if emit:
            self._emit_dbus_signal("VisibilityChanged", visible)

    def set_tooltip_title(self, title: str) -> None:
        self._tooltip_title = title
        self._emit_dbus_signal("ToolTipTitleChanged", title)

    def set_tooltip_text(self, text: Optional[str]) -> None:
        self._tooltip_text = "" if text is None else text
        self._emit_dbus_signal("ToolTipTextChanged", self._tooltip_text)

    def on_symbolic_config_change(self, settings: Gio.Settings, key: str) -> None:
        self.icon_should_change()

    def icon_should_change(self) -> None:
        self._emit_dbus_signal("IconNameChanged", self._get_icon_name())
        self.query_visibility()

    def on_adapter_added(self, _path: str) -> None:
        self.query_visibility()

    def on_adapter_removed(self, _path: str) -> None:
        self.query_visibility()

    def on_manager_state_changed(self, state: bool) -> None:
        self.query_visibility()
        if state:
            launch('blueman-tray', icon_name='blueman', sn=False)

    def _on_plugins_changed(self, _plugins: PluginManager[AppletPlugin], _name: str) -> None:
        implementations = self._get_status_icon_implementations()
        if not self._implementations or self._implementations != implementations:
            self._implementations = implementations

        if self.parent.manager_state:
            launch('blueman-tray', icon_name='blueman', sn=False)

    def _get_status_icon_implementations(self) -> List[str]:
        return [implementation for implementation, _ in sorted(
            (plugin.on_query_status_icon_implementation()
             for plugin in self.parent.Plugins.get_loaded_plugins(StatusIconImplementationProvider)),
            key=itemgetter(1),
            reverse=True
        )] + ["GtkStatusIcon"]

    def _get_icon_name(self) -> str:
        # default icon name
        name = "blueman"
        for plugin in self.parent.Plugins.get_loaded_plugins(StatusIconProvider):
            icon = plugin.on_status_icon_query_icon()
            if icon is not None:
                # status icon
                name = icon

        # depending on configuration, ensure fullcolor icons..
        name = name.replace("-symbolic", "")
        if self.general_config.get_boolean("symbolic-status-icons"):
            # or symbolic
            name = f"{name}-symbolic"

        return name
