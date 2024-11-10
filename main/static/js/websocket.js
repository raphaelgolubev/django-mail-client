/**
 * Создает вебсокет соединение
 * 
 * @param {string} host - адрес хоста
 * @param {number} port - порт
 * @param {string} route - путь
 * 
 * @returns {WebSocket} объект вебсокета
 */
function createWebSocket(host, port, route) {
    return new WebSocket(`ws://${host}:${port}/${route}`);
}

/**
 * Отправляет сообщение вебсокету
 * 
 * @param {WebSocket} webSocket - объект вебсокета
 * @param {string} name - имя действия
 */
function sendAction(webSocket, name) {
    action = JSON.stringify({action: name})
    webSocket.send(action);

    console.log('Отправлено:', action);
}

/**
 * Парсит сообщение вебсокета
 * 
 * @param {MessageEvent} event - событие вебсокета
 * @returns {Object} JSON объект
 */
function parseMessage(event) {
    return JSON.parse(event.data);
}

/**
 * Извлекает идентификатор письма из строки вида "10.1", где
 * 10 - идентификатор аккаунта в БД, 1 - идентификатор письма
 */
function extractMessageId(message) {
    id = message.email.message_id.split('.')[1];
    result = (message.total + 1) - id;

    return result;
}

/**
 * Добавляет строку в таблицу
 * 
 * @param {string} selector - селектор таблицы
 * @param {string} message - сообщение
 */
function addEmailRow(selector, message) {
    // Идентификатор письма
    let email_id = message.email.id; //extractMessageId(message);
    // Тема письма
    let subject = message.email.subject;
    // Содержание письма
    let content = message.email.content;
    // Список вложений
    let attachments = message.email.attachments;
    // Дата отправки письма
    let date_sent = message.email.date_sent;
    // Дата получения письма
    let date_received = message.email.date_received;
    selector.append(`
        <tr>
            <td>${email_id}</td>
            <td>${subject}</td>
            <td>${content}</td>
            <td>${attachments}</td>
            <td>${date_sent}</td>
            <td>${date_received}</td>
        </tr>
    `);
}

/**
 * Проверяет, существует ли элемент в DOM
 * 
 * @param {string} selector - селектор
 * @returns {boolean} true, если существует
 */
function isElementExists(selector) {
    return selector.length > 0;
}

/**
 * Обновляет прогресс бар
 * @param {Object} message - сообщение
 * @param {number} account_id - идентификатор аккаунта
 * 
 */
function updateProgressBar(message, account_id) {
    // Контейнер
    let accountProgressBarContainer = $('#progress-container-' + account_id);
    // Label
    let label = $('#plabel-' + account_id);
    let progress_message = $('#progress-message-' + account_id);
    // Идентификатор письма в БД
    let db_message_id = extractMessageId(message)

    if (message.percent) {
        const percentValue = parseFloat(message.percent); // Преобразуем строку в число
        const progressValue = 100 - percentValue; // Вычисляем значение для progressBar

        accountProgressBarContainer.css('--percentage', progressValue); // Устанавливаем значение для progressBar
        // Устанавливаем значение для progressBar
        // accountProgressBar.css('width', progressValue + '%').attr('aria-valuenow', progressValue); 
        label.text(Math.ceil(progressValue) + '%');
        // Устанавливаем значение для <p>
        progress_message.text(db_message_id + ' из ' + (message.total + 1));
    }
}

function set_done(message, account_id) {
    let accountProgressBarContainer = $('#progress-container-' + account_id);
    let label = $('#plabel-' + account_id);
    let progress_message = $('#progress-message-' + account_id);

    accountProgressBarContainer.css('--percentage', message.percent);
    label.text('100%');
    progress_message.text(message.total + ' из ' + message.total);
}

/**
 * Скрывает контейнер с прогресс барами
 */
function hideProgressBar() {
    $('#progress-bar').hide();
}

function loadMessage(message) {
    // Идентификатор аккаунта электронной почты в БД
    let account_id = message.email.email_account
    // тело таблицы
    let emailsContainer = $('#emails-' + account_id);
    // Добавляем письмо в таблицу
    addEmailRow(emailsContainer, message);
    // Обновляем прогресс бар
    updateProgressBar(message, account_id);
}


const socket = createWebSocket('localhost', 8000, 'ws/emails/');


// Соединение с сервером установлено
socket.onopen = function(event) {
    console.log('Соединение установлено:', event);
    sendAction(socket, 'start_imap_read');
};

// Получил сообщение от сервера
socket.onmessage = function(event) {
    console.log('Получено сообщение', event);
    const message = parseMessage(event);
    
    if (message.status === 'load') {
        console.log('JSON сообщение', message);
        loadMessage(message);
    } else if (message.status === 'done') {
        console.log('Все письма получены', message);
        set_done(message, message.account_id);
    }
};

// Соединение закрыто
socket.onclose = function(event) {
    console.log('Соединение закрыто:', event);
    hideProgressBar();
};

// Ошибка соединения
socket.onerror = function(error) {
    console.error('Ошибка WebSocket:', error);
    hideProgressBar();
};