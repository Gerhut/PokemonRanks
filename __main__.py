from math import floor
from datetime import datetime
from os import environ

from dotenv import load_dotenv
from github import Github, InputFileContent
from requests import post

language_id = 9  # Chinese
generation_id = 4  # Ultra Sun / Ultra Moon
battle_type = 2  # Double battle


def request_pokemon_global_link(url, data={}, **kwargs):
    url = 'https://3ds.pokemon-gl.com/frontendApi' + url

    timestamp = floor(datetime.now().timestamp() * 1000)
    data = dict({
        'languageId': language_id,
        'timezone': 'UTC',
        'timeStamp': timestamp,
    }, **data)

    headers = {
        'Referer': 'https://3ds.pokemon-gl.com/',
    }

    response = post(url, data=data, headers=headers, **kwargs)
    response.raise_for_status()

    data = response.json()
    assert data['status_code'] == '0000', data

    return response


def get_cookies():
    response = request_pokemon_global_link('/getLoginStatus')

    return response.cookies


def get_latest_season(cookies):
    response = request_pokemon_global_link('/gbu/getSeason', {
        'generationId': generation_id,
    }, cookies=cookies)

    data = response.json()
    latest_season = data['seasonInfo'][0]
    return latest_season


def get_pokemons(season, cookies):
    response = request_pokemon_global_link('/gbu/getSeasonPokemon', {
        'seasonId': season['seasonId'],
        'battleType': battle_type,
    }, cookies=cookies)

    data = response.json()
    pokemons = data['rankingPokemonInfo']
    return pokemons


def update_github_gist(github_token, gist_id, gist_description_prefix,
                       gist_filename, pokemons):
    pokemon_names = [pokemon['name'] for pokemon in pokemons]
    content = '\n'.join(pokemon_names)

    github = Github(github_token)
    gist = github.get_gist(gist_id)

    description = '{0} @ {1:%c}'.format(
        gist_description_prefix, datetime.now())
    files = {gist_filename: InputFileContent(content)}

    gist.edit(description, files)


def main():
    load_dotenv()

    cookies = get_cookies()
    season = get_latest_season(cookies=cookies)
    pokemons = get_pokemons(season, cookies=cookies)
    update_github_gist(
        environ['GITHUB_TOKEN'],
        environ['GIST_ID'],
        environ['GIST_DESCRIPTION_PREFIX'],
        environ['GIST_FILENAME'],
        pokemons)


main()
