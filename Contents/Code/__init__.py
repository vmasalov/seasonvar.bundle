import json

API_URL = "http://api.seasonvar.ru/"
PREFIX = "/video/seasonvarserials"

NAME = L('Title')
LATEST_SERIALS = L('LatestSerials')
LIST_SERIALS = L('ListSerials')
SEASON_TITLE = L('SeasonTitle')
ABC_SELECT_EN = L('ABCSelect_EN')
ABC_SELECT_RU = L('ABCSelect_RU')
SEARCH = L('Search')
SEARCH_PROMPT = L('SearchPrompt')
EMPTY_RESULT_TITLE = L('EmptyResultTitle')
EMPTY_RESULT_MESSAGE = L('EmptyResultMessage')

ADD_BOOKMARK_TITLE = L('AddBookmarkTitle')
ADD_BOOKMARK_MESSAGE = L('AddBookmarkMessage')

BOOKMARK = L('BookmarkList')
BOOKMARK_ADDED_MESSAGE = L('BookmarkListAddedMessage')
BOOKMARK_CLEAR_TITLE = L('BookmarkListClearTitle')
BOOKMARK_CLEAR_MESSAGE = L('BookmarkListClearMessage')
BOOKMARK_CLEARED_MESSAGE = L('BookmarkListClearedMessage')

CLEAR_BOOKMARK = L('ClearBookmark')

MISSING_API_KEY_TITLE = L('MissingAPIKeyTitle')
MISSING_API_KEY_MESSAGE = L('MissingAPIKeyMessage')
UNAUTHORIZED_TITLE = L('UnauthorizedTitle')
UNAUTHORIZED_MESSAGE = L('UnauthorizedMessage')
IP_BLOCKED_TITLE = L('IpBlockedTitle')
IP_BLOCKED_MESSAGE = L('IpBlockedMessage')

ART = 'art-default.jpg'

ICON_DEFAULT = 'icon-default.png'
ICON_RESUME = 'icon-resume.png'
ICON_LATEST = 'icon-latest.png'
ICON_COVER = 'icon-cover'
ICON_SEARCH = 'icon-search.png'
ICON_RU = 'icon-ru.png'
ICON_EN = 'icon-en.png'
ICON_BOOKMARKS = 'icon-bookmark.png'
ICON_ADD_BOOKMARK = 'icon-bookmark.png'
ICON_BOOKMARKS_CLEAR = 'icon-clear.png'

####################################################################################################
# Start and main menu
####################################################################################################


def Start():
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON_DEFAULT)
    VideoItem.thumb = R(ICON_DEFAULT)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    HTTP.Headers['Referer'] = 'http://seasonvar.ru'


@handler(PREFIX, NAME, art=ART, thumb=ICON_DEFAULT)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ru_abc, title=ABC_SELECT_RU), title=ABC_SELECT_RU, thumb=R(ICON_RU)))
    oc.add(DirectoryObject(key=Callback(en_abc, title=ABC_SELECT_EN), title=ABC_SELECT_EN, thumb=R(ICON_EN)))
    oc.add(DirectoryObject(key=Callback(latest, title=LATEST_SERIALS), title=LATEST_SERIALS, thumb=R(ICON_LATEST)))
    oc.add(InputDirectoryObject(key=Callback(search), title=SEARCH, prompt=SEARCH_PROMPT, thumb=R(ICON_SEARCH)))
    oc.add(DirectoryObject(key=Callback(bookmarks, title=BOOKMARK), title=BOOKMARK, thumb=R(ICON_BOOKMARKS)))

    return oc

######################################################################################
# Parse TV show list
######################################################################################


@route(PREFIX + "/search")
def search(query):
    if is_key_active():
        oc = ObjectContainer(title1=query)

        # setup the search request url
        values = {
            'key': Prefs["key"],
            'command': 'search',
            'query': query
        }

        # do http request for search data
        request = HTTP.Request(API_URL, values=values, cacheTime=CACHE_1DAY)
        response = json.loads(request.content)

        if is_authorized(response):
            if is_ip_valid(response):
                for season in response:
                    name = season.get('name')+', S'+season.get('season')[0]
                    oc.add(
                        TVShowObject(
                            rating_key=name,
                            key=Callback(get_season_by_id, id=season.get('id')),
                            title=name,
                            summary=season.get('description'),
                            thumb=Resource.ContentsOfURLWithFallback(url=season.get('poster_small'), fallback=ICON_COVER)
                        )
                    )
                return oc
            else:
                return display_ip_blocked_message()
        else:
            return display_unauthorized_message()
    else:
        return display_missing_key_message()

######################################################################################
# List of the latest TV shows
######################################################################################


@route(PREFIX + "/latest")
def latest(title):
    if is_key_active():
        # setup the search request url
        values = {
            'key': Prefs["key"],
            'command': 'getUpdateList',
            'day_count': '1'
        }

        # do http request for search data
        request = HTTP.Request(API_URL, values=values, cacheTime=CACHE_1DAY)
        response = json.loads(request.content)

        if is_authorized(response):
            if is_ip_valid(response):
                oc = ObjectContainer(title1=unicode(title, 'UTF-8'))

                if isinstance(response, dict) and 'error' in response.values():
                    return MessageContainer(
                        EMPTY_RESULT_TITLE,
                        EMPTY_RESULT_MESSAGE
                    )
                else:
                    for serial in response:
                        serial_id = serial.get('id')
                        serial_title = serial.get('name')
                        serial_thumb = serial.get('poster_small')
                        serial_summary = serial.get('message')

                        oc.add(
                            TVShowObject(
                                rating_key=serial_title,
                                key=Callback(get_season_by_id, id=serial_id),
                                title=serial_title,
                                summary=serial_summary,
                                thumb=Resource.ContentsOfURLWithFallback(url=serial_thumb)
                            )
                        )

                    return oc
            else:
                return display_ip_blocked_message()
        else:
            return display_unauthorized_message()
    else:
        return display_missing_key_message()

######################################################################################
# Choose by alphabet
######################################################################################


@route(PREFIX + "/en")
def en_abc(title):
    if is_key_active():
        oc = ObjectContainer(title1=title)

        abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
               'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z']

        for letter in abc:
            oc.add(DirectoryObject(key=Callback(get_serial_list_by_title, title=letter), title=unicode(letter, 'UTF-8')))
        return oc
    else:
        return display_missing_key_message()


@route(PREFIX + "/ru")
def ru_abc(title):
    if is_key_active():
        oc = ObjectContainer(title1=title)

        abc = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
               'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я']

        for letter in abc:
            oc.add(DirectoryObject(key=Callback(get_serial_list_by_title, title=letter), title=unicode(letter, 'UTF-8')))
        return oc
    else:
        return display_missing_key_message()

######################################################################################
# List serial by selected letter
######################################################################################


@route(PREFIX + "/get_serial_list_by_title")
def get_serial_list_by_title(title):
    if is_key_active():
        values = {'key': Prefs["key"], 'command': 'getSerialList', 'letter': title}

        # do http request for search data
        request = HTTP.Request(API_URL, values=values, cacheTime=CACHE_1DAY)
        response = json.loads(request.content)

        if is_authorized(response):
            if is_ip_valid(response):
                oc = ObjectContainer(title1=unicode(title, 'UTF-8'))

                if isinstance(response, dict) and 'error' in response.values():
                    return MessageContainer(
                        EMPTY_RESULT_TITLE,
                        EMPTY_RESULT_MESSAGE
                    )
                else:
                    for serial in response:
                        total = serial.get('count_of_seasons')
                        serial_title = serial.get('name')
                        serial_thumb = serial.get('poster_small')
                        serial_summary = serial.get('description')
                        serial_country = serial.get('country')

                        if total:
                            oc.add(
                                TVShowObject(
                                    rating_key=serial_title,
                                    key=Callback(get_season_list_by_title, title=serial_title),
                                    title=serial_title,
                                    summary=serial_summary,
                                    countries=[serial_country],
                                    thumb=Resource.ContentsOfURLWithFallback(url=serial_thumb)
                                )
                            )
                        else:
                            # there are no seasons
                            oc.add(
                                SeasonObject(
                                    rating_key=serial_title,
                                    key=Callback(get_season_by_id, id=serial.get('last_season_id')),
                                    title=serial_title,
                                    index=int(1),
                                    summary=serial_summary,
                                    thumb=Resource.ContentsOfURLWithFallback(url=serial_thumb)
                                )
                            )
                    return oc
            else:
                return display_ip_blocked_message()
        else:
            return display_unauthorized_message()
    else:
        return display_missing_key_message()


@route(PREFIX + "/get_season_list_by_title")
def get_season_list_by_title(title):
    if is_key_active():
        values = {
            'key': Prefs["key"],
            'command': 'getSeasonList',
            'name': title
        }

        request = HTTP.Request(API_URL, values=values, cacheTime=CACHE_1DAY)
        response = json.loads(request.content)

        if is_authorized(response):
            if is_ip_valid(response):
                oc = ObjectContainer(title2=unicode(title, 'UTF-8'))

                if isinstance(response, dict) and 'error' in response.values():
                    return MessageContainer(
                        EMPTY_RESULT_TITLE,
                        EMPTY_RESULT_MESSAGE
                    )
                else:
                    for season in response:
                        season_id = season.get('id')
                        season_number = season.get('season_number')
                        oc.add(SeasonObject(
                            rating_key=title+season_number,
                            key=Callback(get_season_by_id, id=season_id),
                            title=SEASON_TITLE+' '+season_number,
                            index=int(season_number),
                            summary=season.get('description'),
                            thumb=Resource.ContentsOfURLWithFallback(url=season.get('poster_small'), fallback=ICON_COVER)
                        ))
                    return oc
            else:
                return display_ip_blocked_message()
        else:
            return display_unauthorized_message()
    else:
        return display_missing_key_message()


@route(PREFIX + "/get_season_by_id")
def get_season_by_id(id):
    if is_key_active():
        values = {
            'key': Prefs["key"],
            'command': 'getSeason',
            'season_id': id
        }

        request = HTTP.Request(API_URL, values=values, cacheTime=CACHE_1DAY)
        response = json.loads(request.content)

        if is_authorized(response):
            if is_ip_valid(response):
                MediaContainer.art = Resource.ContentsOfURLWithFallback(url=response.get('poster'), fallback=ART)

                oc = ObjectContainer(title2=response.get('name'))

                playlist = response.get('playlist')
                for video in playlist:
                    video_name = video.get('name')
                    video_link = video.get('link')
                    oc.add(create_eo(
                        url=video_link,
                        title=video_name,
                        summary=response.get('description'),
                        rating=averageRating(response.get('rating')),
                        thumb=response.get('poster_small')
                    ))

                oc.add(DirectoryObject(
                    key=Callback(add_bookmark, title=response.get('name'), id=response.get('id'), thumb=response.get('poster'), summary=response.get('description')),
                    title=ADD_BOOKMARK_TITLE,
                    summary=response.get('name')+ADD_BOOKMARK_MESSAGE,
                    thumb=R(ICON_ADD_BOOKMARK)
                    )
                )

                return oc
            else:
                return display_ip_blocked_message()
        else:
            return display_unauthorized_message()
    else:
        return display_missing_key_message()


@route(PREFIX + "/create_eo")
def create_eo(url, title, summary, rating, thumb, include_container=False):
    eo = EpisodeObject(
                        rating_key=url,
                        key=Callback(create_eo, url=url, title=title, summary=summary, rating=rating, thumb=thumb, include_container=True),
                        title=title,
                        summary=summary,
                        rating=float(rating),
                        thumb=thumb,
                        items=[
                            MediaObject(
                                parts=[
                                    PartObject(key=url)
                                ],
                                container=Container.MP4,
                                video_codec=VideoCodec.H264,
                                video_resolution='544',
                                audio_codec=AudioCodec.AAC,
                                audio_channels=2,
                                optimized_for_streaming=True
                            )
                        ]
    )

    if include_container:
        return ObjectContainer(objects=[eo])
    else:
        return eo

######################################################################################
# Bookmarks
######################################################################################


@route(PREFIX + "/bookmarks")
def bookmarks(title):
    oc = ObjectContainer(title1=title)

    for show_id in Dict:
        show = Dict[show_id]
        show_title = unicode(show.get('title'), 'UTF-8')
        oc.add(
            TVShowObject(
                rating_key=show_title,
                key=Callback(get_season_by_id, id=show_id),
                title=show_title,
                summary=unicode(show.get('summary'), 'UTF-8'),
                thumb=Resource.ContentsOfURLWithFallback(url=show.get('thumb'))
            )
        )

    # add a way to clear bookmarks list
    oc.add(DirectoryObject(
        key=Callback(clear_bookmarks),
        title=BOOKMARK_CLEAR_TITLE,
        thumb=R(ICON_BOOKMARKS_CLEAR),
        summary=BOOKMARK_CLEAR_MESSAGE
        )
    )

    return oc


@route(PREFIX + "/addbookmark")
def add_bookmark(title, id, thumb, summary):
    Dict[id] = dict(title=title, thumb=thumb, summary=summary)
    Dict.Save()

    return MessageContainer(
        BOOKMARK,
        BOOKMARK_ADDED_MESSAGE
    )


@route(PREFIX + "/clearbookmarks")
def clear_bookmarks():
    Dict.Reset()
    return MessageContainer(
        BOOKMARK,
        BOOKMARK_CLEARED_MESSAGE
    )


######################################################################################
#  Utilities
######################################################################################

# get average rating for the tv show
def averageRating(ratings):
    result = 0.0

    if ratings:
        for rater in ratings.iterkeys():
            ratio = float(ratings.get(rater).get('ratio'))
            result += ratio

        result = result / len(list(ratings.iterkeys()))

    return result


def is_key_active():
    return Prefs["key"]


def is_authorized(response):
    if 'error' in response:
        if response.get('error') == 'Authentication::getUser::wrong key':
            return False
    return True


def is_ip_valid(response):
    if 'error' in response:
        if response.get('error') == 'Authorization::checkRules::this ip is not allowed':
            return False
    return True


def display_ip_blocked_message():
    return MessageContainer(
        IP_BLOCKED_TITLE,
        IP_BLOCKED_MESSAGE
    )

def display_unauthorized_message():
    return MessageContainer(
        UNAUTHORIZED_TITLE,
        UNAUTHORIZED_MESSAGE
    )


def display_missing_key_message():
    return MessageContainer(
        MISSING_API_KEY_TITLE,
        MISSING_API_KEY_MESSAGE
    )