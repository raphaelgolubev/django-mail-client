# Django mail client

Почтовый клиент, способный агрегировать письма из нескольких источников.

# Запуск

`docker-compose up --build --remove-orphans`

# Использование

1. Нажмите на зеленую кнопку "Добавить аккаунт"
2. Введите адрес электронной почты
3. Введите пароль от электронной почты или пароль приложения (https://support.google.com/mail/answer/185833?hl=en)
4. IMAP-сервер и порт будут выбран автоматически. Вы можете ввести свои значения, если понадобится.
5. Перезагрузите страницу

После перезагрузки страницы будет создано веб-сокет соединение с сервером. Сервер начнет отправлять письма в браузер.
