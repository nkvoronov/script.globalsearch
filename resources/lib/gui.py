import datetime
import infodialog
import json
import operator
from defs import *

#TODO REMOVE
MOVIES = 110
TVSHOWS = 120
SEASONS = 130
EPISODES = 140
MUSICVIDEOS = 150
ARTISTS = 160
ALBUMS = 170
SONGS = 180
EPG = 190
ACTORS = 200
DIRECTORS = 210
#/TODO

def log(txt):
    if isinstance(txt,str):
        txt = txt.decode('utf-8')
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)

class GUI(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.params = kwargs['params']
        self.searchstring = kwargs['searchstring']

    def onInit(self):
        self._hide_controls()
        log('script version %s started' % ADDONVERSION)
        self.nextsearch = False
        # some sanitize work for search string: strip the input and replace some chars
        self.searchstring = self._clean_string(self.searchstring).strip()
        if self.searchstring == '':
            self._close()
        else:
            self.window_id = xbmcgui.getCurrentWindowId()
            xbmcgui.Window(self.window_id).setProperty('GlobalSearch.SearchString', self.searchstring)
            if not self.nextsearch:
                if self.params == {}:
                    self._load_settings()
                else:
                    self._parse_argv()
            self._reset_variables()
            self._init_items()
            self._fetch_items()

    def _hide_controls(self):
        for cid in [SEARCHBUTTON, NORESULTS]:
            self.getControl(cid).setVisible(False)

    def _parse_argv(self):
        for key, value in CATEGORIES.iteritems():
            CATEGORIES[key]['enabled'] = self.params.get(value, '') == 'true'

    def _load_settings(self):
        for key, value in CATEGORIES.iteritems():
            CATEGORIES[key]['enabled'] = ADDON.getSetting(key) == 'true'

    def _reset_variables(self):
        self.focusset= 'false'
        self.getControl(SEARCHLABEL).setLabel(xbmc.getLocalizedString(194))

    def _init_items(self):
        self.getControl(SEARCHBUTTON).setLabel(LANGUAGE(32299))
        self.Player = MyPlayer()
        self.menu = self.getControl(MENU)
        self.content = {}

    def _fetch_items(self):
        for key, value in sorted(CATEGORIES.items(), key=lambda x: x[1]['order']):
            if CATEGORIES[key]['enabled']:
                self._get_items(CATEGORIES[key], self.searchstring)
        self._check_focus()

    def _get_items(self, cat, search, extrafilter=None):
        if cat['type'] == 'epg':
            self._fetch_channelgroups()
            return
        self.getControl(SEARCHCATEGORY).setLabel(xbmc.getLocalizedString(cat['label']))
        json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"%s", "params":{"properties":%s, "sort":{"method":"%s"}, %s}, "id": 1}' % (cat['method'], json.dumps(cat['properties']), cat['sort'], cat['rule'] % search))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        listitems = []
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key(cat['type']):
            for item in json_response['result'][cat['type']]:
                if extrafilter:
                    if item['albumid'] != int(extrafilter):
                        continue
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item, cat['icon'], cat['media']))
                if cat['streamdetails']:
                    for stream in item['streamdetails']['video']:
                        listitem.addStreamInfo('video', stream)
                    for stream in item['streamdetails']['audio']:
                        listitem.addStreamInfo('audio', stream)
                    for stream in item['streamdetails']['subtitle']:
                        listitem.addStreamInfo('subtitle', stream)
                if cat['type'] == 'tvshows':
                    listitem.setProperty('TotalSeasons', str(item['season']))
                    listitem.setProperty('TotalEpisodes', str(item['episode']))
                    listitem.setProperty('WatchedEpisodes', str(item['watchedepisodes']))
                    listitem.setProperty('UnWatchedEpisodes', str(item['episode'] - item['watchedepisodes']))
                elif cat['type'] == 'seasons':
                    listitem.setProperty('tvshowid', str(item['tvshowid']))
                elif cat['type'] == 'artists' or cat['type'] == 'albums':
                    info, props = self._split_labels(item, cat['properties'], cat['type'][0:-1] + '_')
                    for key, value in props.iteritems():
                        listitem.setProperty(key, value)
                elif cat['type'] == 'songs':
                    listitem.setProperty('artistid', str(item['artistid']))
                    listitem.setProperty('albumid', str(item['albumid']))
                elif cat['type'] == 'movies' or cat['type'] == 'episodes' or cat['type'] == 'musicvideos':
                    listitem.setProperty('resume', str(int(item['resume']['position'])))
                if cat['type'] == 'movies' or cat['type'] == 'tvshows' or cat['type'] == 'episodes' or cat['type'] == 'musicvideos' or cat['type'] == 'songs':
                    listitem.setPath(item['file'])
                listitem.setInfo(cat['media'], self._get_info(item, cat['type'][0:-1]))
                listitems.append(listitem)
        if len(listitems) > 0:
            menuitem = xbmcgui.ListItem(xbmc.getLocalizedString(cat['label']))
            menuitem.setArt({'icon':cat['menuthumb']})
            menuitem.setPath(cat['type'])
            self.menu.addItem(menuitem)
            self.content[cat['type']] = listitems
            if self.focusset == 'false':
                self.clearList()
                self.setContainerProperty('Content', cat['type'])
                self.addItems(listitems)
                xbmc.sleep(100)
                self.focusset = 'true'

    def _fetch_channelgroups(self):
        self.getControl(SEARCHCATEGORY).setLabel(xbmc.getLocalizedString(19069))
        channelgrouplist = []
        json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"PVR.GetChannelGroups", "params":{"channeltype":"tv"}, "id":1}')
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
            json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"PVR.GetChannels", "params":{"channelgroupid":%i, "properties":["channel", "thumbnail"]}, "id":1}' % channelgroupid)
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
        # get all programs for every channel id
        for channel in channels:
            channelid = channel['channelid']
            channelname = channel['label']
            channelthumb = channel['thumbnail']
            json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"PVR.GetBroadcasts", "params":{"channelid":%i, "properties":["starttime", "endtime", "runtime", "genre", "plot"]}, "id":1}' % channelid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = json.loads(json_query)
            if(json_response.has_key('result')) and(json_response['result'] != None) and(json_response['result'].has_key('broadcasts')):
                for item in json_response['result']['broadcasts']:
                    broadcastname = item['label']
                    epgmatch = re.search('.*' + self.searchstring + '.*', broadcastname, re.I)
                    if epgmatch:
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
            if len(listitems) > 0:
                menuitem = xbmcgui.ListItem(xbmc.getLocalizedString(cat['label']))
                menuitem.setArt({'icon':cat['menuthumb']})
                menuitem.setPath(cat['type'])
                self.menu.addItem(menuitem)
                self.content[cat['type']] = listitems
                if self.focusset == 'false':
                    self.clearList()
                    self.setContainerProperty('Content', cat['type'])
                    self.addItems(listitems)
                    xbmc.sleep(100)
                    self.focusset = 'true'

    def _update_list(self, item):
        self.clearList()
        self.setContainerProperty('Content', item)
        self.addItems(self.content[item])

    def _get_info(self, labels, item):
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
            labels['duration'] = labels['runtime']
            labels['path'] = labels['file']
            del labels['file']
            del labels['runtime']
            if item != 'tvshow':
                del labels['streamdetails']
                del labels['resume']
            else:
                del labels['watchedepisodes']
        if item == 'season' or item == 'episode':
            labels['tvshowtitle'] = labels['showtitle']
            del labels['showtitle']
            if item == 'season':
                del labels['tvshowid']
                del labels['watchedepisodes']
            else:
                labels['aired'] = labels['firstaired']
                del labels['firstaired']
        if item == 'album':
            del labels['artistid']
        if item == 'song':
            labels['tracknumber'] = labels['track']
            del labels['track']
            del labels['file']
            del labels['artistid']
            del labels['albumid']
        for key, value in labels.iteritems():
            if isinstance(value, list):
                if key == 'artist' and item == 'musicvideo':
                    continue
                value = " / ".join(value)
            labels[key] = value
        return labels

    def _get_art(self, labels, icon, media):
        if media == 'video':
            art = labels['art']
            if labels.get('poster'):
                art['thumb'] = labels['poster']
            elif labels.get('banner'):
                art['thumb'] = labels['banner']
        else:
            art = {}
            art['thumb'] = labels['thumbnail']
            art['fanart'] = labels['fanart']
        art['icon'] = icon
        return art

    def _split_labels(self, item, labels, prefix):
        props = {}
        for label in labels:
            if label == 'thumbnail' or label == 'fanart' or label == 'rating' or label == 'userrating' or label == 'file' or label == 'artistid' or label == 'albumid' or label == 'songid' or (prefix == 'album_' and (label == 'artist' or label == 'genre' or label == 'year')):
                continue
            if isinstance(item[label], list):
                item[label] = " / ".join(item[label])
            if label == 'albumlabel':
                props[prefix + 'label'] = item['albumlabel']
            else:
                props[prefix + label] = item[label]
            del item[label]
        return item, props

    def _clean_string(self, string):
        return string.replace('(', '[(]').replace(')', '[)]').replace('+', '[+]')

    def _get_allitems(self, key, listitem):
        extrafilter = None
        if key == 'tvshowseasons' or key == 'tvshowepisodes':
            search = listitem.getVideoInfoTag().getDbId()
        elif key == 'artistalbums' or key == 'artistsongs':
            search = listitem.getMusicInfoTag().getDbId()
        else:
            search = listitem.getProperty('artistid')[1:-1]
            extrafilter = listitem.getProperty('albumid')
        self._reset_variables()
        self._hide_controls()
        self._get_items(CATEGORIES[key], search, extrafilter)
        self._check_focus()

    def _get_selectaction(self):
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue","params":{"setting":"myvideos.selectaction"}, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        action = 1
        if json_response.has_key('result') and (json_response['result'] != None) and json_response['result'].has_key('value'):
            action = json_response['result']['value']
        return action

    def _play_item(self, key, value, listitem=None):
        if key == 'file':
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.Open", "params":{"item":{"%s":"%s"}}, "id":1}' % (key, value))
        else:
            action = self._get_selectaction()
            resume = int(listitem.getProperty('resume'))
            if action == 0:
                labels = ()
                functions = ()
                if int(resume) > 0:
                    m, s = divmod(resume, 60)
                    h, m = divmod(m, 60)
                    val = '%d:%02d:%02d' % (h, m, s)
                    labels += (xbmc.getLocalizedString(12022) % val,)
                    functions += ('resume',)
                    labels += (xbmc.getLocalizedString(12021),)
                    functions += ('play',)
                else:
                    labels += (xbmc.getLocalizedString(208),)
                    functions += ('play',)
                labels += (xbmc.getLocalizedString(22081),)
                functions += ('info',)
                selection = xbmcgui.Dialog().contextmenu(labels)
                if selection >= 0:
                    if functions[selection] == 'play':
                        action = 1
                    if functions[selection] == 'resume':
                        action = 2
                    if functions[selection] == 'info':
                        action = 3
            if action == 3:
                self._show_info(listitem)
            elif action == 1 or action == 2:
                if action == 2:
                    self.Player.resume = resume
                xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.Open", "params":{"item":{"%s":%d}}, "id":1}' % (key, int(value)))

    def _browse_item(self, path, window):
        xbmc.executebuiltin('ActivateWindow(' + window + ',' + path + ',return)')

    def _check_focus(self):
        self.getControl(SEARCHLABEL).setLabel('')
        self.getControl(SEARCHCATEGORY).setLabel('')
        self.getControl(SEARCHBUTTON).setVisible(True)
        if self.focusset == 'false':
            self.getControl(NORESULTS).setVisible(True)
            self.setFocus(self.getControl(SEARCHBUTTON))
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno(xbmc.getLocalizedString(284), LANGUAGE(32298))
            if ret:
                self._new_search()

    def _context_menu(self, controlId, listitem):
        labels = ()
        functions = ()
#TODO   media = listitem.getxxx()
        if controlId == MOVIES+1 or controlId == ACTORS+1 or controlId == DIRECTORS+1:
            labels += (xbmc.getLocalizedString(13346),)
            functions += ('info',)
            path = listitem.getVideoInfoTag().getTrailer()
            if path:
                labels += (LANGUAGE(32205),)
                functions += ('play',)
        elif controlId == TVSHOWS+1:
            labels += (xbmc.getLocalizedString(20351), LANGUAGE(32207), LANGUAGE(32208),)
            functions += ('info', 'tvshowseasons', 'tvshowepisodes',)
        elif controlId == EPISODES+1:
            labels += (xbmc.getLocalizedString(20352),)
            functions += ('info',)
        elif controlId == MUSICVIDEOS+1:
            labels += (xbmc.getLocalizedString(20393),)
            functions += ('info',)
        elif controlId == ARTISTS+1:
            labels += (xbmc.getLocalizedString(21891), LANGUAGE(32209), LANGUAGE(32210),)
            functions += ('info', 'artistalbums', 'artistsongs',)
        elif controlId == ALBUMS+1:
            labels += (xbmc.getLocalizedString(13351), LANGUAGE(32203),)
            functions += ('info', 'browse',)
        elif controlId == SONGS+1:
            labels += (xbmc.getLocalizedString(658), LANGUAGE(32206),)
            functions += ('info', 'songalbum',)
        if labels:
            selection = xbmcgui.Dialog().contextmenu(labels)
            if selection >= 0:
                if functions[selection] == 'info':
                    self._show_info(listitem)
                elif functions[selection] == 'browse':
                    self._browse_item('musicdb://albums/%s/' % str(listitem.getMusicInfoTag().getDbId()), 'Music')
                elif functions[selection] == 'play':
                    self._play_item('file', path)
                else:
                    self._get_allitems(functions[selection], listitem)

    def _show_info(self, listitem):
        self.getControl(MAINGROUP).setVisible(False)
        xbmcgui.Dialog().info(listitem)
        self.getControl(MAINGROUP).setVisible(True)

    def _new_search(self):
        keyboard = xbmc.Keyboard('', LANGUAGE(32101), False)
        keyboard.doModal()
        if(keyboard.isConfirmed()):
            self.searchstring = keyboard.getText()
            self.clearList()
            self.onInit()

    def onClick(self, controlId):
        if controlId == self.getCurrentContainerId():
            listitem = self.getControl(controlId).getSelectedItem()
#TODO       media = listitem.getxxx()
            if controlId == TVSHOWS+1:
                path = 'videodb://tvshows/titles/%s/' % str(listitem.getVideoInfoTag().getDbId())
                self._browse_item(path, 'Videos')
            elif controlId == SEASONS+1:
                path = 'videodb://tvshows/titles/%s/%s/' % (str(listitem.getProperty('tvshowid')), str(listitem.getVideoInfoTag().getSeason()))
                self._browse_item(path, 'Videos')
            elif controlId == ARTISTS+1:
                path = 'musicdb://artists/%s/' % str(listitem.getMusicInfoTag().getDbId())
                self._browse_item(path, 'Music')
            elif controlId == ALBUMS+1:
                albumid = listitem.getMusicInfoTag().getDbId()
                self._play_item('albumid', albumid)
            elif controlId == SONGS+1:
                songid = listitem.getMusicInfoTag().getDbId()
                self._play_item('songid', songid)
            elif controlId == MOVIES+1 or controlId == ACTORS+1 or controlId == DIRECTORS+1:
                movieid = listitem.getVideoInfoTag().getDbId()
                self._play_item('movieid', movieid, listitem)
            elif controlId == EPISODES+1:
                episodeid = listitem.getVideoInfoTag().getDbId()
                self._play_item('episodeid', episodeid, listitem)
            elif controlId == MUSICVIDEOS+1:
                musicvideoid = listitem.getVideoInfoTag().getDbId()
                self._play_item('musicvideoid', musicvideoid, listitem)
        elif controlId == MENU:
            item = self.menu.getSelectedItem().getPath()
            self._update_list(item)
        elif controlId == SEARCHBUTTON:
            self._new_search()

    def onAction(self, action):
        if action.getId() in ACTION_CANCEL_DIALOG:
            self._close()
        elif action.getId() in ACTION_CONTEXT_MENU or action.getId() in ACTION_SHOW_INFO:
            controlId = self.getFocusId()
            if controlId == self.getCurrentContainerId():
                listitem = self.getControl(controlId).getSelectedItem()
#TODO           media = listitem.getxxx()
                if action.getId() in ACTION_CONTEXT_MENU:
                    self._context_menu(controlId, listitem)
                elif action.getId() in ACTION_SHOW_INFO:
                    if controlId != EPG+1 and controlId != SEASONS+1:
                        self._show_info(listitem)

    def _close(self):
        log('script stopped')
        self.close()
        xbmc.sleep(300)
        xbmcgui.Window(self.window_id).clearProperty('GlobalSearch.SearchString')


class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.resume = 0

    def onPlayBackStarted(self):
        for count in range(50):
            if self.isPlayingVideo():
                break
            xbmc.sleep(100)
        self.seekTime(float(self.resume))
