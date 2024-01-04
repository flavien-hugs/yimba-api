# yimba-api
> Yimba est une plateforme d'analyse des émotions et opinions en ligne, conçue pour collecter, analyser et surveiller les commentaires provenant de diverses sources, y compris les médias sociaux.

## Prérequis

* [Python3.10](python.org)
* [Poetry](python-poetry.org)
* [Docker](docker.com)
* [Mongo](mongodb.com)
* [Redis](redis.io)

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
