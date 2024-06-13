from utils import get_publisher_id, get_all_games_from_publisher
from collections import Counter

# The name of the publisher
publisher_name = "4am-brain-llc"
# Get the ID of the author
publisher_id = get_publisher_id(publisher_name)
print(f"'{publisher_name}' bgg publisher id is: {publisher_id}")

games_from_publisher = get_all_games_from_publisher(publisher_id)

print(f"'{publisher_name}' has designed {len(games_from_publisher)} games")

#sort by year
games_from_publisher.sort(key=lambda x: x['year'])

print(f"'{publisher_name}' first game was {games_from_publisher[0]['title']}, published in {games_from_publisher[0]['year']}")
print(f"'{publisher_name}' last game is {games_from_publisher[-1]['title']}, published in {games_from_publisher[-1]['year']}")
print(f"'{publisher_name}' average score is {sum([float(x['average_score']) for x in games_from_publisher])/len(games_from_publisher)}")
print(f"'{publisher_name}' average weight is {sum([float(x['average_weight']) for x in games_from_publisher])/len(games_from_publisher)}")


authors = Counter()
for game in games_from_publisher:
    designer = game['designer']
    authors[designer] += 1

preferred_author = authors.most_common(1)[0]

print(f"The author who has published the most games with {publisher_name} is {preferred_author[0]} with {preferred_author[1]} games.")
