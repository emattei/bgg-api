import requests
import time
from bs4 import BeautifulSoup
from typing import Optional
from xml.etree import ElementTree as ET


def _get_with_rate_limit(url, delay_seconds=1):
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                print("Rate limit exceeded. Waiting...")
                time.sleep(delay_seconds)
            else:
                raise


def get_author_id(author_name: str,
                  api_root_path: str = 'https://www.boardgamegeek.com/xmlapi2'
                  ) -> Optional[str]:
    """
    Retrieves the ID of a board game designer based on their name.

    Args:
        author_name (str): The name of the board game designer.
        api_root_path (str, optional): The root path of the API.
          Defaults to 'https://www.boardgamegeek.com/xmlapi2'.

    Returns:
        Optional[str]: The ID of the board game designer, or None if not found.
    """
    response = _get_with_rate_limit(
        f'{api_root_path}/search?query={author_name}&type=boardgamedesigner'
        )
    root = ET.fromstring(response.text)
    item = root.find('item')
    return item.get('id') if item is not None else None


def _get_publisher_id_helper(html: str, publisher_name: str) -> str:
    """
    Helper function to extract the publisher ID from the HTML content.

    Args:
        html (str): The HTML content to search for the publisher ID.
        publisher_name (str): The name of the publisher to search for.

    Returns:
        str: The publisher ID if found, or None if no matching publisher
          is found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if publisher_name in href:
            # The ID is the third element when we split the href by '/'
            return href.split('/')[2]
    return None  # Return None if no matching publisher is found


def get_publisher_id(publisher_name: str,
                     landing_page="https://boardgamegeek.com/browse/boardgamepublisher"
                     ) -> str:
    """
    Retrieves the ID of a board game publisher based on their name.

    Args:
        html (str): The HTML content of the page containing the list of
          board game publishers.
        publisher_name (str): The name of the board game publisher.

    Returns:
        str: The ID of the board game publisher.
    """
    page_id = 1
    # Fetch the list of all board games
    response = _get_with_rate_limit(f"{landing_page}/page/{page_id}")
    html = response.text
    return _get_publisher_id_helper(html, publisher_name)


def get_game_publisher(game_id: str,
                       api_root_path: str = 'https://www.boardgamegeek.com/xmlapi2'
                       ) -> Optional[str]:
    """
    Retrieves the publisher of a board game based on its ID.

    Args:
        game_id (str): The ID of the board game.
        api_root_path (str, optional): The root path of the API.
            Defaults to 'https://www.boardgamegeek.com/xmlapi2'.

    Returns:
        Optional[str]: The publisher of the board game, or None if not found.
    """
    response = _get_with_rate_limit(
        f'{api_root_path}/thing?id={game_id}&type=boardgame'
        )
    root = ET.fromstring(response.text)
    item = root.find('item')
    if not item:
        return None
    link = item.find("link[@type='boardgamepublisher']")
    return link.get('value') if link is not None else None


def get_game_designer(game_id: str,
                      api_root_path: str = 'https://www.boardgamegeek.com/xmlapi2'
                      ) -> dict:
    """
    Retrieves the designer of a board game based on its ID.

    Args:
        game_id (str): The ID of the board game.
        api_root_path (str, optional): The root path of the API.
            Defaults to 'https://www.boardgamegeek.com/xmlapi2'.

    Returns:
        Optional[str]: The designer of the board game, or None if not found.
    """
    response = _get_with_rate_limit(
        f'{api_root_path}/thing?id={game_id}&type=boardgame'
        )
    root = ET.fromstring(response.text)
    item = root.find('item')
    link = item.find("link[@type='boardgamedesigner']")
    return link.get('value') if link is not None else None


def get_all_games_from_author(author_id: str,
                              sleep_time=10, api_root_path: str = "https://api.geekdo.com/api/geekitem"
                              ) -> list:
    """
    Retrieves the list of all board games designed by a specific author.

    Args:
        author_id (str): The ID of the board game designer.
        api_root_path (str): The root path of the API.
            Defaults to 'https://api.geekdo.com/api/geekitem'.

    Returns:
        list: A list of dictionaries containing the details of the board games.
        Each dictionary contains the following:
            - title: The title of the board game.
            - year: The year the board game was published.
            - average_score: The average score of the board game.
            - average_weight: The average weight of the board game.
            - publisher: The publisher of the board game.
            - bgg_id: The ID of the board game on BoardGameGeek.
    """
    page_id = 1
    games = []
    while True:
        response = _get_with_rate_limit(
            f'{api_root_path}/linkeditems?ajax=1&linkdata_index=boardgamedesigner&objectid={author_id}&objecttype=person&showcount=50&sort=name&subtype=boardgame&pageid={page_id}',
              sleep_time)
        data = response.json()
        if not data['items']:
            break
        for item in data['items']:
            print(item['objectid'], item['name'])
            game = {
                'title': item['name'],
                'year': item['yearpublished'],
                'average_score': item['average'],
                'average_weight': item['avgweight'],
                'publisher': get_game_publisher(item['objectid']),
                'bgg_id': item['objectid'],
                'rank': item['rank'] if 'rank' in item else 'N/A'
            }
            games.append(game)
        page_id += 1
    return games


def get_all_games_from_publisher(publisher_id,
                                 sleep_time=10, api_root_path="https://api.geekdo.com/api/geekitem"
                                 ):
    """
    Retrieves all games from a specific publisher using the BoardGameGeek API.

    Args:
        publisher_id (int): The ID of the publisher.
        sleep_time (int, optional): The time to sleep between API requests.
            Defaults to 10.
        api_root_path (str, optional): The root path of the API.
            Defaults to "https://api.geekdo.com/api/geekitem".

    Returns:
        list: A list of dictionaries representing the games:
            - title (str): The title of the game.
            - year (int): The year the game was published.
            - designer (str): The designer of the game.
            - average_score (float): The average score of the game.
            - average_weight (float): The average weight of the game.
            - publisher (int): The ID of the publisher.
            - bgg_id (int): The BoardGameGeek ID of the game.
            - rank (int or str): The rank of the game, or 'N/A' if not available.
    """
    page_id = 1
    games = []
    while True:
        response =_get_with_rate_limit(
            f"{api_root_path}/linkeditems?ajax=1&linkdata_index=boardgame&nosession=1&objectid={publisher_id}&objecttype=company&pageid={page_id}&showcount=1000&sort=name&subtype=boardgamepublisher",
            sleep_time)
#        https://api.geekdo.com/api/geekitem/recs/boardgamepublisher?ajax=1&linkdata_index=boardgame&objectid=56502&objecttype=company&pageid=1
        data = response.json()
        if not data['items']:
            break
        for item in data['items']:
            game = {
                'title': item['name'],
                'year': item['yearpublished'],
                'designer': get_game_designer(item['objectid']),
                'average_score': item['average'],
                'average_weight': item['avgweight'],
                'publisher': publisher_id,
                'bgg_id': item['objectid'],
                'rank': item['rank'] if 'rank' in item else 'N/A'
            }
            games.append(game)
        page_id += 1
    return games
