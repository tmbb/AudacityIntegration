# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os 
import shutil
import tempfile
import simplejson
import time
import datetime

from aqt import editor, addons, mw
from anki.sound import play


def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt4.QtCore import pyqtRemoveInputHook
  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()


def addons_folder():
    return addons.AddonManager(mw).addonsFolder()

drop_location = os.path.join(addons_folder(),
                             "pick_up_media_addon",
                             "media-file")

playsound = False

no_media_message = '''
You have no media in the Drop Location!
Drop there some media and retry.
If you have already dropped some media, something is wrong.
'''

def pick_up_media_setupWatcher(self):
    self.pick_up_media_watcher = QFileSystemWatcher()
    self.pick_up_media_watcher.addPath(drop_location)
    
def pick_up_media_listenToWatcher(self):
    QObject.connect(self.pick_up_media_watcher,
                    SIGNAL("directoryChanged(QString)"),
                    self.pick_up_media_get_media_if_any)

def pick_up_media_get_media_if_any(self):
    contents = os.listdir(drop_location)
    if contents:
        # Sort the contents by alphabetical order to ensure deterministic
        # behaviour. If we have more than a file there, something's wrong, 
        # but at least it will be predictably wrong.
        contents.sort()
        basename = contents[0]
        fname = os.path.join(drop_location, basename)
        
        self.pick_up_media_watcher.removePath(drop_location)
        time.sleep(0.8)
        
        self.pick_up_media_addMedia(fname)
        clear_drop_location()
        self.pick_up_media_watcher.addPath(drop_location)
        
def clear_drop_location():
    contents = os.listdir(drop_location)
    for f in contents:
        while True:
            try:
                os.remove(os.path.join(drop_location, f))
                break
            except:
                time.sleep(0.05)

def new__init__(self, *args, **kwargs):
    old__init__(self, *args, **kwargs)
    self.pick_up_media_setupWatcher()
    self.pick_up_media_listenToWatcher()
    clear_drop_location()

def pick_up_media_addMedia(self, path):
    html = self._pick_up_media_addMedia(path, canDelete=False)
    self.web.eval("setFormat('inserthtml', %s);" % simplejson.dumps(html))

def _pick_up_media_addMedia(self, path, canDelete=False):
        "Add to media folder and return basename."
        pics = ("jpg", "jpeg", "png", "tif", "tiff", "gif")
        # copy to media folder
        name = self.mw.col.media.addFile(path)
        # remove original?
        if canDelete and self.mw.pm.profile['deleteMedia']:
            if os.path.abspath(name) != os.path.abspath(path):
                try:
                    os.unlink(old)
                except:
                    pass
        # return a local html link
        ext = name.split(".")[-1].lower()
        if ext in pics:
            return '<img src="%s">' % name
        # TODO: use inkscape to convert if it is an svg file!
        else:
            # Don't play sound!
            return '[sound:%s]' % name



editor.Editor.pick_up_media_get_media_if_any = pick_up_media_get_media_if_any
editor.Editor.pick_up_media_setupWatcher = pick_up_media_setupWatcher
editor.Editor.pick_up_media_listenToWatcher = pick_up_media_listenToWatcher
editor.Editor._pick_up_media_addMedia = _pick_up_media_addMedia
editor.Editor.pick_up_media_addMedia = pick_up_media_addMedia

old__init__ = editor.Editor.__init__
editor.Editor.__init__ = new__init__