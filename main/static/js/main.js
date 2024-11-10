// Обработчик для кнопки "Показать/Скрыть"
function toggleEmails(accountId) {
    var emails = document.getElementById('emails-' + accountId);
    if (emails.style.display === 'none') {
        emails.style.display = 'table-row-group';
    } else {
        emails.style.display = 'none';
    }
}

// Обработчик для поля email выполняющий подстановку в поле imap_server при вводе почты
document.getElementById('email').addEventListener('input', function() {
    const email = this.value;
    const domain = email.split('@')[1]; // Получаем домен после '@'
    
    if (domain) {
        // Устанавливаем значение поля imap_server
        document.getElementById('imap_server').value = `imap.${domain}`;
    } else {
        // Если домен не указан, очищаем поле imap_server
        document.getElementById('imap_server').value = '';
    }
});

// Обработчик для формы добавления аккаунта
$('#add-account-form').on('submit', function(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    $.ajax({
        type: 'POST',
        url: 'add_account/',
        data: $(this).serialize(), // Сериализуем данные формы
        success: function(response) {
            // Обработка успешного ответа
            console.log('Аккаунт добавлен:', response);
            
            // Добавляем новый аккаунт в список
            if (response.status === 'success') {
                const account = response.account;
                $('#account-list').append(`
                    <div class="item d-flex justify-content-start align-content-stretch flex-wrap">
                        <div class="d-flex align-items-center">
                            <div id="progress-container-${account.id}" class="progress progress-circular" style="--percentage: 0">
                                <div class="progress-bar"></div>
                                <div id="plabel-${account.id}" ,="" class="progress-label">0%</div>
                            </div>
                        </div>
                    
                        <div class="d-flex justify-content-center align-items-center flex-grow-1">
                            <span class="badge badge-primary my-badge">
                                ${account.email} (ID: ${account.id}, IMAP: ${account.imap_server}, Порт: ${account.imap_port})
                            </span>

                            <span id="progress-message-${account.id}" class="badge badge-success my-badge">
                                0 из 0
                            </span>
                        </div>
                
                        <button data-id="${account.id}" class="btn btn-danger btn-sm float-right delete-account-button">
                            <i class="fas fa-trash"></i> Удалить
                        </button>
                    </div>
                `);
                
                // Закрываем модальное окно
                $('#addAccountModal').modal('hide');

                // Перезагружаем страницу
                // window.location.reload();
            }
        },
        error: function() {
            console.log('Произошла ошибка при добавлении аккаунта.');
            alert('Произошла ошибка при добавлении аккаунта.');

            // Закрываем модальное окно
            $('#addAccountModal').modal('hide');
        }
    });
});