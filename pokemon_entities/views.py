import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    localtime_now = timezone.localtime()

    pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lte=localtime_now,
        disappeared_at__gte=localtime_now
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    pokemons_on_page = []
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        )
        for pokemon in pokemons_on_page:
            if pokemon['title_ru'] == pokemon_entity.pokemon.title:
                break
        else:
            pokemons_on_page.append({
                'pokemon_id': pokemon_entity.pokemon.id,
                'img_url': pokemon_entity.pokemon.image.url,
                'title_ru': pokemon_entity.pokemon.title,
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    pokemon_entities = PokemonEntity.objects.filter(pokemon=pokemon)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        )

    pokemon_card = {
        "pokemon_id": pokemon.id,
        "title_ru": pokemon.title,
        "title_en": pokemon.title_en,
        "title_jp": pokemon.title_jp,
        "description": pokemon.description,
        "img_url": request.build_absolute_uri(pokemon.image.url),
        "next_evolution": {},
        "previous_evolution": {},
    }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_card
    })
