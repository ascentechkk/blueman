#!/usr/bin/python3

"""
Lists of elements to display or hide on Blueman GUI
"""

from blueman.plugins.manager.Notes import Notes

visible_device_types = [
    'audio-headset',
    'input-keyboard',
    'input-mouse'
]

hidden_device_menu_plugins = [
    Notes
]

disabled_plugins = [
    "DhcpClient.py",
    "DiscvManager.py",
    "GameControllerWakelock.py",
    "NMDUNSupport.py",
    "NMPANSupport.py",
    "NetUsage.py",
    "Networking.py",
    "PPPSupport.py",
    "SerialManager.py",
    "TransferService.py",
    "Notes.py"
]

hidden_plugins = [
    "DhcpClient",
    "DiscvManager",
    "GameControllerWakelock",
    "NMDUNSupport",
    "NMPANSupport",
    "NetUsage",
    "Networking",
    "PPPSupport",
    "SerialManager",
    "TransferService",
    "StatusNotifierItem",
    "DBusService",
    "Menu",
    "StandardItems"
]