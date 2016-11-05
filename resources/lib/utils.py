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

CATEGORIES = {
              'movies':{
                       'enabled':False, 
                       'type':'movies', 
                       'method':'VideoLibrary.GetMovies', 
                       'properties':MOVIELABELS, 
                       'sort':'title', 
                       'rule':'{"field":"title", "operator":"contains", "value":"%s"}',
                       'cast':True, 
                       'streamdetails':True, 
                       'label':342, 
                       'icon':'DefaultVideo.png', 
                       'media':'video', 
                       'control':110
                       }, 
              'tvshows':{
                         'enabled':False, 
                         'type':'tvshows', 
                         'method':'VideoLibrary.GetTVShows', 
                         'properties':TVSHOWLABELS, 
                         'sort':'label', 
                         'rule':'{"field":"title", "operator":"contains", "value":"%s"}',
                         'cast':True, 
                         'streamdetails':False, 
                         'label':20343, 
                         'icon':'DefaultVideo.png', 
                         'media':'video', 
                         'control':120
                        }, 
              'seasons':{
                         'enabled':False, 
                         'type':'seasons', 
                         'method':'VideoLibrary.GetSeasons', 
                         'properties':SEASONLABELS, 
                         'sort':'label', 
                         'rule':'{"field":"title", "operator":"contains", "value":"%s"}',
                         'cast':False, 
                         'streamdetails':False, 
                         'label':20373, 
                         'icon':'DefaultVideo.png', 
                         'media':'video', 
                         'control':130
                        }, 
              'episodes':{
                         'enabled':False, 
                         'type':'episodes', 
                         'method':'VideoLibrary.GetEpisodes', 
                         'properties':EPISODELABELS, 
                         'sort':'title', 
                         'rule':'{"field":"title", "operator":"contains", "value":"%s"}',
                         'cast':True, 
                         'streamdetails':True, 
                         'label':20360, 
                         'icon':'DefaultVideo.png', 
                         'media':'video', 
                         'control':140
                         }, 
              'musicvideos':{
                         'enabled':False, 
                         'type':'musicvideos', 
                         'method':'VideoLibrary.GetMusicVideos', 
                         'properties':MUSICVIDEOLABELS, 
                         'sort':'label', 
                         'rule':'{"field":"title", "operator":"contains", "value":"%s"}',
                         'cast':False, 
                         'streamdetails':True, 
                         'label':20389, 
                         'icon':'DefaultVideo.png', 
                         'media':'video', 
                         'control':150
                            }, 
              'artists':{
                       'enabled':False, 
                       'type':'artists', 
                       'method':'AudioLibrary.GetArtists', 
                       'properties':ARTISTLABELS, 
                       'sort':'label', 
                       'rule':'{"field": "artist", "operator": "contains", "value": "%s"}',
                       'cast':False, 
                       'streamdetails':False, 
                       'label':133, 
                       'icon':'DefaultArtist.png', 
                       'media':'music', 
                       'control':160
                        }, 
              'albums':{
                       'enabled':False, 
                       'type':'albums', 
                       'method':'AudioLibrary.GetAlbums', 
                       'properties':ALBUMLABELS, 
                       'sort':'label', 
                       'rule':'{"field": "album", "operator": "contains", "value": "%s"}',
                       'cast':False, 
                       'streamdetails':False, 
                       'label':132, 
                       'icon':'DefaultAlbumCover.png', 
                       'media':'music', 
                       'control':170
                       }, 
              'songs':{
                       'enabled':False, 
                       'type':'songs', 
                       'method':'AudioLibrary.GetSongs', 
                       'properties':SONGLABELS, 
                       'sort':'title', 
                       'rule':'{"field": "title", "operator": "contains", "value": "%s"}',
                       'cast':False, 
                       'streamdetails':False, 
                       'label':134, 
                       'icon':'DefaultAudio.png', 
                       'media':'music', 
                       'control':180
                      }, 
              'actors':{
                        'enabled':False, 
                        'type':'actors', 
                        'method':'VideoLibrary.GetMovies', 
                        'properties':MOVIELABELS, 
                        'sort':'title', 
                        'rule':'{"field":"actor", "operator":"contains", "value":"%s"}',
                        'cast':True, 
                        'streamdetails':True, 
                        'label':344, 
                        'icon':'DefaultMovie.png', 
                        'media':'video', 
                        'control':210
                       }, 
              'directors':{
                           'enabled':False, 
                           'type':'directors', 
                           'method':'VideoLibrary.GetMovies', 
                           'properties':MOVIELABELS, 
                           'sort':'title', 
                           'rule':'{"field":"director", "operator":"contains", "value":"%s"}',
                           'cast':True, 
                           'streamdetails':True, 
                           'label':20348, 
                           'icon':'DefaultMovie.png', 
                           'media':'video', 
                           'control':230
                          }, 
              'epg':{
                     'enabled':False
                     'type':'epg', 
                    }
             }

def log(txt):
    if isinstance(txt,str):
        txt = txt.decode('utf-8')
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)
