# ВК-бот

### Это мой проект ВК-бота, рассылающего расписание университета

### Пример использования

![](https://github.com/VerS7/python-rasp-bot/blob/main/example.png)

### Build

Сборка Docker-образа
`docker build -t python-rasp-bot .`

Запуск Docker-контейнера
`docker run --name <name> --env-file <.env file> --restart=always -v ./files:/app/files -d python-rasp-bot`
