import folium

from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL,
                pokemon_stats=None):
    if pokemon_stats is None:
        pokemon_stats = {}
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    popup_text = f"<b>Location</b>: {lat}, {lon}<hr>"
    for stat, value in pokemon_stats.items():
        popup_text = f"{popup_text}{stat}: {value}<br>"
    folium.Popup(popup_text, max_width='100')

    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        popup=popup_text,
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    localtime_now = timezone.localtime()

    pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lte=localtime_now,
        disappeared_at__gte=localtime_now
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url),
            pokemon_stats={
                "Level": pokemon_entity.level,
                "Health": pokemon_entity.health,
                "Strength": pokemon_entity.strength,
                "Defence": pokemon_entity.defence,
                "Stamina": pokemon_entity.stamina
            }
        )

    pokemons = PokemonEntity.objects.filter(
        appeared_at__lte=localtime_now,
        disappeared_at__gte=localtime_now
    ).values("pokemon__id", "pokemon__title", "pokemon__image").distinct()

    pokemons_on_page = []
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon["pokemon__id"],
            'img_url': request.build_absolute_uri(
                f'media/{pokemon["pokemon__image"]}'
            ),
            'title_ru': pokemon["pokemon__title"]})

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    localtime_now = timezone.localtime()
    pokemon_entities = PokemonEntity.objects.filter(
        pokemon=pokemon,
        appeared_at__lte=localtime_now,
        disappeared_at__gte=localtime_now,
    )
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url),
            pokemon_stats={
                "Level": pokemon_entity.level,
                "Health": pokemon_entity.health,
                "Strength": pokemon_entity.strength,
                "Defence": pokemon_entity.defence,
                "Stamina": pokemon_entity.stamina
            }
        )

    pokemon_card = {
            "pokemon_id": pokemon.id,
            "title_ru": pokemon.title,
            "title_en": pokemon.title_en,
            "title_jp": pokemon.title_jp,
            "description": pokemon.description,
            "img_url": request.build_absolute_uri(pokemon.image.url),
        }

    next_evolutions = pokemon.next_evolutions.all()
    # template doesn't take multiple evolutions
    if next_evolutions:
        pokemon_card["next_evolution"] = {
            "title_ru": next_evolutions[0].title,
            "pokemon_id": next_evolutions[0].id,
            "img_url": request.build_absolute_uri(next_evolutions[0].image.url)
        }

    if pokemon.previous_evolution:
        pokemon_card["previous_evolution"] = {
                "title_ru": pokemon.previous_evolution.title,
                "pokemon_id": pokemon.previous_evolution.id,
                "img_url": request.build_absolute_uri(
                    pokemon.previous_evolution.image.url
                )
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_card
    })
