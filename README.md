


![workflow](https://github.com/Turianpy/password_manager/actions/workflows/main.yml/badge.svg)

  

# Описание проекта

  

Простой менеджер паролей с jwt аутентификацией и зашифровкой/расшифровкой паролей на сервере.

  

Пользователи должны создать учетную запись и подтвердить электронную почту, после чего им доступны эндпоинты для создания, имзенения и получения своих паролей

## Эндпоинты:

Регистрация:

`/api/auth/signup/`

POST:
```json
{
	"username": "myusername",
	"email": "something@something.com",
	"password": "example123"
}
```

После успешного POST запроса на этот эндпоинт, на указанную почту придет письмо со ссылкой для активации учетной записи. Письмо отобразится в папке sent_emails на том же уровне проекта, где находится manage.py

Ссылка будет выглядеть так:
`http://localhost/api/auth/activate/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdC50ZXN0IiwiZXhwIjoxNjk5OTcxODQ0fQ.HwTW-t5a6i6Jo3POSE0gWPv1mpRQ8HPmVuFppi0Dp2I`

В ответ на GET запрос после перехода по валидной ссылке, пользователь получит ответ:
```json
{
	"message": "Account successfully activated"
}
```


Получение токена:

`/api/auth/token/`

POST:

```json
{
	"username": "myusername",
	"password": "example123"
}
```

Ответ:

```json
{
    "refresh": "str",
    "access": "str"
}
```

После добавления access токена в Bearer header,  пользователь может обратиться к эндпоинтам ниже


Создание и получение пары пароль-сервис:

`/api/password/{service_name}` 

В json POST-запроса необходимо указать только одно поле, сам пароль. Пример запроса:
```json
{
	"password": "strongpass123"
}
```
GET запрос вернет пару пароль-сервис в формате json
```json
{
	"service_name": "someserivce",
	"password": "yourpass"
}
```

Получение паролей по части имени сервиса:

`/api/password/?service_name={part_of_service_name}`

Поиск происходит по icontains. Если параметр запроса пуст, пользователь получит список всех своих паролей в таком же формате, что ответ на GET запрос выше.


## Запуск проекта c docker

В папке infra необходимо создать файл `.env`

Пример .env
```env
DB_ENGINE = 'django.db.backends.postgresql'
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_URL = 'redis://redis:6379/0'

SECRET_KEY = 'plPLehaqF_otSzLzh33J55D7-bJkDLoVkpmFrzAqT_igos-En6UtBLIshkYqF'
```

Из директории infra запустить:

`docker compose up`

После чего можно проверить доступ к эндпоинтам, описанным выше, с помощью любого инструмента для тестирования API. Например Postman.

Так же можно перейти в шелл контейнера

`docker exec -it pm_api //bin/sh`

и запустить тесты

`pytest`


