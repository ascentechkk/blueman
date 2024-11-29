bluemandir = $(pythondir)/blueman/plugins/applet

blueman_PYTHON = \
    __init__.py \
    AuthAgent.py \
    AutoConnect.py \
    ConnectionNotifier.py \
    DBusService.py \
    DisconnectItems.py \
    KillSwitch.py \
    Menu.py \
    PowerManager.py \
    RecentConns.py \
    SavePairedStates.py \
    ShowConnected.py \
    StatusIcon.py \
    StandardItems.py \
    StatusNotifierItem.py

if HAVE_PULSEAUDIO
blueman_PYTHON += PulseAudioProfile.py
endif

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 

