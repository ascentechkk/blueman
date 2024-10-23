import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class WarningMessageDialog(Gtk.MessageDialog):
    def __init__(self, message: str) -> None:
        super().__init__(parent = None,
                         type = Gtk.MessageType.WARNING,
                         buttons = Gtk.ButtonsType.OK,
                         text = message)
        width = 350
        height = 100

        self.set_title("Warning")
        self.set_default_size(width, height)
        self.connect("response", self.on_response)

    def on_response(self, dialog, response_id):
        dialog.destroy()