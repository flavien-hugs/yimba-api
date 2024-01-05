# yimba-api
> Yimba est une plateforme d'analyse des émotions et opinions en ligne, conçue pour collecter, analyser et surveiller les commentaires provenant de diverses sources, y compris les médias sociaux.

## Prérequis

* [Python3.10](https://python.org)
* [Poetry](https://python-poetry.org)
* [Docker](https://docker.com)
* [Mongo](https://mongodb.com)
* [Redis](https://redis.io)

## Utilisation

- Cloner le dépôt
```shell
git clone https://github.com/flavien-hugs/yimba-api.git
```
- Éxecuter le projet
```shell
cd yimba-api
make run
```

## Exécution des tests

- Exécuter le test de couverture
```shell
poetry run coverage run -m pytest -v tests
```

- Vérifier la couverture de test du code
```shell
poetry run coverage report -m
```
## Docs utiles
```shell
[postman docs](https://www.postman.com/twitter/workspace/twitter-s-public-workspace/collection/9956214-784efcda-ed4c-4491-a4c0-a26470a67400?ctx=documentation)
```
