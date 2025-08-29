import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from .models import Character, Film, Planet

# NODES
class PlanetNode(DjangoObjectType):
    class Meta:
        model = Planet
        interfaces = (relay.Node,)
        fields = ("id", "name", "films")
        filter_fields = {"name": ["exact", "icontains", "istartswith"]}

class FilmNode(DjangoObjectType):
    class Meta:
        model = Film
        interfaces = (relay.Node,)
        fields = ("id","title","opening_crawl","director",
                  "producers","release_date","planets","characters")
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
            "director": ["exact", "icontains"],
            "producers": ["icontains"],
            "release_date": ["exact", "lt", "gt"],
            "planets__name": ["icontains"],
        }

class CharacterNode(DjangoObjectType):
    class Meta:
        model = Character
        interfaces = (relay.Node,)
        fields = ("id", "name", "films")
        filter_fields = {"name": ["exact", "icontains", "istartswith"]}

# QUERIES
class Query(graphene.ObjectType):
    node = relay.Node.Field()
    character = relay.Node.Field(CharacterNode)
    film = relay.Node.Field(FilmNode)
    planet = relay.Node.Field(PlanetNode)

    all_characters = DjangoFilterConnectionField(CharacterNode)
    all_films = DjangoFilterConnectionField(FilmNode)
    all_planets = DjangoFilterConnectionField(PlanetNode)

# MUTATIONS
class CreatePlanet(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    planet = graphene.Field(PlanetNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        planet = Planet.objects.create(name=input["name"])
        return CreatePlanet(planet=planet)

class CreateFilm(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        opening_crawl = graphene.String(required=True)
        director = graphene.String(required=True)
        producers = graphene.List(graphene.String, required=True)
        release_date = graphene.types.datetime.Date(required=False)
        planet_ids = graphene.List(graphene.ID, required=False)

    film = graphene.Field(FilmNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        producers_str = ",".join(input["producers"])
        film = Film.objects.create(
            title=input["title"],
            opening_crawl=input["opening_crawl"],
            director=input["director"],
            producers=producers_str,
            release_date=input.get("release_date"),
        )
        for gid in input.get("planet_ids") or []:
            _, pk = from_global_id(gid)
            film.planets.add(Planet.objects.get(pk=pk))
        return CreateFilm(film=film)

class CreateCharacter(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        film_ids = graphene.List(graphene.ID, required=False)

    character = graphene.Field(CharacterNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        ch = Character.objects.create(name=input["name"])
        for gid in input.get("film_ids") or []:
            _, pk = from_global_id(gid)
            ch.films.add(Film.objects.get(pk=pk))
        return CreateCharacter(character=ch)

class Mutation(graphene.ObjectType):
    create_planet = CreatePlanet.Field()
    create_film = CreateFilm.Field()
    create_character = CreateCharacter.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
