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
 * @param {Object} param - параметры действия
 */
function sendAction(webSocket, name, param = {}) {
    const action = JSON.stringify({action: name, ...param}); // Объединяем объект с параметрами
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

// /**
//  * Извлекает идентификатор письма из строки вида "10.1", где
//  * 10 - идентификатор аккаунта в БД, 1 - идентификатор письма
//  */
// function extractMessageId(message) {
//     id = message.email.message_id.split('.')[1];
//     result = (message.total + 1) - id;

//     return result;
// }

/**
 * Добавляет строку в таблицу
 * 
 * @param {string} selector - селектор таблицы
 * @param {string} message - сообщение
 */
function addEmailRow(selector, message) {
    // Идентификатор письма
    let email_id = message.email.message_id;
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
 * Обновляет прогресс бар
 * @param {Object} message - сообщение
 * 
 */
function updateProgressBar(message) {
    // Прогресс бар
    let progressBar = $('.progress-bar');
    // Сообщение о прогрессе
    let progress_message = $('#progress-message');
    // Идентификатор письма в БД
    let db_message_id = (message.total - message.email.message_id) + 1;

    if (message.percent) {
        const percentValue = parseFloat(message.percent); // Преобразуем строку в число
        const progressValue = 100 - percentValue; // Вычисляем значение для progressBar

        // Устанавливаем значение для progressBar
        progressBar.css('width', progressValue + '%').attr('aria-valuenow', progressValue);
        // Устанавливаем значение для <span>
        progress_message.text(db_message_id + ' из ' + (message.total + 1));
    }
}

function setDone(message) {
    let progressBar = $('.progress-bar');
    let progress_message = $('#progress-message');
    let total = message.total + 1;

    progressBar.css('width', '100%').attr('aria-valuenow', 100);
    progress_message.text(total + ' из ' + total);
}

/**
 * Загружает сообщение в таблицу
 * @param {Object} message - сообщение
 * 
*/
function loadMessage(message) {
    // Идентификатор аккаунта электронной почты в БД
    let account_id = message.email.email_account
    // тело таблицы
    let emailsContainer = $('#emails-' + account_id);
    // Добавляем письмо в таблицу
    addEmailRow(emailsContainer, message);
    // Обновляем прогресс бар
    updateProgressBar(message);
}

/**
 * Устанавливает статус прогресс бара
 * @param {Object} message - сообщение
 * 
*/
function setStatus(message) {
    let status = $('#progress-status');
    status.text(message.human_status);
}

const socket = createWebSocket('localhost', 8000, 'ws/emails/');


// Соединение с сервером установлено
socket.onopen = function(event) {
    const url = window.location.href; // Получаем текущий URL
    const lastSegment = url.split('/').pop(); // Разделяем по '/' и берем последний элемент

    console.log('Соединение установлено:', event);
    sendAction(socket, 'start_imap_read', {"account_id": lastSegment});
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
        setDone(message);
    }

    setStatus(message);
};

// Соединение закрыто
socket.onclose = function(event) {
    console.log('Соединение закрыто:', event);
};

// Ошибка соединения
socket.onerror = function(error) {
    console.error('Ошибка WebSocket:', error);
};