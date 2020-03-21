import os
import sys
from urllib.parse import unquote_plus
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
LANGUAGE = ADDON.getLocalizedString
CWD = ADDON.getAddonInfo('path')


if (__name__ == '__main__'):
    searchstring = None
    try:
        params = dict(arg.split('=') for arg in sys.argv[ 1 ].split('&'))
    except:
        params = {}
    searchstring = params.get('searchstring','')
    searchstring = unquote_plus(searchstring)
    if searchstring == '':
        keyboard = xbmc.Keyboard('', LANGUAGE(32101), False)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            searchstring = keyboard.getText()
    else:
        del params['searchstring']
    if searchstring:
        from lib import gui
        ui = gui.GUI('script-globalsearch.xml', CWD, 'default', '1080i', True, searchstring=searchstring, params=params)
        ui.doModal()
        del ui
