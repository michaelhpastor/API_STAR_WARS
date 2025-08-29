from django.contrib import admin
from .models import Planet, Film, Character

@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "director", "release_date")
    search_fields = ("title", "director", "producers")
    filter_horizontal = ("planets",)

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    filter_horizontal = ("films",)
