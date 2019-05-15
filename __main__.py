from datetime import datetime
from io import BytesIO
from math import floor
from os import environ
from os.path import join
from shutil import rmtree

from dotenv import load_dotenv
from git import Repo
from github import Github
from PIL import Image
from requests import get, post

language_id = 9  # Chinese
generation_id = 4  # Ultra Sun / Ultra Moon
battle_type = 2  # Double battle


def build_message(message_prefix):
    return '{0} @ {1:%c}'.format(message_prefix, datetime.now())


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

    print('Requesting Pokemon Global Link:', url)

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


def prepare_repository(github_token, gist_id):
    repository = Repo.init('dist')
    remote_url = 'https://{}@gist.github.com/{}.git'.format(
        github_token, gist_id)
    remote = repository.create_remote('origin', remote_url)

    print('Pulling repository:', remote_url)
    remote.pull('master')
    return repository


def get_pokemon_image(pokemon):
    size = 90

    n = pokemon['monsno']
    id = int(pokemon['formNo'])
    '''
    r = (0x1000000 | ((0x159a55e5 * (n + id * 0x10000)) & 0xffffff))
    .toString(16)
    .substr(1);
    '''
    code = hex(0x1000000 | ((0x159a55e5 * (n + id * 0x10000)) & 0xffffff))[3:]
    url = ('https://n-3ds-pgl-contents.pokemon-gl.com'
           '/share/images/pokemon/{}/{}.png').format(size, code)

    print('Fetching pokemon image:', url)

    response = get(url)
    response.raise_for_status()

    content = response.content
    image = Image.open(BytesIO(content))

    half_size = size >> 1

    top_left = image.crop((0, 0, half_size, half_size))
    top_right = image.crop((half_size, 0, size, half_size))
    bottom_left = image.crop((0, half_size, half_size, size))
    bottom_right = image.crop((half_size, half_size, size, size))
    image.paste(top_left, (half_size, half_size))
    image.paste(top_right, (0, half_size))
    image.paste(bottom_left, (half_size, 0))
    image.paste(bottom_right, (0, 0))

    return image


def build_ranking_image(pokemons, repository, gist_filename):
    images = (get_pokemon_image(pokemon) for pokemon in pokemons)

    map = [
        # (left, top, width, height)
        (0, 0, 60, 60),
        (60, 6, 54, 54),
        (114, 12, 48, 48),
        (162, 20, 40, 40),
        (202, 20, 40, 40),
        (242, 20, 40, 40),
        (282, 20, 40, 40),

        (2, 60, 40, 40),
        (42, 60, 40, 40),
        (82, 60, 40, 40),
        (122, 60, 40, 40),
        (162, 60, 40, 40),
        (202, 60, 40, 40),
        (242, 60, 40, 40),
        (282, 60, 40, 40),
    ]

    image = Image.new('RGBA', (325, 100))
    for coordinator in map:
        pokemon_image = images.__next__()
        box = coordinator[0:2]
        size = coordinator[2:4]

        image.paste(pokemon_image.resize(size, Image.LANCZOS), box)

    filename = join(repository.working_tree_dir, gist_filename)
    image.save(filename, 'PNG')


def update_repository(repository, gist_filename, message):
    repository.index.add([gist_filename])
    repository.index.commit(message)

    print('Pushing repository')
    repository.remotes.origin.push('master')
    rmtree('dist')


def update_gist_description(github_token, gist_id, message):
    github = Github(github_token)
    gist = github.get_gist(gist_id)

    print('Updating description:', message)
    gist.edit(description=message)


def main():
    load_dotenv()

    message = build_message(environ['MESSAGE_PREFIX'])

    cookies = get_cookies()
    season = get_latest_season(cookies=cookies)
    pokemons = get_pokemons(season, cookies=cookies)

    repository = prepare_repository(
        environ['GITHUB_TOKEN'], environ['GIST_ID'])
    build_ranking_image(pokemons, repository, environ['GIST_FILENAME'])
    update_repository(repository, environ['GIST_FILENAME'], message)

    update_gist_description(
        environ['GITHUB_TOKEN'], environ['GIST_ID'], message)


main()
