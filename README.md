# StarWars GraphQL (Django + Graphene)

Backend mínimo para prueba técnica con **Django + GraphQL (Graphene-Django v3, Relay)**.  

## Funcionalidades
- Listar **personajes** con **filtro por nombre**.
- Consultar sus **películas** (title, opening crawl, director, producers) y **planetas**.
- **Mutations** para crear planetas, películas y personajes.
- **Pruebas** unitarias y de integración.
- (Opcional) Cargar datos reales desde la API externa **SWAPI** con un *management command*.

## Requisitos
- Python 3.11 o 3.12 (probado en 3.12)  
- pip / venv  
- SQLite (incluida por defecto)  

> Zona horaria configurada: `America/Bogota`.

## Estructura del proyecto
```
.
├─ config/                # Proyecto Django
├─ sw/                    # App principal (models, schema, tests, fixtures, management command)
│  ├─ management/commands/load_swapi.py
│  ├─ fixtures/sw_fixture.json
│  ├─ models.py
│  ├─ schema.py
│  └─ tests.py
├─ db.sqlite3
├─ manage.py
├─ requirements.txt
└─ README.md
```

## Instalación y ejecución

### 1) Crear y activar entorno virtual
```
python -m venv .venv
.venv\Scripts\activate   # en Windows PowerShell
# source .venv/bin/activate   # en Linux/Mac
```

### 2) Instalar dependencias
```
pip install -r requirements.txt
```

### 3) Migraciones
```
python manage.py makemigrations
python manage.py migrate
```

### 4) Cargar datos
- **Opción A (rápida, fixture local):**
```
python manage.py loaddata sw_fixture.json
```

- **Opción B (API externa SWAPI):**
```
# Mirror recomendado si hay inspección SSL en la red
python manage.py load_swapi --base https://swapi.py4e.com/api --limit-people 20

# Todo el catálogo (puede tardar)
python manage.py load_swapi --base https://swapi.py4e.com/api

# En caso de problemas SSL (solo en desarrollo)
python manage.py load_swapi --base https://swapi.py4e.com/api --insecure
```

### 5) Levantar servidor
```
python manage.py runserver
```

GraphiQL disponible en:  
http://localhost:8000/graphql

## Queries de ejemplo

### 1) Listar personajes filtrando por nombre
```
query {
  allCharacters(name_Icontains: "luke") {
    edges {
      node {
        id
        name
      }
    }
  }
}
```

### 2) Ver detalle completo (películas + planetas + metadatos)
```
query {
  allCharacters(name_Icontains: "luke") {
    edges {
      node {
        name
        films {
          edges {
            node {
              title
              openingCrawl
              director
              producers
              planets { edges { node { name } } }
            }
          }
        }
      }
    }
  }
}
```

### 3) Filtrar películas por director
```
query {
  allFilms(director_Icontains: "george") {
    edges {
      node {
        id
        title
        director
      }
    }
  }
}
```

> Si habilitaste el resolver opcional `producersList`, también puedes consultar:
```
query {
  allFilms {
    edges {
      node {
        title
        producersList
      }
    }
  }
}
```

## Mutations de ejemplo

### Crear planeta
```
mutation {
  createPlanet(input: { name: "Hoth" }) {
    planet { id name }
  }
}
```

### Crear película
```
mutation {
  createFilm(input: {
    title: "Return of the Jedi",
    openingCrawl: "Luke Skywalker has returned to his home planet...",
    director: "Richard Marquand",
    producers: ["Howard G. Kazanjian", "George Lucas", "Rick McCallum"]
  }) {
    film { id title director producers }
  }
}
```

### Crear personaje
```
mutation {
  createCharacter(input: { name: "Chewbacca" }) {
    character { id name }
  }
}
```

## Pruebas
Ejecutar:
```
python manage.py test
```

Incluye:
- Filtrado de `allCharacters` por nombre.
- Mutación `createPlanet`.

## Problemas comunes

**Error:** `Application labels aren't unique, duplicates: admin`  
- Quita duplicados de `INSTALLED_APPS` en `settings.py`.

**Error:** `no such table: sw_planet`  
- Ejecuta migraciones (`makemigrations sw` y `migrate`) desde la carpeta donde está `manage.py`.

**Error SSL al cargar SWAPI**  
- Actualiza certificados:
```
pip install -U pip requests urllib3 certifi
```
- Usa el mirror: `--base https://swapi.py4e.com/api`  
- Como último recurso: `--insecure` (solo en desarrollo).

## Notas técnicas
- GraphQL implementado con **Relay** (`Node`, `Connections`, `DjangoFilterConnectionField`).  
- Filtros soportados: `name_Icontains`, `title_Icontains`, `director_Icontains`, etc.  
- `producers` se guarda como string separado por comas.  
  Se puede exponer como lista usando un resolver adicional (`producersList`).  
