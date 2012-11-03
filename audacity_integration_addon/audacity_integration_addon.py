# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os
import time

from aqt import editor, addons, mw

import install

def addons_folder(): return mw.pm.addonFolder()

ADDON_NAME = "audacity_integration_addon"

READY_DROP_LOCATION = os.path.join(addons_folder(), ADDON_NAME, "ready")
MEDIA_DROP_LOCATION = os.path.join(addons_folder(), ADDON_NAME, "media-file")
ALREADY_INSTALLED_PATH = os.path.join(addons_folder(), ADDON_NAME, "already-installed.txt")

def already_installed():
    f = open(ALREADY_INSTALLED_PATH)
    state = f.readline()
    f.close()
    if state.startswith("True"):
        return True
    else:
        return False

def update_installed():
    f = open(ALREADY_INSTALLED_PATH, 'w')
    state = f.write("True")
    f.close()

def audacity_integration_setupWatcher(self):
    self.audacity_integration_watcher = QFileSystemWatcher()
    self.audacity_integration_watcher.addPath(READY_DROP_LOCATION)
    
def audacity_integration_listenToWatcher(self):
    QObject.connect(self.audacity_integration_watcher,
                    SIGNAL("directoryChanged(QString)"),
                    self.audacity_integration_get_media)

def audacity_integration_get_media(self):
    media = os.listdir(MEDIA_DROP_LOCATION)
    ready = os.listdir(READY_DROP_LOCATION)
    # Sort the contents by alphabetical order to ensure deterministic
    # behaviour. If we have more than a file there, something's wrong, 
    # but at least it will be deterministically wrong.
    media.sort()
    self.audacity_integration_watcher.removePath(READY_DROP_LOCATION)

    for fname in media:
        self.addMedia(os.path.join(MEDIA_DROP_LOCATION, fname),
                      canDelete=False)
    #time.sleep(0.05)
    clear_dir(MEDIA_DROP_LOCATION)
    clear_dir(READY_DROP_LOCATION)
    
    self.audacity_integration_watcher.addPath(READY_DROP_LOCATION)
        
def clear_dir(dir):
    contents = os.listdir(dir)
    for f in contents:
        while True:
            try:
                os.remove(os.path.join(dir, f))
                break
            except:
                time.sleep(0.01)

def new__init__(self, *args, **kwargs):
    old__init__(self, *args, **kwargs)
    clear_dir(READY_DROP_LOCATION)
    clear_dir(MEDIA_DROP_LOCATION)
    self.audacity_integration_setupWatcher()
    self.audacity_integration_listenToWatcher()

editor.Editor.audacity_integration_get_media = audacity_integration_get_media
editor.Editor.audacity_integration_setupWatcher = audacity_integration_setupWatcher
editor.Editor.audacity_integration_listenToWatcher = audacity_integration_listenToWatcher

old__init__ = editor.Editor.__init__
editor.Editor.__init__ = new__init__

if not already_installed():
    install.audacity_integration_install()
    update_installed()