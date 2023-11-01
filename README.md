# Foodgram
Этот сервис предоставляет возможность пользователям публиковать рецепты и включает в себя следующие функции:

Главная страница: отображает основное содержание сервиса.
Страницы рецептов: позволяют просматривать отдельные рецепты.
Пользователи: предоставляют информацию о пользователях.
Подписки: пользователи могут подписываться на других пользователей.
Избранное: пользователи могут сохранять рецепты в избранное.
Список покупок: доступ к списку покупок, который включает в себя все рецепты, добавленные в этот список. Пользователь может скачать файл с перечнем ингредиентов и их количеством для всех рецептов, сохраненных в этом списке.
Создание и редактирование рецептов: пользователи могут добавлять новые рецепты и редактировать существующие.


Адрес сервера: http://158.160.8.128/  
Почта для входа в админ-панель: admin@gmail.com  
Пароль: admin

## Автор
[Королев Радислав](https://github.com/PIEJIN)

## Установка
1. Склонируйте репозиторий.
```
git clone git@github.com:piejin/foodgram-project-react.git
```
<br>

2. Находясь в директории infra/.
```
docker compose up
```
<br>

3. Примените миграции и настройте статику, создайте superuser.
```
docker compose -f docker-compose.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```
<br>

<br>

4. Заполните базу данных ингредиентами.
```
docker compose -f docker-compose.yml exec backend python manage.py create_ingredients
```
<br>

5. Создайте .env  в корне проекта. Пример:
```
SECRET_KEY ='django-insecure-qwertyuio12345678'
DEBUG_MODE = False

POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django

DB_HOST=db
DB_PORT=5432

ALLOWED_HOSTS=localhost, 158.160.8.128, 127.0.0.1
```
<br>


## Примеры Запросов
Регистрация пользователя
```
POST http://localhost/api/users/

{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```

Создание рецепта
```
POST http://localhost/api/recipes/

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
