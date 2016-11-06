import datetime
import infodialog
import json
import operator
from utils import *

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
                if self.params == {}:
                    self._load_settings()
                else:
                    self._parse_argv()
            self._reset_variables()
            self._init_items()
            self._fetch_items()

    def _hide_controls(self):
        for cid in [119, 129, 139, 149, 159, 169, 179, 189, 219, 229, 239, 189, 998, 999]:
            self.getControl(cid).setVisible(False)

    def _reset_controls(self):
        for cid in [111, 121, 131, 141, 151, 161, 171, 181, 211, 231]:
            self.getControl(cid).reset()

    def _parse_argv(self):
        for key, value in CATEGORIES.iteritems():
            CATEGORIES[key]['enabled'] = self.params.get(value, '') == 'true'

    def _load_settings(self):
        for key, value in CATEGORIES.iteritems():
            CATEGORIES[key]['enabled'] = ADDON.getSetting(key) == 'true'

    def _reset_variables(self):
        self.focusset= 'false'
        self.getControl(990).setLabel(xbmc.getLocalizedString(194))

    def _init_items(self):
        self.playingtrailer = 'false'
        self.getControl(998).setLabel(LANGUAGE(32299))
        self.Player = MyPlayer(function=self._trailerstopped)

    def _fetch_items(self):
        for key, value in sorted(CATEGORIES.items(), key=lambda x: x[1]['order']):
            if CATEGORIES[key]['enabled']:
                self._get_items(CATEGORIES[key], self.searchstring)
        self._check_focus()

    def _get_items(self, cat, search):
        if cat['type'] == 'epg':
            self._fetch_channelgroups()
            return
        self.getControl(991).setLabel(xbmc.getLocalizedString(cat['label']))
        json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"%s", "params":{"properties":%s, "sort":{"method":"%s"}, "filter":%s}, "id": 1}'
                                         % (cat['method'], json.dumps(cat['properties']), cat['sort'], cat['rule'] % search))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        listitems = []
        count = 0
        if json_response.has_key('result') and(json_response['result'] != None) and json_response['result'].has_key(cat['type']):
            for item in json_response['result'][cat['type']]:
                count = count + 1
                listitem = xbmcgui.ListItem(item['label'])
                listitem.setArt(self._get_art(item, cat['icon'], cat['media']))
                if cat['streamdetails']:
                    for stream in item['streamdetails']['video']:
                        listitem.addStreamInfo('video', stream)
                    for stream in item['streamdetails']['audio']:
                        listitem.addStreamInfo('audio', stream)
                    for stream in item['streamdetails']['subtitle']:
                        listitem.addStreamInfo('subtitle', stream)
                if cat['cast']:
                    listitem.setCast(item['cast'])
                if cat['type'] == 'artists' or cat['type'] == 'albums':
                    info, props = self._split_labels(item, cat['properties'], cat['type'][0:-1] + '_')
                    for key, value in props.iteritems():
                        listitem.setProperty(key, value)
                if cat['type'] == 'songs':
                    listitem.setProperty('albumid', str(item['albumid']))
                listitem.setInfo(cat['media'], self._get_info(item, cat['type'][0:-1]))
                listitems.append(listitem)
        self.getControl(cat['control'] + 1).addItems(listitems)
        if count > 0:
            self.getControl(cat['control']).setLabel(str(count))
            self.getControl(cat['control'] + 9).setVisible(True)
            if self.focusset == 'false':
                xbmc.sleep(100)
                self.setFocus(self.getControl(cat['control'] + 1))
                self.focusset = 'true'

    def _fetch_channelgroups(self):
        self.getControl(991).setLabel(xbmc.getLocalizedString(19069))
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
            labels['duration'] = labels['runtime'] # we does json return runtime instead of duration?
            del labels['runtime']
            if item != 'musicvideo':
                del labels['cast']
            if item != 'tvshow':
                del labels['streamdetails']
        if item == 'season' or item == 'episode':
            del labels['showtitle']
            if item == 'season':
                del labels['firstaired']
        if item == 'song':
            labels['tracknumber'] = labels['track']
            del labels['track']
            del labels['file']
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
            art['thumb'] = labels['fanart']
            art['fanart'] = labels['fanart']
        art['icon'] = icon
        return art

    def _split_labels(self, item, labels, prefix):
        props = {}
        for label in labels:
            if label == 'thumbnail' or label == 'fanart' or label == 'rating' or label == 'userrating' or (prefix == 'album_' and (label == 'genre' or label == 'year')):
                continue
            if isinstance(item[label], list):
                item[label] = " / ".join(item[label])
            props[prefix + label] = item[label]
            del item[label]
        return item, props

    def _clean_string(self, string):
        return string.replace('(', '[(]').replace(')', '[)]').replace('+', '[+]')

    def _get_allitems(self, key):
        if key == 'tvshowseasons' or key == 'tvshowepisodes':
            search = listitem.getVideoInfoTag().getDbId()
        elif key == 'artistalbums' or key == 'artistsongs':
            search = listitem.getMusicInfoTag().getDbId()
        else:
            search = listitem.getProperty('artistid')
        self._reset_variables()
        self._hide_controls()
        self._reset_controls()
        self.fetch_items(CATEGORIES[key], search)
        self._check_focus()

    def _play_item(self, key, value):
        if key == 'path':
            self.playingtrailer = 'true'
            self.getControl(100).setVisible(False)
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.Open", "params":{"item":{"%s":"%s"}}, "id":1}' % (key, value))
        else:
            self._close()
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Player.Open", "params":{"item":{"%s":%d}}, "id":1}' % (key, int(value)))

    def _trailerstopped(self):
        self.getControl(100).setVisible(True)
        self.playingtrailer = 'false'

    def _browse_item(self, path, window):
        self._close()
        xbmc.executebuiltin('ActivateWindow(' + window + ',' + path + ',return)')

    def _check_focus(self):
        self.getControl(990).setLabel('')
        self.getControl(991).setLabel('')
        self.getControl(998).setVisible(True)
        if self.focusset == 'false':
            self.getControl(999).setVisible(True)
            self.setFocus(self.getControl(998))
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
            functions += ('info', 'tvshowseasons', 'tvshowepisodes',)
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
            functions += ('info', 'artistalbums', 'artistsongs',)
        elif controlId == 171:
            labels += (xbmc.getLocalizedString(13351), LANGUAGE(32203),)
            functions += ('info', self._browse_item,)
        elif controlId == 181:
            labels += (xbmc.getLocalizedString(658), LANGUAGE(32206),)
            functions += ('info', 'songalbum',)
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
                    functions[selection]('trailer', trailer)
                else:
                    self._get_allitems(functions[selection], listitem)

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
        if controlId != 998:
            listitem = self.getControl(controlId).getSelectedItem()
            if controlId == 121 or controlId == 131:
                path = listitem.getVideoInfoTag().getPath()
                self._browse_item(path, 'Videos')
            elif controlId == 161:
                path = 'musicdb://artists/' + artistid + '/'
                self._browse_item(path, 'MusicLibrary')
            elif controlId == 171:
                albumid = listitem.getMusicInfoTag().getDbid()
                self._play_item('albumid', albumid)
            elif controlId == 181:
                songid = listitem.getMusicInfoTag().getDbid()
                self._play_item('songid', songid)
            elif controlId == 111 or controlId == 211 or controlId == 231:
                movieid = listitem.getVideoInfoTag().getDbid()
                self._play_item('movieid', movieid)
            elif controlId == 141:
                episodeid = listitem.getVideoInfoTag().getDbid()
                self._play_item('episodeid', episodeid)
            elif controlId == 151:
                musicvideoid = listitem.getVideoInfoTag().getDbid()
                self._play_item('musicvideoid', episodeid)
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
