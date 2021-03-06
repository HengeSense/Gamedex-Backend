"""gameSources.py: Import Games from third party sources: Steam, PSN and XBL """

__author__ = "Michael Martin"
__status__ = "Production"

import StringIO
import gzip
import json
import logging

from google.appengine.api import urlfetch

from lxml.cssselect import CSSSelector
from lxml import etree


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getSteamGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSteamGames(id):

    url = 'http://steamcommunity.com/id/%s/games?tab=all' % id

    headers = {'Accept-Encoding': 'gzip'}

    # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
    # allow 30 seconds for response
    response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

    # decompress
    f = StringIO.StringIO(response.content)
    c = gzip.GzipFile(fileobj=f)
    content = c.read()

    if response.status_code == 200:

        html = etree.HTML(content)
        scriptSel = CSSSelector('script')

        gamesScript = ''

        # iterate all script tags and find rgGames in script
        for row in scriptSel(html):
            if (row.text is not None and 'rgGames' in row.text):
                gamesScript = row.text

        # parse json in gamesScript
        jsonString = gamesScript[gamesScript.find('['):gamesScript.find(']') + 1]
        jsonObj = json.loads(jsonString)

        # clean json
        gameList = []
        for game in jsonObj:
            gameList.append(game['name'])

        return gameList


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getPSNGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getPSNGames(id):

    # GET /playstation/psn/profile/[psn_id]/get_ordered_trophies_data HTTP/1.1
    # Host    us.playstation.com
    # X-Requested-With    XMLHttpRequest
    # User-Agent  Mozilla
    # Accept  text/html
    # Accept-Encoding gzip,deflate,sdch
    # Accept-Charset    ISO-8859-1,utf-8;q=0.7,*;q=0.3

    # playstation user games/trophy url
    url = 'http://us.playstation.com/playstation/psn/profile/%s/get_ordered_trophies_data' % (id)

    # headers required for response
    headers = {'Host': 'us.playstation.com', 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept': 'text/html', 'Accept-Encoding': 'gzip'}

    # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
    # allow 30 seconds for response
    response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

    # decompress
    f = StringIO.StringIO(response.content)
    c = gzip.GzipFile(fileobj=f)
    content = c.read()

    # valid response - begin parse
    if response.status_code == 200:

        # game titles imported
        importedTitles = []

        # iterate game list
        html = etree.HTML(content)

        titleSectionSel = CSSSelector('.titlesection')
        titleSel = CSSSelector('.gameTitleSortField')

        # for each game > get title
        for row in titleSectionSel(html):

            try:
                titleElement = titleSel(row)

                # get game title as plain ascii and remove non-ascii characters
                gameTitle = titleElement[0].text.encode('ascii', 'ignore').strip()

                # add title
                importedTitles.append(gameTitle)

            except IndexError:
                logging.error('PSN Import: IndexError')

        return importedTitles


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getXBLGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getXBLGames(id):

    # convert spaces to +
    id = id.replace(' ', '+')

    # url
    url = 'http://www.xboxgamertag.com/search/%s' % (id)

    headers = {'Accept-Encoding': 'gzip'}

    # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
    # allow 30 seconds for response
    response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30, True)

    # decompress
    f = StringIO.StringIO(response.content)
    c = gzip.GzipFile(fileobj=f)
    content = c.read()

    logging.info(content)

    # valid response - begin parse
    if response.status_code == 200:

        # game titles imported
        importedTitles = []

        # iterate game list
        html = etree.HTML(content)

        titleSectionSel = CSSSelector('#recentGamesTable tr')
        titleSel = CSSSelector('.gameName a')

        # for each game > get title
        for row in titleSectionSel(html):

            try:
                titleElement = titleSel(row)

                # get game title as plain ascii and remove non-ascii characters
                gameTitle = titleElement[0].text.encode('ascii', 'ignore').strip()

                # add title
                importedTitles.append(gameTitle)

            except IndexError:
                logging.error('XBL Import: IndexError')

        return importedTitles
