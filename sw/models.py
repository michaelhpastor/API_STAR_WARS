from django.db import models

class Planet(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Film(models.Model):
    title = models.CharField(max_length=200)
    opening_crawl = models.TextField()
    director = models.CharField(max_length=100)
    # Guardamos productores como string (simple y suficiente para la prueba)
    producers = models.CharField(max_length=500, help_text="Nombres separados por coma")
    release_date = models.DateField(null=True, blank=True)

    planets = models.ManyToManyField(Planet, related_name="films", blank=True)

    def __str__(self):
        return self.title

class Character(models.Model):
    name = models.CharField(max_length=120)
    films = models.ManyToManyField(Film, related_name="characters", blank=True)

    def __str__(self):
        return self.name
