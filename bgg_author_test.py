from utils import get_author_id, get_all_games_from_author, get_game_publisher
from collections import Counter

# The name of the author
author_name = "Reiner Knizia"
#author_name = "Erik Mantsch"
# Get the ID of the author
author_id = get_author_id(author_name)
print(f"'{author_name}' bgg game designer id is: {author_id}")

games_from_author = get_all_games_from_author(author_id, sleep_time=30)

print(f"'{author_name}' has designed {len(games_from_author)} games")

#sort by year
games_from_author.sort(key=lambda x: x['year'])

print(f"'{author_name}' first game was {games_from_author[0]['title']}, published in {games_from_author[0]['year']}")
print(f"'{author_name}' last game is {games_from_author[-1]['title']}, published in {games_from_author[-1]['year']}")
print(f"'{author_name}' average score is {sum([float(x['average_score']) for x in games_from_author])/len(games_from_author)}")
print(f"'{author_name}' average weight is {sum([float(x['average_weight']) for x in games_from_author])/len(games_from_author)}")

publishers = Counter()
for game in games_from_author:
    publisher = get_game_publisher(game['bgg_id'])
    publishers[publisher] += 1


# Find the publisher with the maximum count
preferred_publisher = publishers.most_common(1)[0]

print(f"The publisher who has published the most games of {author_name} is {preferred_publisher[0]} with {preferred_publisher[1]} games.")
