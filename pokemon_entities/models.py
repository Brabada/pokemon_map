from django.db import models  # noqa F401


# your models here

class PokemonElementType(models.Model):
    title = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.title


class Pokemon(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    title_en = models.CharField(max_length=200,
                                blank=True,
                                verbose_name="Название(англ.)")
    title_jp = models.CharField(max_length=200,
                                blank=True,
                                verbose_name="Название(японск.)")
    image = models.ImageField(null=True,
                              verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    previous_evolution = models.ForeignKey("self",
                                           null=True,
                                           blank=True,
                                           on_delete=models.SET_NULL,
                                           related_name='next_evolutions',
                                           verbose_name="Предыдущая эволюция")
    element_type = models.ManyToManyField(PokemonElementType,
                                          blank=True,
                                          related_name="pokemons",
                                          verbose_name="Element type")

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon,
                                on_delete=models.CASCADE,
                                related_name='entities',
                                verbose_name="Покемон")
    lat = models.FloatField(verbose_name="Широта")
    lon = models.FloatField(verbose_name="Долгота")
    appeared_at = models.DateTimeField(verbose_name="Дата и время появления")
    disappeared_at = models.DateTimeField(verbose_name="Дата и время "
                                                       "исчезновения")
    level = models.IntegerField(null=True,
                                blank=True,
                                verbose_name="Уровень")
    health = models.IntegerField(null=True,
                                 blank=True,
                                 verbose_name="Здоровье")
    strength = models.IntegerField(null=True,
                                   blank=True,
                                   verbose_name="Сила")
    defence = models.IntegerField(null=True,
                                  blank=True,
                                  verbose_name="Защита")
    stamina = models.IntegerField(null=True,
                                  blank=True,
                                  verbose_name="Выносливость")

    def __str__(self):
        return f"{self.pokemon.title} {self.lat} {self.lon}"

