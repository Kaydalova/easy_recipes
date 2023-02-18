# Foodgram - Продуктовый помощник

![foodgram_workflow](https://github.com/kaydalova/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

---

 Приложение, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «cписок покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Есть возможность выгрузить файл (.txt) с перечнем и количеством необходимых ингредиентов для рецептов.

## Доступ

Проект запущен на сервере и доступен по адресу:
- http://130.193.50.29/recipes

- Тестовый пользователь:
torres2@yandex.ru
qazwsx554697

- Админская учетка:
admin@admin.ru
admin

## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Github Actions

## Установка проекта локально

* Склонировать репозиторий на локальную машину:
```bash
git clone git@github.com:Kaydalova/foodgram-project-react.git
cd foodgram-project-react
```

* Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

* Cоздайте файл `.env` в директории `/infra/` с содержанием:

```
SECRET_KEY=секретный ключ django
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* Перейти в директирию и установить зависимости из файла requirements.txt:

```bash
cd foodgram/
pip install -r requirements.txt
```

* Выполните миграции:

```bash
python manage.py migrate
```
* Загрузите ингредиенты:
```bash
python manage.py import_csv

```
* Запустите сервер:
```bash
python manage.py runserver
```

## Запуск проекта в Docker контейнере
* Установите Docker и docker compose плагин.

Параметры запуска описаны в файлах `docker-compose.yml` и `nginx.conf` которые находятся в директории `infra/`.  
Измените список ip адресов в файле `nginx.conf`

* Запустите docker compose:
```bash
docker compose up -d --build
```  
  > После сборки появляются 3 контейнера:
  > 1. контейнер базы данных **db**
  > 2. контейнер приложения **backend**
  > 3. контейнер web-сервера **nginx**
* Примените миграции:
```bash
docker compose exec backend python manage.py migrate
```
* Загрузите ингредиенты:
```bash
docker сompose exec backend python manage.py import_csv
```

```
* Создайте администратора:
```bash
docker compose exec backend python manage.py createsuperuser
```
* Соберите статику:
```bash
docker compose exec backend python manage.py collectstatic --noinput
```
