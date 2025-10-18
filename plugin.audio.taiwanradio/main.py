import xbmcgui
import xbmcplugin
import xbmc
import urllib.request
import sys
import urllib.parse

# 獲取參數
handle = int(sys.argv[1])

# 電台清單（未來擴展友好）
STATIONS = {
    # 電台清單新增分為三種：
    # GET：透過GET特定網址得到當下串流連結(e.g. A-Line Radio)
    # POST：需要帶入參數以獲得串流連結(e.g. Hit FM)
    # DIRECT：網址即為串流連結(e.g. 警察廣播電台)
    'alineall': {
        'name': 'A-Line Radio 網路音樂台',
        'url': 'https://ipget.apple-line.com/alinePlayer.php',
        'method': 'GET',
        'desc': 'A-Line Radio 最舒服的電台'
    },
    'alinesouth': {
        'name': 'A-Line Radio 正港電台',
        'url': 'https://ipget.apple-line.com/ch05Player.php',
        'method': 'GET',
        'desc': 'A-Line Radio 南部 正港電台'
    },
    'hitfmnorth': {
        'name': 'Hit FM 北部',
        'url': 'https://www.hitoradio.com/newweb/hichannel.php',
        'method': 'POST',
        'post_data': 'channelID=1&action=getLIVEURL',  # 專屬 Hit FM Body
        'desc': 'Hit FM 中部流行音樂台'
    },
    'hitfmcentral': {
        'name': 'Hit FM 中部',
        'url': 'https://www.hitoradio.com/newweb/hichannel.php',
        'method': 'POST',
        'post_data': 'channelID=2&action=getLIVEURL',  # 專屬 Hit FM Body
        'desc': 'Hit FM 中部流行音樂台'
    },
    'family977': {
        'name': '古典音樂台',
        'url': 'https://onair.family977.com.tw:8977/live.mp3',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '好家庭聯播網 - 古典音樂台'
    },
    'bestradio': {
        'name': '好事989電台',
        'url': 'https://stream.rcs.revma.com/fkdywbc59duvv',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '好事聯播網'
    },
    'ilikeradio': {
        'name': '中廣流行網',
        'url': 'https://stream.rcs.revma.com/aw9uqyxy2tzuv',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '中廣流行網 I like radio'
    },
    'iradio': {
        'name': '中廣音樂網',
        'url': 'https://stream.rcs.revma.com/ndk05tyy2tzuv',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '中廣音樂網 I radio'
    },
    'pbsall': {
        'name': '警廣全國治安交通網',
        'url': 'https://stream.pbs.gov.tw/live/mp3:PBS/playlist.m3u8',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '警察廣播電台 全國治安交通網'
    },
    'pbstaichung': {
        'name': '警廣台中分台',
        'url': 'https://stream.pbs.gov.tw/live/TCS/playlist.m3u8',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '警察廣播電台 台中分台'
    },
    'baodaocentral': {
        'name': '寶島聯播網 大千電台',
        'url': 'http://125.227.87.206:8000/FM99.1',  # 直接串流
        'method': 'DIRECT',  # 無需 API，直接播放
        'desc': '寶島聯播網 中部 大千電台'
    },
}

def get_m3u8_url(station_id):
    try:
        station = STATIONS[station_id]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7390.71 Mobile Safari/537.36'}
        
        if station['method'] == 'GET':
            # GET 請求（A-Line 等），可能需增加規則以正確的Header請求資料
            req = urllib.request.Request(station['url'], headers=headers)
            
        elif station['method'] == 'POST':
            # POST 請求（Hit FM 等），可能需增加規則以正確的Header請求資料
            if station_id == 'hitfmnorth' or station_id == 'hitfmcentral':
                data = station['post_data'].encode('utf-8')
                headers.update({
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': str(len(data))
                })
            else:
                data = b''  # 空 Body 預防
            
            req = urllib.request.Request(
                station['url'], 
                data=data, 
                headers=headers, 
                method='POST'
            )
        elif station['method'] == 'DIRECT':
            # 直接串流：立即返回 URL
            return station['url']
        
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8').strip()
    except Exception as e:
        xbmc.log(f"{station_id} Error: {e}", xbmc.LOGERROR)
        return None

def list_stations():
    xbmcplugin.setContent(handle, 'songs')
    
    for station_id, info in STATIONS.items():
        li = xbmcgui.ListItem(info['name'], offscreen=True)
        li.setArt({'icon': 'DefaultMusicSongs.png'})
        li.setInfo('music', {
            'title': info['name'],
            'genre': info['desc']
        })
        url = sys.argv[0] + '?station=' + station_id
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    
    xbmcplugin.endOfDirectory(handle)

def play_station(station_id):
    xbmcplugin.setContent(handle, 'songs')
    
    url = get_m3u8_url(station_id)
    if url:
        li_play = xbmcgui.ListItem("播放 " + STATIONS[station_id]['name'], offscreen=True)
        li_play.setArt({'icon': 'DefaultMusicSongs.png'})
        li_play.setProperty('IsPlayable', 'true')
        li_play.setInfo('music', {
            'title': STATIONS[station_id]['name'],
            'genre': STATIONS[station_id]['desc']
        })
        li_play.setPath(url)
        xbmcplugin.addDirectoryItem(handle, url, li_play, False)
        
        li_refresh = xbmcgui.ListItem("重新整理串流", offscreen=True)
        li_refresh.setArt({'icon': 'DefaultAddon.png'})
        refresh_url = sys.argv[0] + '?station=' + station_id + '&action=refresh'
        xbmcplugin.addDirectoryItem(handle, refresh_url, li_refresh, True)
    else:
        li_error = xbmcgui.ListItem("連線失敗", offscreen=True)
        li_error.setArt({'icon': 'DefaultAddon.png'})
        xbmcplugin.addDirectoryItem(handle, '', li_error, True)
    
    xbmcplugin.endOfDirectory(handle)

# 路由處理
if len(sys.argv) < 3 or not sys.argv[2]:
    list_stations()
else:
    query = sys.argv[2][1:]
    params = urllib.parse.parse_qs(query)
    
    station_id = params.get('station', [''])[0]
    action = params.get('action', [''])[0]
    
    if station_id in STATIONS:
        if action == 'refresh':
            play_station(station_id)
        else:
            play_station(station_id)
    else:
        list_stations()