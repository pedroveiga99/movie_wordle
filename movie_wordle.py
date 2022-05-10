import requests
from random import randint
import pandas as pd
import urllib

v3_key = '0899fa1b2f8aa8b61bea873616d223be'
v4_key = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwODk5ZmExYjJmOGFhOGI2MWJlYTg3MzYxNmQyMjNiZSIsInN1YiI6IjYyNTQwZWVhZmQ2MzAwNmU0YzBkYjg1ZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.cyBTY0snLC4VEnkH5yf_1nW-WOXZ041dQD5tPZ6UXPY'

list_key = '8198267'

api_root = 'https://api.themoviedb.org/3'

run = True

NUM_COMP_ACTORS = 15
LIVES = 2

def help():
    return 'string de ajuda'


def get_try():
    tentativa = input('Qual é a sua tentativa de filme?  ')

    while not tentativa:
        tentativa = input('Qual é a sua tentativa de filme?  ')

    tentativa = {'query': tentativa}
    tentativa = urllib.parse.urlencode(tentativa)

    query = '{}/search/movie?api_key={}&{}'.format(api_root, v3_key, tentativa)
    response = requests.get(query)
    response = response.json()

    # Assumindo que a melhor hipotese é a primeira
    try_movie_id = response['results'][0]['id']

    query = '{}/movie/{}?api_key={}'.format(api_root, try_movie_id, v3_key)
    response = requests.get(query)
    response = response.json()

    try_movie_info = pd.Series(response)
    print(try_movie_info)

    return try_movie_info


def compare_movies(selected_movie, selected_cast, try_movie):
    # Compare the different characteristics
    comp = {}

    # Release year
    # The result is the diff in years. Positive = try_movie was released earlier
    r_year = int(selected_movie.release_date[0:4]) - int(try_movie.release_date[0:4])
    comp['r_year'] = r_year

    # Genres
    common_genres = []
    selected_genres = selected_movie.genres
    try_genres = try_movie.genres
    try_genres_set = set()

    for genre in try_genres:
        try_genres_set.add(genre['id'])

    for genre in selected_genres:
        if genre['id'] in try_genres_set:
            common_genres.append(genre['name'])

    comp['common_genres'] = common_genres

    # Saga
    try:
        saga = selected_movie.belongs_to_collection['id'] == try_movie.belongs_to_collection['id']
    except:
        saga = False
    comp['saga'] = saga

    # Vote average
    # The result is the diff in votes. Positive = try_movie is 'worse'
    vote = float(selected_movie.vote_average) - float(try_movie.vote_average)
    comp['vote'] = vote

    # Cast
    # Get the try movie cast
    common_actors = []
    query = '{}/movie/{}/credits?api_key={}'.format(api_root, try_movie.id, v3_key)
    response = requests.get(query)
    response = response.json()
    try_movie_cast = pd.DataFrame.from_dict(response['cast'], orient='columns')
    try_movie_cast = try_movie_cast[try_movie_cast.known_for_department == 'Acting']
    try_movie_cast = try_movie_cast.sort_values('popularity', ascending=False).reset_index(drop=True)[:NUM_COMP_ACTORS]

    for try_id in try_movie_cast.id:
        if try_id in selected_cast:
            name = try_movie_cast[try_movie_cast.id == try_id]['name'].to_string(index=False)
            common_actors.append(name)
    comp['cast'] = common_actors

    return comp


def jogo():
    correct = False
    lives = LIVES

    # Get all movies from the list and chose one, randomly
    query = '{}/list/{}?api_key={}'.format(api_root, list_key, v3_key)

    response = requests.get(query)
    response = response.json()
    movie_list = response['items']

    selection = randint(0, len(movie_list) - 1)
    selected_movie_id = movie_list[selection]['id']

    # Get all information about the movie
    query = '{}/movie/{}?api_key={}'.format(api_root, selected_movie_id, v3_key)
    response = requests.get(query)
    response = response.json()
    selected_movie_info = pd.Series(response)
    print(selected_movie_info)

    # Get the movie cast
    query = '{}/movie/{}/credits?api_key={}'.format(api_root, selected_movie_id, v3_key)
    response = requests.get(query)
    response = response.json()
    selected_movie_cast = pd.DataFrame.from_dict(response['cast'], orient='columns')
    selected_movie_cast = selected_movie_cast[selected_movie_cast.known_for_department == 'Acting']
    selected_movie_cast = selected_movie_cast.sort_values('popularity', ascending=False).reset_index(drop=True)
    selected_movie_cast = selected_movie_cast[:NUM_COMP_ACTORS]
    selected_movie_cast_ids = set()
    for index, actor in selected_movie_cast.iterrows():
        selected_movie_cast_ids.add(actor.id)
    # print(selected_movie_cast)

    while (not correct) and (lives > 0):
        # Tentativa
        try_movie_info = get_try()

        if try_movie_info.id == selected_movie_info.id:  # correct anwser
            correct = True
            continue
        else:  # wrong anwser
            lives -= 1

        # Give a final hint
        if lives == 1:
            print('A little help. The movie tagline is:')
            print(selected_movie_info.tagline)

        comp = compare_movies(selected_movie_info, selected_movie_cast_ids, try_movie_info)
        print(comp)

    # Check if it is a win or lose
    if correct:
        print('Congratulations! You won!')
    elif lives <= 0:
        print('You suck! The correct movie was: {}'.format(selected_movie_info.original_title))
    else:
        # Usually it is not supose to get here
        print('Upsi, houve um erro qualquer')


def main():
    run = True

    while run:
        resposta = input('Inserir: ')

        match resposta:
            case 'h':
                print(help())
            case 'x':
                run = False
                print('Obrigado por jogar')
            case 'j':
                jogo()
            case _:  # default
                print('outra coisa')


if __name__ == '__main__':
    intro_text = """
    Bem vindo ao Movie Wordle!\n
    Este é um jogo semelhante ao wordle mas com o objetivo de adivinhar um filme aleatório.
    Por cada resposta errada será indicado ... Pode também, a qualquer momento, pedir uma dica.
    Para ver melhor as regras insira 'h'; Para jogar insira 'j'; Para sair insira 'x'.
    """
    print(intro_text)
    main()
