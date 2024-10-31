#!/usr/bin/python3
"""
Filters GUI Elements
"""

from blueman.bluez.Device import Device


allowd_classes = [
    0x000404, # Wearable Headset Device
    0x000408, # Hands-free Device
    0x000410, # Microphone
    0x000414, # Loudspeaker
    0x000418, # Headphones
    0x00041c, # Portable Audio
    0x000420, # Car Audio
    0x000428, # HiFi Audio Device
    0x000540, # Mouse
    0x000580, # Keyboard
    0x0005c0, # Combo Mouse/Keyboard
]


allowed_appearances = [
    0x03c1, # Mouse
    0x03c2, # Keyboard
    0x0840, # Generic Audio Sink
    0x0841, # Standalone Speaker
    0x0842, # Soundbar
    0x0843, # Bookshelf Speaker
    0x0844, # Standmounted Speaker
    0x0845, # Speakerphone
    0x0881, # Microphone
    0x0940, # Generic Wearable Audio Device
    0x0941, # Earbud
    0x0942, # Headset
    0x0943, # Headphones
    0x0944, # Neck Band
]


def get_allowed_device(path: str) -> bool:
    device = Device(obj_path=path)
    klass = device["Class"] & 0xfff
    appearance = device["Appearance"]

    if klass in allowd_classes:
        return True

    if appearance in allowed_appearances:
        return True

    return False

