import os
import time
import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sw.models import Planet, Film, Character

DEFAULT_SWAPI_BASE = os.environ.get("SWAPI_BASE", "https://swapi.dev/api")

def fetch_all(endpoint, base, verify=True, retries=3, backoff=1.5, timeout=20):
    url = f"{base.rstrip('/')}/{endpoint.strip('/')}/"
    results = []
    for attempt in range(1, retries + 1):
        try:
            while url:
                resp = requests.get(url, timeout=timeout, verify=verify)
                resp.raise_for_status()
                data = resp.json()
                results.extend(data.get("results", []))
                url = data.get("next")
            return results
        except requests.exceptions.SSLError as e:
            if attempt == retries:
                raise
            time.sleep(backoff ** attempt)
        except requests.RequestException as e:
            if attempt == retries:
                raise
            time.sleep(backoff ** attempt)
    return results

class Command(BaseCommand):
    help = "Carga datos de SWAPI (planets, films, people) en la base local."

    def add_arguments(self, parser):
        parser.add_argument("--limit-people", type=int, default=None)
        parser.add_argument("--base", type=str, default=DEFAULT_SWAPI_BASE,
                            help="Base URL de SWAPI (por defecto https://swapi.dev/api)")
        parser.add_argument("--insecure", action="store_true",
                            help="Desactiva verificación SSL (solo si tu red lo exige).")

    @transaction.atomic
    def handle(self, *args, **opts):
        base = opts["base"]
        verify = not opts["insecure"]
        limit_people = opts["limit_people"]

        self.stdout.write(self.style.NOTICE(f"Usando SWAPI base: {base} (verify SSL={verify})"))

        try:
            planets_data = fetch_all("planets", base, verify=verify)
            films_data = fetch_all("films", base, verify=verify)
            people_data = fetch_all("people", base, verify=verify)
        except requests.exceptions.SSLError as e:
            raise CommandError(f"Error SSL con {base}. Prueba un mirror con --base o usa --insecure.\n{e}")
        except requests.RequestException as e:
            raise CommandError(f"Fallo HTTP con {base}: {e}")

        if limit_people:
            people_data = people_data[:limit_people]

        # Mapear y upsert
        url_to_planet = {}
        for p in planets_data:
            name = (p.get("name") or "Unknown").strip()
            planet_obj, _ = Planet.objects.get_or_create(name=name)
            url_to_planet[p.get("url")] = planet_obj

        url_to_film = {}
        for f in films_data:
            title = (f.get("title") or "Untitled").strip()
            opening_crawl = f.get("opening_crawl") or ""
            director = f.get("director") or ""
            producers = f.get("producer") or ""  # SWAPI usa "producer"
            release_date = f.get("release_date") or None

            film_obj, _ = Film.objects.get_or_create(
                title=title,
                defaults={
                    "opening_crawl": opening_crawl,
                    "director": director,
                    "producers": producers,
                    "release_date": release_date,
                }
            )
            film_obj.opening_crawl = opening_crawl
            film_obj.director = director
            film_obj.producers = producers
            film_obj.release_date = release_date
            film_obj.save()

            film_obj.planets.clear()
            for planet_url in f.get("planets") or []:
                pl = url_to_planet.get(planet_url)
                if pl:
                    film_obj.planets.add(pl)

            url_to_film[f.get("url")] = film_obj

        for c in people_data:
            name = (c.get("name") or "Unknown").strip()
            ch_obj, _ = Character.objects.get_or_create(name=name)
            ch_obj.films.clear()
            for film_url in c.get("films") or []:
                fo = url_to_film.get(film_url)
                if fo:
                    ch_obj.films.add(fo)

        self.stdout.write(self.style.SUCCESS("Carga completa desde SWAPI."))
