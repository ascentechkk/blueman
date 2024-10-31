from gettext import gettext as _
from typing import Optional

from blueman.Functions import launch
from blueman.main.DBusProxies import ManagerService
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.CommonUi import show_about_dialog
from blueman.gui.applet.PluginDialog import PluginDialog

import gi

from blueman.plugins.applet.PowerManager import PowerManager, PowerStateListener

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk


class StandardItems(AppletPlugin, PowerStateListener):
    __depends__ = ["Menu"]
    __unloadable__ = False
    __description__ = _("Adds standard menu items to the status icon menu")
    __author__ = "walmis"

    __gsettings__ = {
        "schema": "org.blueman.plugins.standarditems",
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

    def on_devices(self) -> None:
        m = ManagerService()
        if m.get_name_owner() and self.get_option("toggle-manager-onclick"):
            m.quit()
        else:
            m.activate()
