import sys
import datetime
import re
import xbmc
import xbmcgui
import infodialog
import json
import operator

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

#TODO use label or title?

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


class GUI(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        # some sanitize work for search string: strip the input and replace some chars
        self.searchstring = self._clean_string(kwargs['searchstring']).strip()
        self.params = kwargs['params']
        log('script version %s started' % ADDONVERSION)
        self.nextsearch = False

    def onInit(self):
        if self.searchstring == '':
            self._close()
        else:
            self.window_id = xbmcgui.getCurrentWindowDialogId()
            xbmcgui.Window(self.window_id).setProperty('GlobalSearch.SearchString', self.searchstring)
            self.ACTORSUPPORT = True
            self.DIRECTORSUPPORT = True
            self.EPGSUPPORT = True
            self._hide_controls()
            if not self.nextsearch:
                self.categories = {}
                if self.params == {}:
                    self._load_settings()
                else:
                    self._parse_argv()
            self._reset_variables()
            self._init_items()
            self._fetch_items()

    def _fetch_items(self):
        if self.categories['self.movies'] == 'true':
            self._fetch_movies('title', 342, 111)
        if self.categories['self.tvshows'] == 'true':
            self._fetch_tvshows()
        if self.categories['self.episodes'] == 'true':
            self._fetch_episodes()
        if self.categories['self.musicvideos'] == 'true':
            self._fetch_musicvideos()
        if self.categories['self.artists'] == 'true':
            self._fetch_artists()
        if self.categories['self.albums'] == 'true':
            self._fetch_albums()
        if self.categories['self.songs'] == 'true':
            self._fetch_songs()
        if self.categories['self.actors'] == 'true':
            self._fetch_movies('actor', 344, 211)
        if self.categories['self.epg'] == 'true':
            self._fetch_channelgroups()
        if self.categories['self.directors'] == 'true':
            self._fetch_movies('director', 20348, 231)
        self._check_focus()

    def _hide_controls(self):
        for cid in [119, 129, 139, 149, 159, 169, 179, 189, 219, 229, 239, 189, 199]:
            self.getControl(cid).setVisible(False)

    def _reset_controls(self):
        for cid in [111, 121, 131, 141, 151, 161, 171, 181, 211, 231]:
            self.getControl(cid).reset()

    def _parse_argv(self):
        for key, value in CATEGORIES.iteritems():
            self.categories[key] = self.params.get(value, '')

    def _load_settings(self):
        for key, value in CATEGORIES.iteritems():
            self.categories[key] = ADDON.getSetting(value)

    def _reset_variables(self):
        self.focusset= 'false'
        self.getControl(190).setLabel(xbmc.getLocalizedString(194))

    def _init_items(self):
        self.fetch_seasonepisodes = 'false'
        self.fetch_albumssongs = 'false'
        self.fetch_songalbum = 'false'
        self.playingtrailer = 'false'
        self.getControl(198).setLabel(LANGUAGE(32299))
        self.Player = MyPlayer(function=self._trailerstopped)

    def _fetch_movies(self, query, label, control):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(label))
        count = 0
        if query == 'movies':
            rule = '{"or": [{"field":"title", "operator":"contains", "value":"%s"}, {"field":"originaltitle", "operator":"contains", "value":"%s"}]}' % (self.searchstring, self.searchstring)
        else:
            rule = '{"field":"%s", "operator":"contains", "value":"%s"}' % (query, self.searchstring)
        json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetMovies", "params":{"properties":%s, "sort":{"method":"label"}, "filter": %s}, "id": 1}' % (json.dumps(MOVIELABELS), rule))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('movies'):
            for item in json_response['result']['movies']:
                count += 1
                listitem = xbmcgui.ListItem(item['title'])
                listitem.setArt(self._get_art(item['art'], 'DefaultMovie.png', 'video'))
                for stream in item['streamdetails']['video']:
                    listitem.addStreamInfo('video', stream)
                for stream in item['streamdetails']['audio']:
                    listitem.addStreamInfo('audio', stream)
                for stream in item['streamdetails']['subtitle']:
                    listitem.addStreamInfo('subtitle', stream)
                listitem.setCast(item['cast'])
                listitem.setInfo('video', self._get_info(item, 'movie'))
                listitems.append(listitem)
        self.getControl(control).addItems(listitems)
        if count > 0:
            self.getControl(control - 1).setLabel(str(count))
            self.getControl(control + 8).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(control))
                self.focusset = 'true'

    def _fetch_tvshows(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(20343))
        count = 0
        json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params":{"properties":%s, "sort":{"method":"label"}, "filter":{"field": "title", "operator": "contains", "value":"%s"}}, "id":1}' % (json.dumps(TVSHOWLABELS), self.searchstring))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('tvshows'):
            for item in json_response['result']['tvshows']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['title'])
                listitem.setArt(self._get_art(item['art'], 'DefaultMovie.png', 'video'))
                listitem.setCast(item['cast'])
                listitem.setInfo('video', self._get_info(item, 'tvshow'))
                listitems.append(listitem)
        self.getControl(121).addItems(listitems)
        if count > 0:
            self.getControl(120).setLabel(str(count))
            self.getControl(129).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(121))
                self.focusset = 'true'

    def _fetch_seasons(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(20343))
        count = 0
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasons", "params": {"properties": %s, "sort": { "method": "label" }, "tvshowid":%s }, "id": 1}' % (json.dumps(SEASONLABELS), self.tvshowid))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('seasons'):
            for item in json_response['result']['seasons']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item['art'], 'DefaultFolder.png', 'video'))
                listitem.setInfo('video', self._get_info(item, 'season'))
                listitems.append(listitem)
        self.getControl(131).addItems(listitems)
        if count > 0:
            self.foundseasons = 'true'
            self.getControl(130).setLabel(str(count))
            self.getControl(139).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(131))
                self.focusset = 'true'

    def _fetch_episodes(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(20360))
        count = 0
        if self.fetch_seasonepisodes == 'true':
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "properties": %s, "sort": { "method": "title" }, "tvshowid":%s }, "id": 1}' % (json.dumps(EPISODELABELS), self.tvshowid))
        else:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "properties": %s, "sort": { "method": "title" }, "filter": {"field": "title", "operator": "contains", "value": "%s"} }, "id": 1}' % (json.dumps(EPISODELABELS), self.searchstring))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('episodes'):
            for item in json_response['result']['episodes']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item['art'], 'DefaultVideo.png', 'video'))
                listitem.setInfo('video', self._get_info(item, 'episode'))
                listitems.append(listitem)
        self.getControl(141).addItems(listitems)
        if count > 0:
            self.getControl(140).setLabel(str(count))
            self.getControl(149).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(141))
                self.focusset = 'true'

    def _fetch_musicvideos(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(20389))
        count = 0
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": %s, "sort": { "method": "label" }, "filter": {"field": "title", "operator": "contains", "value": "%s"} }, "id": 1}' % (json.dumps(MUSICVIDEOLABELS), self.searchstring))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('musicvideos'):
            for item in json_response['result']['musicvideos']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item['art'], 'DefaultVideo.png'))
                listitem.setInfo('video', self._get_info(item, 'musicvideo'))
                listitems.append(listitem)
        self.getControl(151).addItems(listitems)
        if count > 0:
            self.getControl(150).setLabel(str(count))
            self.getControl(159).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(151))
                self.focusset = 'true'

    def _fetch_artists(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(133))
        count = 0
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": %s, "sort": { "method": "label" }, "filter": {"field": "artist", "operator": "contains", "value": "%s"} }, "id": 1}' % (json.dumps(ARTISTLABELS), self.searchstring))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('artists'):
            for item in json_response['result']['artists']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item, 'DefaultArtist.png', 'music'))
                info, props = self._split_labels(item, ARTISTLABELS, 'artist_')
                for key, value in props.iteritems():
                    listitem.setProperty(key, str(value))
                listitem.setInfo('music', self._get_info(info, 'artist'))
                listitems.append(listitem)
        self.getControl(161).addItems(listitems)
        if count > 0:
            self.getControl(160).setLabel(str(count))
            self.getControl(169).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(161))
                self.focusset = 'true'

    def _fetch_albums(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(132))
        count = 0
        if self.fetch_albumssongs == 'true':
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": %s, "sort": { "method": "label" }, "filter": {"artistid": %s} }, "id": 1}' % (json.dumps(ALBUMLABELS), self.artistid))
        else:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": %s, "sort": { "method": "label" }, "filter": {"field": "album", "operator": "contains", "value": "%s"} }, "id": 1}' % (json.dumps(ALBUMLABELS), self.searchstring))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('albums'):
            for item in json_response['result']['albums']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item, 'DefaultAlbumCover.png', 'music'))
                info, props = self._split_labels(item, ALBUMLABELS, 'album_')
                for key, value in props.iteritems():
                    listitem.setProperty(key, str(value))
                listitem.setInfo('music', self._get_info(info, 'album'))
                listitems.append(listitem)
        self.getControl(171).addItems(listitems)
        if count > 0:
            self.getControl(170).setLabel(str(count))
            self.getControl(179).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(171))
                self.focusset = 'true'

    def _fetch_songs(self):
        listitems = []
        self.getControl(191).setLabel(xbmc.getLocalizedString(134))
        count = 0
        if self.fetch_albumssongs == 'true':
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": %S, "sort": { "method": "title" }, "filter": {"artistid": %s} }, "id": 1}' % (json.dumps(SONGLABELS), self.artistid))
        else:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": %s, "sort": { "method": "title" }, "filter": {"field": "title", "operator": "contains", "value": "%s"} }, "id": 1}' % (json.dumps(SONGLABELS), self.searchstring))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key('songs'):
            for item in json_response['result']['songs']:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item, 'DefaultAudio.png', 'music'))
                listitem.setInfo('music', self._get_info(item, 'song'))
                listitems.append(listitem)
        self.getControl(181).addItems(listitems)
        if count > 0:
            self.getControl(180).setLabel(str(count))
            self.getControl(189).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(181))
                self.focusset = 'true'

    def _fetch_channelgroups(self):
        self.getControl(191).setLabel(xbmc.getLocalizedString(19069))
        channelgrouplist = []
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "PVR.GetChannelGroups", "params": {"channeltype": "tv"}, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if(json_response.has_key('result')) and(json_response['result'] != None) and(json_response['result'].has_key('channelgroups')):
            for item in json_response['result']['channelgroups']:
                channelgrouplist.append(item['channelgroupid'])
            if channelgrouplist:
                self._fetch_channels(channelgrouplist)

    def _fetch_channels(self, channelgrouplist):
        # get all channel id's
        channellist = []
        for channelgroupid in channelgrouplist:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "PVR.GetChannels", "params": {"channelgroupid": %i, "properties": ["channel", "thumbnail"]}, "id": 1}' % channelgroupid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = json.loads(json_query)
            if(json_response.has_key('result')) and(json_response['result'] != None) and(json_response['result'].has_key('channels')):
                for item in json_response['result']['channels']:
                    channellist.append(item)
        if channellist:
            # remove duplicates
            channels = [dict(tuples) for tuples in set(tuple(item.items()) for item in channellist)]
            # sort
            channels.sort(key=operator.itemgetter('channelid'))
            self._fetch_epg(channels)

    def _fetch_epg(self, channels):
        listitems = []
        count = 0
        # get all programs for every channel id
        for channel in channels:
            channelid = channel['channelid']
            channelname = channel['label']
            channelthumb = channel['thumbnail']
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "PVR.GetBroadcasts", "params": {"channelid": %i, "properties": ["starttime", "endtime", "runtime", "genre", "plot"]}, "id": 1}' % channelid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = json.loads(json_query)
            if(json_response.has_key('result')) and(json_response['result'] != None) and(json_response['result'].has_key('broadcasts')):
                for item in json_response['result']['broadcasts']:
                    broadcastname = item['label']
                    epgmatch = re.search('.*' + self.searchstring + '.*', broadcastname, re.I)
                    if epgmatch:
                        count = count + 1
                        broadcastid = item['broadcastid']
                        duration = item['runtime']
                        genre = item['genre'][0]
                        plot = item['plot']
                        starttime = item['starttime']
                        endtime = item['endtime']
                        listitem = xbmcgui.ListItem(label=broadcastname, iconImage='DefaultFolder.png', thumbnailImage=channelthumb)
                        listitem.setProperty("icon", channelthumb)
                        listitem.setProperty("genre", genre)
                        listitem.setProperty("plot", plot)
                        listitem.setProperty("starttime", starttime)
                        listitem.setProperty("endtime", endtime)
                        listitem.setProperty("duration", str(duration))
                        listitem.setProperty("channelname", channelname)
                        listitem.setProperty("dbid", str(channelid))
                        listitems.append(listitem)
        self.getControl(221).addItems(listitems)
        if count > 0:
            self.getControl(220).setLabel(str(count))
            self.getControl(229).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(221))
                self.focusset = 'true'

    def _get_info(self, info, item):
        labels = {}
        for key, value in info.iteritems():
           if isinstance(value, list):
               value = " / ".join(value)
           labels[key] = value
        labels['mediatype'] = item
        labels['dbid'] = labels['%sid' % item]
        del labels['%sid' % item]
        labels['title'] = labels['label']
        del labels['label']
        if item != 'artist' and item != 'album' and item != 'song' and item != 'epg':
            del labels['art']
        else:
            del labels['thumbnail']
            del labels['fanart']
        if item == 'movie' or item == 'tvshow' or item == 'episode' or item == 'musicvideo':
            labels['duration'] = labels['runtime'] # we does json return runtime instead of duration?
            del labels['runtime']
            if item != 'musicvideo':
                del labels['cast']
            if item != 'tvshow':
                del labels['streamdetails']
        if item == 'song':
            labels['tracknumber'] = labels['track']
            del labels['track']
            del labels['file']
        return labels

    def _get_art(self, labels, icon, media):
        if media == 'video':
            labels['icon'] = icon
            if labels.get('poster'):
                labels['thumb'] = labels['poster']
            elif labels.get('banner'):
                labels['thumb'] = labels['banner']
        else:
            art = {}
            art['icon'] = icon
            art['thumb'] = labels['fanart']
            art['fanart'] = labels['fanart']
            labels = art
        return labels

    def _split_labels(self, item, labels, prefix):
        props = {}
        for label in labels:
            if label == 'thumbnail' or label == 'fanart' or label == 'rating' or label == 'userrating' or (prefix == 'album_' and (label == 'genre' or label == 'year')):
                continue
            props[prefix + label] = item[label]
            del item[label]
        return item, props

    def _clean_string(self, string):
        return string.replace('(', '[(]').replace(')', '[)]').replace('+', '[+]')

    def _getTvshow_Seasons(self):
        self.fetch_seasonepisodes = 'true'
        listitem = self.getControl(121).getSelectedItem()
        self.tvshowid = listitem.getVideoInfoTag().getDbId()
        self.searchstring = self._clean_string(listitem.getLabel())
        self._reset_results(self._fetch_seasons)
        self.fetch_seasonepisodes = 'false'

    def _getTvshow_Episodes(self):
        self.fetch_seasonepisodes = 'true'
        listitem = self.getControl(121).getSelectedItem()
        self.tvshowid = listitem.getProperty('dbid')
        self.searchstring = self._clean_string(listitem.getLabel())
        self._reset_results(self._fetch_episodes)
        self.fetch_seasonepisodes = 'false'

    def _getArtist_Albums(self):
        self.fetch_albumssongs = 'true'
        listitem = self.getControl(161).getSelectedItem()
        self.artistid = listitem.getProperty('dbid')
        self.searchstring = self._clean_string(listitem.getLabel())
        self._reset_results(self._fetch_albums)
        self.fetch_albumssongs = 'false'

    def _getArtist_Songs(self):
        self.fetch_albumssongs = 'true'
        listitem = self.getControl(161).getSelectedItem()
        self.artistid = listitem.getProperty('dbid')
        self.searchstring = self._clean_string(listitem.getLabel())
        self._reset_results(self._fetch_songs)
        self.fetch_albumssongs = 'false'

    def _getSong_Album(self):
        self.fetch_songalbum = 'true'
        listitem = self.getControl(181).getSelectedItem()
        self.artistname = listitem.getProperty('artist')
        self.searchstring = self._clean_string(listitem.getProperty('album'))
        self._reset_results(self._fetch_albums)
        self.fetch_songalbum = 'false'

    def _reset_results(self, action):
        self._reset_variables()
        self._hide_controls()
        self._reset_controls()
        action()
        self._check_focus()

    def _play_video(self, path):
        self._close()
        xbmc.Player().play(path)

    def _play_audio(self, path, listitem):
        self._close()
        xbmc.Player().play(path, listitem)

    def _play_album(self):
        self._close()
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.Open", "params":{"item":{"albumid":%d}}, "id":1}' % int(self.albumid))

    def _play_trailer(self, trailer):
        self.playingtrailer = 'true'
        self.getControl(100).setVisible(False)
        self.Player.play(trailer)

    def _trailerstopped(self):
        self.getControl(100).setVisible(True)
        self.playingtrailer = 'false'

    def _browse_item(self, path, window):
        self._close()
        xbmc.executebuiltin('ActivateWindow(' + window + ',' + path + ',return)')

    def _check_focus(self):
        self.getControl(190).setLabel('')
        self.getControl(191).setLabel('')
        self.getControl(198).setVisible(True)
        if self.focusset == 'false':
            self.getControl(199).setVisible(True)
            self.setFocus(self.getControl(198))
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno(xbmc.getLocalizedString(284), LANGUAGE(32298))
            if ret:
                self._newSearch()

    def _showContextMenu(self, controlId, listitem):
        labels = ()
        functions = ()
        if controlId == 111 or controlId == 211 or controlId == 231:
            labels += (xbmc.getLocalizedString(13346),)
            functions += ('info',)
            trailer = listitem.getVideoInfoTag().getTrailer()
            if trailer:
                labels += (LANGUAGE(32205),)
                functions += (self._play_trailer,)
        elif controlId == 121:
            labels += (xbmc.getLocalizedString(20351), LANGUAGE(32207), LANGUAGE(32208),)
            functions += ('info', self._getTvshow_Seasons, self._getTvshow_Episodes,)
        elif controlId == 131:
            labels += (LANGUAGE(32204),)
            functions += ('info',)
        elif controlId == 141:
            labels += (xbmc.getLocalizedString(20352),)
            functions += ('info',)
        elif controlId == 151:
            labels += (xbmc.getLocalizedString(20393),)
            functions += ('info',)
        elif controlId == 161:
            labels += (xbmc.getLocalizedString(21891), LANGUAGE(32209), LANGUAGE(32210),)
            functions += ('info', self._getArtist_Albums, self._getArtist_Songs,)
        elif controlId == 171:
            labels += (xbmc.getLocalizedString(13351), LANGUAGE(32203),)
            functions += ('info', self._browse_item,)
        elif controlId == 181:
            labels += (xbmc.getLocalizedString(658), LANGUAGE(32206),)
            functions += ('info', self._getSong_Album,)
        elif controlId == 221:
            labels += (xbmc.getLocalizedString(19047),)
            functions += (self._browse_item,)
        if labels:
            selection = xbmcgui.Dialog().contextmenu(labels)
            if selection >= 0:
                if functions[selection] == 'info':
                    xbmcgui.Dialog().info(listitem)
                elif functions[selection] == 'self._showInfo':
                    functions[selection](controlId, listitem)
                elif functions[selection] == 'self._browse_item':
                    functions[selection](listitem.getMusicInfoTag().getPath(), 'MusicLibrary')
                elif functions[selection] == 'self._play_trailer':
                    functions[selection](trailer)
                else:
                    functions[selection]()

    def _showInfo(self, controlId, listitem):
        info_dialog = infodialog.GUI('script-globalsearch-infodialog.xml' , CWD, 'default', listitem=listitem)
        info_dialog.doModal()
        del info_dialog

    def _newSearch(self):
        keyboard = xbmc.Keyboard('', LANGUAGE(32101), False)
        keyboard.doModal()
        if(keyboard.isConfirmed()):
            self.searchstring = keyboard.getText()
            self._reset_controls()
            self.onInit()

    def onClick(self, controlId):
        if controlId != 198:
            listitem = self.getControl(controlId).getSelectedItem()
            if controlId == 121 or controlId == 131:
                path = listitem.getVideoInfoTag().getPath()
                self._browse_item(path, 'Videos')
            elif controlId == 161:
                path = 'musicdb://artists/' + artistid + '/'
                self._browse_item(path, 'MusicLibrary')
            elif controlId == 171:
                self.albumid = listitem.getMusicInfoTag().getDbid()
                self._play_album()
            elif controlId == 181:
                path = listitem.getMusicInfoTag().getPath()
                self._play_audio(path, listitem)
            else:
                path = listitem.getVideoInfoTag().getPath()
                self._play_video(path)
        else:
            self._newSearch()

    def onAction(self, action):
        try:
            controlId = self.getFocusId()
            listitem = self.getControl(controlId).getSelectedItem()
        except:
            pass
        if action.getId() in ACTION_CANCEL_DIALOG:
            if self.playingtrailer == 'false':
                self._close()
            else:
                self.Player.stop()
                self._trailerstopped()
        elif action.getId() in ACTION_CONTEXT_MENU:
            self._showContextMenu(controlId, listitem)
        elif action.getId() in ACTION_OSD:
            if self.playingtrailer == 'true' and xbmc.getCondVisibility('videoplayer.isfullscreen'):
                xbmc.executebuiltin('ActivateWindow(12901)')
        elif action.getId() in ACTION_SHOW_GUI:
            if self.playingtrailer == 'true':
                self.Player.stop()
                self._trailerstopped()
        elif action.getId() in ACTION_SHOW_INFO:
            if self.playingtrailer == 'true' and xbmc.getCondVisibility('videoplayer.isfullscreen'):
                xbmc.executebuiltin('ActivateWindow(142)')
            else:
                if controlId != "221":
                    xbmcgui.Dialog().info(listitem)
                else:
                    self._showInfo(controlId, listitem)

    def _close(self):
        log('script stopped')
        self.close()
        xbmc.sleep(300)
        xbmcgui.Window(self.window_id).clearProperty('GlobalSearch.SearchString')


class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.function = kwargs["function"]

    def onPlayBackEnded(self):
        self.function()

    def onPlayBackStopped(self):
        self.function()
