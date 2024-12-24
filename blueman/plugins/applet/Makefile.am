bluemandir = $(pythondir)/blueman/plugins/applet

blueman_PYTHON = \
    __init__.py \
    AuthAgent.py \
    AutoConnect.py \
    ConnectionNotifier.py \
    DBusService.py \
    KillSwitch.py \
    Menu.py \
    PowerManager.py \
    RemoveBlockedDevice.py \
    DeviceStateSaver.py \
    StatusIcon.py \
    StatusNotifierItem.py \
    SystrayDeviceMenu.py

if HAVE_PULSEAUDIO
blueman_PYTHON += PulseAudioProfile.py
endif

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 

