import sys
import re
import xbmc
import xbmcgui

ADDON = sys.modules['__main__'].ADDON
ADDONID = sys.modules['__main__'].ADDONID
ADDONVERSION = sys.modules['__main__'].ADDONVERSION
LANGUAGE = sys.modules['__main__'].LANGUAGE
CWD = sys.modules['__main__'].CWD

ACTION_CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)
ACTION_CONTEXT_MENU = (117,)
ACTION_OSD = (107, 163,)
ACTION_SHOW_GUI = (18,)
ACTION_SHOW_INFO = (11,)

CATEGORIES = {'self.movies':'movies', 'self.tvshows':'tvshows', 'self.episodes':'episodes', 'self.musicvideos':'musicvideos', 'self.artists':'artists', 'self.albums':'albums', 
              'self.songs':'songs', 'self.actors':'actors', 'self.directors':'directors', 'self.epg':'epg'}

MOVIELABELS = ["genre", "country", "year", "top250", "setid", "rating", "userrating", "playcount", "cast", "director", "mpaa", "plot", "plotoutline", "title", "originaltitle", "sorttitle", 
               "runtime", "studio", "tagline", "writer", "premiered", "set", "imdbnumber", "lastplayed", "votes", "trailer", "dateadded", "streamdetails", "art"]

TVSHOWLABELS = ["genre", "year", "episode", "season", "rating", "userrating", "playcount", "cast", "mpaa", "plot", "title", "originaltitle", "sorttitle", "runtime", "studio", "premiered", 
                "imdbnumber", "lastplayed", "votes", "dateadded", "art"]

SEASONLABELS = ["episode", "season", "showtitle", "tvshowid", "userrating", "watchedepisodes", "playcount", "art"]

EPISODELABELS = ["episode", "season", "rating", "userrating", "playcount", "cast", "director", "plot", "title", "originaltitle", "runtime", "writer", "showtitle", "firstaired", "lastplayed", 
                 "votes", "dateadded", "streamdetails", "art"]

MUSICVIDEOLABELS = ["genre", "year", "rating", "userrating", "playcount", "director", "plot", "title", "runtime", "studio", "premiered", "lastplayed", "album", "artist", "dateadded", 
                    "streamdetails", "art"]

ARTISTLABELS = ["genre", "description", "formed", "disbanded", "born", "yearsactive", "died", "mood", "style", "instrument", "thumbnail", "fanart"]

ALBUMLABELS = ["title", "description", "albumlabel", "artist", "genre", "year", "thumbnail", "fanart", "theme", "type", "mood", "style", "rating", "userrating"]

SONGLABELS = ["title", "artist", "album", "genre", "duration", "year", "file", "thumbnail", "fanart", "comment", "rating", "userrating", "track", "playcount"]


def log(txt):
    if isinstance(txt,str):
        txt = txt.decode('utf-8')
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)
