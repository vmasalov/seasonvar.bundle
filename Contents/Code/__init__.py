import json
import re

PREFIX = "/video/seasonvarserials"

NAME = L('Title')
LATEST_SERIALS = L('LatestSerials')
LIST_SERIALS = L('ListSerials')
SEASON_TITLE = L('SeasonTitle')
ABC_SELECT_EN = L('ABCSelect_EN')
ABC_SELECT_RU = L('ABCSelect_RU')
ABC_SELECT_OTHER = L('ABCSelect_OTHER')
SEARCH = L('Search')
SEARCH_PROMPT = L('SearchPrompt')
EMPTY_RESULT_TITLE = L('EmptyResultTitle')
EMPTY_RESULT_MESSAGE = L('EmptyResultMessage')
TRANSLATION = L('Translation')
UNKNOWN_TRANSLATOR = L('UnknownTranslator')
ADD_BOOKMARK_TITLE = L('AddBookmarkTitle')
REMOVE_BOOKMARK_TITLE = L('RemoveBookmarkTitle')
ADD_BOOKMARK_MESSAGE = L('AddBookmarkMessage')
REMOVE_BOOKMARK_MESSAGE = L('RemoveBookmarkMessage')

BOOKMARK = L('BookmarkList')
BOOKMARK_ADDED_MESSAGE = L('BookmarkListAddedMessage')
BOOKMARK_REMOVED_MESSAGE = L('BookmarkListRemovedMessage')

BOOKMARK_CLEAR_TITLE = L('BookmarkListClearTitle')
BOOKMARK_CLEAR_MESSAGE = L('BookmarkListClearMessage')
BOOKMARK_CLEARED_MESSAGE = L('BookmarkListClearedMessage')
BOOKMARK_EMPTY_MESSAGE = L('BookmarkListEmptyMessage')

CLEAR_BOOKMARK = L('ClearBookmark')

MISSING_API_KEY_TITLE = L('MissingAPIKeyTitle')
MISSING_API_KEY_MESSAGE = L('MissingAPIKeyMessage')
UNAUTHORIZED_TITLE = L('UnauthorizedTitle')
UNAUTHORIZED_MESSAGE = L('UnauthorizedMessage')
IP_BLOCKED_TITLE = L('IpBlockedTitle')
IP_BLOCKED_MESSAGE = L('IpBlockedMessage')
NO_PREMIUM_MESSAGE = L('NoPremiumMessage')
ERROR_TITLE = L("ErrorTitle")

ART = 'art-default.jpg'

ICON_DEFAULT = 'icon-default.png'
ICON_RESUME = 'icon-resume.png'
ICON_LATEST = 'icon-latest.png'
ICON_COVER = 'icon-cover'
ICON_SEARCH = 'icon-search.png'
ICON_RU = 'icon-ru.png'
ICON_EN = 'icon-en.png'
ICON_OTHER = 'icon-other.png'
ICON_BOOKMARKS = 'icon-bookmark.png'
ICON_ADD_BOOKMARK = 'icon-bookmark.png'
ICON_BOOKMARKS_CLEAR = 'icon-clear.png'


####################################################################################################
# Start and main menu
####################################################################################################


def Start():
    MediaContainer.title1 = UNICODE(NAME)
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON_DEFAULT)
    VideoItem.thumb = R(ICON_DEFAULT)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    HTTP.Headers['Referer'] = 'http://seasonvar.ru'


@handler(PREFIX, NAME, art=ART, thumb=ICON_DEFAULT)
def MainMenu():
    oc = ObjectContainer(
        objects=[
            # Russian ABC category
            DirectoryObject(
                key=Callback(MenuRU, title=ABC_SELECT_RU),
                title=UNICODE(ABC_SELECT_RU),
                thumb=R(ICON_RU)),

            # English ABC category
            DirectoryObject(
                key=Callback(MenuEn, title=ABC_SELECT_EN),
                title=UNICODE(ABC_SELECT_EN),
                thumb=R(ICON_EN)),

            # Symbols category
            DirectoryObject(
                key=Callback(MenuOther, title=ABC_SELECT_OTHER),
                title=UNICODE(ABC_SELECT_OTHER),
                thumb=R(ICON_OTHER)),

            # Latest category
            DirectoryObject(
                key=Callback(MenuLatest, title=LATEST_SERIALS),
                title=UNICODE(LATEST_SERIALS),
                thumb=R(ICON_LATEST)),

            # Bookmarks category
            DirectoryObject(
                key=Callback(MenuBookmarks, title=BOOKMARK),
                title=UNICODE(BOOKMARK),
                thumb=R(ICON_BOOKMARKS)),

            # Search category (Only visible on TV)
            InputDirectoryObject(
                key=Callback(MenuSearch),
                title=UNICODE(SEARCH),
                prompt=SEARCH_PROMPT,
                thumb=R(ICON_SEARCH))
        ]
    )

    return oc


######################################################################################
# Parse TV show list
######################################################################################


@route(PREFIX + "/search")
def MenuSearch(query):
    # check for API KEY
    if not is_api_key_set():
        return display_missing_api_key_message()

    # check for API URL
    if not is_api_url_set():
        return display_missing_api_url_message()

    oc = ObjectContainer(title1=query)

    # setup the search request url
    values = {
        'key': Prefs["key"],
        'command': 'search',
        'query': query
    }

    # do http request for search data
    request = HTTP.Request(Prefs["url"], values=values, cacheTime=CACHE_1DAY)
    response = json.loads(request.content)

    # check response
    response_check = is_response_ok(response)
    if not response_check == "ok":
        return display_message(response_check[0], response_check[1])

    for season in response:
        name = season.get('name') + ', S' + season.get('season')[0]
        oc.add(
            TVShowObject(
                rating_key=name,
                key=Callback(get_season_by_id, id=season.get('id')),
                title=UNICODE(name),
                summary=UNICODE(filter_non_printable(season.get('description'))),
                thumb=Resource.ContentsOfURLWithFallback(url=season.get('poster_small'), fallback=ICON_COVER)
            )
        )
    return oc


######################################################################################
# Menu latest
######################################################################################


@route(PREFIX + "/latest")
def MenuLatest(title):
    # check for API KEY
    if not is_api_key_set():
        return display_missing_api_key_message()

    # check for API URL
    if not is_api_url_set():
        return display_missing_api_url_message()

    # setup the search request url
    values = {
        'key': Prefs["key"],
        'command': 'getUpdateList',
        'day_count': '1'
    }

    # do http request for search data
    request = HTTP.Request(Prefs["url"], values=values, cacheTime=CACHE_1DAY)
    response = json.loads(request.content)

    # check response
    response_check = is_response_ok(response)
    if not response_check == "ok":
        return display_message(response_check[0], response_check[1])

    oc = ObjectContainer(title1=UNICODE(title))
    for serial in response:
        serial_id = serial.get('id')
        serial_title = serial.get('name')
        serial_thumb = serial.get('poster_small')
        serial_summary = filter_non_printable(serial.get('message'))

        oc.add(
            TVShowObject(
                key=Callback(get_season_by_id, id=serial_id),
                rating_key=serial_title,
                title=UNICODE(serial_title),
                summary=UNICODE(serial_summary),
                thumb=Resource.ContentsOfURLWithFallback(url=serial_thumb)
            )
        )

    return oc


######################################################################################
# Choose by alphabet
######################################################################################


@route(PREFIX + "/en")
def MenuEn(title):
    abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z']

    oc = ObjectContainer(title1=UNICODE(title))
    for letter in abc:
        oc.add(DirectoryObject(key=Callback(get_serial_list_by_title, 
                                            title=UNICODE(letter)), 
                               title=UNICODE(letter)))
    return oc


@route(PREFIX + "/ru")
def MenuRU(title):
    abc = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
           'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я']

    oc = ObjectContainer(title1=UNICODE(title))
    for letter in abc:
        oc.add(DirectoryObject(key=Callback(get_serial_list_by_title, 
                                            title=UNICODE(letter)), 
                               title=UNICODE(letter)))
    return oc


@route(PREFIX + "/other")
def MenuOther(title):
    abc = ['.', '+', '#', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

    oc = ObjectContainer(title1=UNICODE(title))
    for letter in abc:
        oc.add(DirectoryObject(key=Callback(get_serial_list_by_title, 
                                            title=UNICODE(letter)), 
                               title=UNICODE(letter)))
    return oc


######################################################################################
# List serial by selected letter
######################################################################################


@route(PREFIX + "/get_serial_list_by_title")
def get_serial_list_by_title(title):
    # check for API KEY
    if not is_api_key_set():
        return display_missing_api_key_message()

    # check for API URL
    if not is_api_url_set():
        return display_missing_api_url_message()

    values = {'key': Prefs["key"], 'command': 'getSerialList', 'letter': title}

    # do http request for search data
    request = HTTP.Request(Prefs["url"], values=values, cacheTime=CACHE_1DAY)
    response = json.loads(request.content)

    # check response
    response_check = is_response_ok(response)
    if not response_check == "ok":
        return display_message(response_check[0], response_check[1])

    oc = ObjectContainer(title1=UNICODE(title))
    for serial in response:
        serial_title = UNICODE(serial.get('name'))
        
        # check 1st letter of the name, as server returns EVERY letter occurence found
	    if not serial_title.startswith(title):
	        continue
        
        
        serial_thumb = serial.get('poster_small')
        serial_summary = UNICODE(filter_non_printable(serial.get('description')))
        serial_country = serial.get('country')

        oc.add(
            TVShowObject(
                rating_key=serial_title,
                key=Callback(get_season_list_by_title, 
                             title=serial_title),
                title=serial_title,
                summary=serial_summary,
                countries=[serial_country],
                thumb=Resource.ContentsOfURLWithFallback(url=serial_thumb)
            )
        )
    return oc


@route(PREFIX + "/get_season_list_by_title")
def get_season_list_by_title(title):
    # check for API KEY
    if not is_api_key_set():
        return display_missing_api_key_message()

    # check for API URL
    if not is_api_url_set():
        return display_missing_api_url_message()

    values = {
        'key': Prefs["key"],
        'command': 'getSeasonList',
        'name':UNICODE(title)
    }

    request = HTTP.Request(Prefs["url"], values=values, cacheTime=CACHE_1DAY)
    response = json.loads(request.content)

    # check response
    response_check = is_response_ok(response)
    if not response_check == "ok":
        return display_message(response_check[0], response_check[1])

    oc = ObjectContainer(title1=UNICODE(title))
    for season in response:
        season_id = season.get('id')
        season_number = season.get('season_number') or "1"

        oc.add(SeasonObject(
            rating_key=season_id,
            key=Callback(get_season_by_id, id=season_id),
            title=UNICODE(SEASON_TITLE + ' ' + season_number),
            index=int(season_number),
            summary=UNICODE(filter_non_printable(season.get('description'))),
            thumb=Resource.ContentsOfURLWithFallback(url=season.get('poster_small'), fallback=ICON_COVER)
        ))
    return oc


@route(PREFIX + "/get_season_by_id")
def get_season_by_id(id):
    # check for API KEY
    if not is_api_key_set():
        return display_missing_api_key_message()

    # check for API URL
    if not is_api_url_set():
        return display_missing_api_url_message()

    values = {
        'key': Prefs["key"],
        'command': 'getSeason',
        'season_id': id
    }

    request = HTTP.Request(Prefs["url"], values=values, cacheTime=CACHE_1DAY)
    response = json.loads(request.content)

    display_message('JSON', response)

    # check response
    response_check = is_response_ok(response)
    if not response_check == "ok":
        return display_message(response_check[0], response_check[1])

    playlist = response.get('playlist')

    # form new dictionary based on the translation
    key = 0
    translation = ""
    translations = {}
    translations_list = []
    for video in playlist:

        # check if there are > 1 translation
        if 'perevod' in video:
            translation = video.get('perevod')
        else:
            if 'perevod' in response:
                translation = response.get('perevod')
            else:
                translation = "__default__"

        # check for missing key index;
        try:
           key = translations_list.index(translation)
        except ValueError:
            translations_list.append(translation)
        finally:
            # at this point translation was added into the list
            # get index
            key = translations_list.index(translation)

        # add video into desired translation list
        if key not in translations:
            translations[key] = []

        episode = 0;
        try:
            episode = int(video.get('name').split(" ")[0])
        except ValueError:
            # These idiots don't follow their own format for the data
            # and provide incorrect values
            episode = 0

        translations[key].append({
            "name": video.get('name'),
            "link": video.get('link'),
            "episode": episode
        })

        # todo: add subtitles
        # video.get('subtitles')

    # Store current response into global Dict
    Dict['cache'] = {
        'id': response.get('id'),
        'name': response.get('name'),
        'poster': response.get('poster'),
        'poster_small': response.get('poster_small'),
        'description': filter_non_printable(response.get('description')),
        'rating': response.get('rating'),
        'playlist': translations,
        'playlist_mapping': translations_list,
        'season': response.get('season_number') or "1"
    }
    Dict.Save()

    if len(translations) == 1:
        return display_season(id=key, season=response.get('season_number') or "1")
    else:
        # render translations
        MediaContainer.art = Resource.ContentsOfURLWithFallback(url=response.get('poster'), fallback=ART)

        title = str(response.get('name') + " ")
        oc = ObjectContainer(title1=UNICODE(title))
        for key in translations:
            title2 = str(TRANSLATION) % translations_list[key]
            if translations_list[key] == '__default__':
                title2 = str(TRANSLATION) % str(UNKNOWN_TRANSLATOR)
            oc.add(DirectoryObject(key=Callback(display_season,
                                                id=key,
                                                season=response.get('season_number') or "1"),
                                                title=UNICODE(title2 + " (" + str(len(translations[key])) + ")")))
        return oc


@route(PREFIX + "/display_season")
def display_season(id, season):
    response = Dict['cache']
    MediaContainer.art = Resource.ContentsOfURLWithFallback(url=response.get('poster'), fallback=ART)

    title1 = response.get('name')

    # fix 0 season
    if season == "0":
        season = "1"

    title2 = str(SEASON_TITLE) + " " + season
    oc = ObjectContainer(title1=UNICODE(title1), title2=UNICODE(title2))

    playlist = response.get('playlist')[int(id)]
    for video in playlist:
        video_link = video.get('link')
        video_name = video.get('name')
        video_episode = video.get('episode')

        oc.add(create_eo(
            url=video_link,
            title=UNICODE(video_name),
            summary=UNICODE(filter_non_printable(response.get('description'))),
            rating=averageRating(response.get('rating')),
            thumb=response.get('poster_small'),
            index=video_episode,
            season=season,
            show=UNICODE(filter_non_printable(title1))
        ))

    if has_bookmark(response.get('id')):

        # show is already in the bookmarks
        oc.add(DirectoryObject(
            key=Callback(remove_bookmark, id=response.get('id')),
            title=UNICODE(REMOVE_BOOKMARK_TITLE),
            summary=UNICODE(response.get('name') + REMOVE_BOOKMARK_MESSAGE),
            thumb=R(ICON_BOOKMARKS_CLEAR)
        ))
    else:

        # show is not in the bookmarks
        oc.add(DirectoryObject(
            key=Callback(add_bookmark, 
                         title=UNICODE(response.get('name')), 
                         id=response.get('id'), 
                         thumb=response.get('poster'),
                         summary=UNICODE(filter_non_printable(response.get('description')))),
            title=UNICODE(ADD_BOOKMARK_TITLE),
            summary=UNICODE(response.get('name') + ADD_BOOKMARK_MESSAGE),
            thumb=R(ICON_ADD_BOOKMARK)
        ))

    return oc


@route(PREFIX + "/create_eo")
def create_eo(url, title, summary, rating, thumb, index, show, season="1", include_container=False):
    eo = EpisodeObject(
        rating_key=url,
        key=Callback(create_eo,
                     url=url, 
                     title=UNICODE(filter_non_printable(title)),
                     summary=UNICODE(filter_non_printable(summary)),
                     rating=rating,
                     thumb=thumb,
                     index=int(index),
                     season=int(season),
                     show=UNICODE(filter_non_printable(show)),
                     include_container=True),
        title=UNICODE(filter_non_printable(title)),
        summary=UNICODE(filter_non_printable(summary)),
        rating=float(rating),
        thumb=thumb,
        season=int(season),
        index=int(index),
        show=UNICODE(filter_non_printable(show)),
        items=[
            MediaObject(
                parts=[
                    PartObject(key=url)
                ],
                container=Container.MP4,
                video_codec=VideoCodec.H264,
                video_resolution=1080,
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
def MenuBookmarks(title):
    count = 0
    if 'bookmarks' in Dict:
        oc = ObjectContainer(title1=title)
        for show_id in Dict['bookmarks']:
            count += 1
            show = Dict['bookmarks'][show_id]
            show_title = show.get('title')
            oc.add(
                TVShowObject(
                    rating_key=show_title,
                    key=Callback(get_season_by_id, id=show_id),
                    title=UNICODE(show_title),
                    summary=UNICODE(show.get('summary')),
                    thumb=Resource.ContentsOfURLWithFallback(url=show.get('thumb'))
                )
            )

        if count > 0:
            # add a way to clear bookmarks list
            oc.add(DirectoryObject(
                key=Callback(clear_bookmarks),
                title=UNICODE(BOOKMARK_CLEAR_TITLE),
                thumb=R(ICON_BOOKMARKS_CLEAR),
                summary=UNICODE(BOOKMARK_CLEAR_MESSAGE)
            ))

            return oc
    return MessageContainer(
        BOOKMARK,
        BOOKMARK_EMPTY_MESSAGE
    )


@route(PREFIX + "/addbookmark")
def add_bookmark(title, id, thumb, summary):
    # initiate new dictionary for bookmarks
    if 'bookmarks' not in Dict:
        Dict['bookmarks'] = {}

    Dict['bookmarks'][id] = dict(title=title, thumb=thumb, summary=summary)
    Dict.Save()

    return MessageContainer(
        BOOKMARK,
        BOOKMARK_ADDED_MESSAGE
    )


@route(PREFIX + "/removebookmark")
def remove_bookmark(id):
    if has_bookmark(key=id):
        try:
            del Dict['bookmarks'][id]
            Dict.Save()
        except KeyError:
            pass

    return MessageContainer(
        BOOKMARK,
        BOOKMARK_REMOVED_MESSAGE
    )


# There is a bug in Dict.Reset() function;
# So, delete internal 'bookmarks' dictionary
@route(PREFIX + "/clearbookmarks")
def clear_bookmarks():
    try:
        del Dict['bookmarks']
        Dict.Save()
    except KeyError:
        pass

    return MessageContainer(
        BOOKMARK,
        BOOKMARK_CLEARED_MESSAGE
    )


def has_bookmark(key):
    if 'bookmarks' in Dict:
        return key in Dict['bookmarks']

    return False


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


def is_api_key_set():
    return Prefs["key"]


def is_api_url_set():
    return Prefs["url"]


def is_response_ok(response):
    if response == "":
        return [EMPTY_RESULT_TITLE, EMPTY_RESULT_MESSAGE]
    elif 'error' in response:
        error = response.get('error')

        if error == "Authentication::getUser::wrong key":
            return [ERROR_TITLE, UNAUTHORIZED_MESSAGE]
        elif error == "Authorization::checkRules::this ip is not allowed":
            return [ERROR_TITLE, IP_BLOCKED_MESSAGE]
        elif error == "Authorization::checkRules::user has no premium status":
            return [ERROR_TITLE, NO_PREMIUM_MESSAGE]
        else:
            return [ERROR_TITLE, error]

    return "ok"


def display_message(title, message):
    return MessageContainer(title, message)


def display_missing_api_key_message():
    return display_message(title=MISSING_API_KEY_TITLE, message=MISSING_API_KEY_MESSAGE)


def display_missing_api_url_message():
    return display_message(title=MISSING_API_KEY_TITLE, message=MISSING_API_KEY_MESSAGE)


def filter_non_printable(s):
    if s is None:
        return ""
    else:
        return re.sub(r'[^\\[\\]]', '', s, re.UNICODE)

def UNICODE(arg):
    return unicode(str(arg), "UTF-8")
