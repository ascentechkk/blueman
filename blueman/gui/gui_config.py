#!/usr/bin/python3

"""
Lists of elements to display or hide on Blueman GUI
"""

from blueman.gui.manager.Notes import Notes

visible_device_types = [
    'audio-headset',
    'input-keyboard',
    'input-mouse'
]

hidden_device_menu_plugins = [
    Notes
]

enabled_plugins = [
    "PulseAudioProfile.py",
    "AuthAgent.py",
    "AutoConnect.py",
    "ConnectionNotifier.py",
    "DisconnectItems.py",
    "ExitItem.py",
    "KillSwitch.py",
    "PowerManager.py",
    "RecentConns.py",
    "ShowConnected.py",
    "StatusIcon.py",
    "StatusNotifierItem.py",
    "DBusService.py",
    "Menu.py",
    "StandardItems.py"
]

hidden_plugins = [
    "StatusNotifierItem",
    "DBusService",
    "Menu",
    "StandardItems"
]