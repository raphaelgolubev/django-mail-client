"""
Скрипт создает файл accounts.json, который будет использован Django для автоматического
добавления в базу данных.
"""
import json
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Sequence


SERVERS = {
    "yandex": ("imap.yandex.ru", 993),
    "mail": ("imap.mail.ru", 993),
    "gmail": ("imap.gmail.com", 993),
}


def get_parser(raw_args: Sequence[str] | None = None):
    parser = ArgumentParser(
        description=__doc__, 
        formatter_class=RawDescriptionHelpFormatter,
        usage='python add_account_cli.py -e [EMAIL] -p [PASSWORD] -is [IMAP_SERVER] -ip [IMAP_PORT]',
        add_help=True,
    )
    parser.add_argument('-e', '--email', required=True, help='Адрес электронной почты')
    parser.add_argument('-p', '--password', required=True, help='Пароль')
    parser.add_argument('-is', '--imap-server', required=False, help='Адрес сервера')
    parser.add_argument('-ip', '--imap-port', required=False, help='Порт сервера')

    return parser.parse_args(args = raw_args)


def write_file(path, data: dict):
    file_data = {}

    if path.exists():
        with open(path, 'r') as file:
            line = file.read()
        file_data = json.loads(line)

    # Применяем strip() ко всем строковым значениям в data
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.strip()

    json_record = json.dumps(data)
    readable = json_record \
        .replace('{', '\n{\n\t') \
        .replace('}', '\n}') \
    
    file_data['accounts'] = file_data.get('accounts', [])
    
    # Проверка на уникальность адреса электронной почты
    for account in file_data['accounts']:
        if account['email'] == data['email']:
            print(f'Обновлен аккаунт {account["email"]}')
            file_data['accounts'].remove(account)

    file_data['accounts'].append(data)  # Добавление нового аккаунта

    with open(path, 'w') as file:
        json.dump(file_data, file, indent=4)  # Запись с отступами для читаемости
    
    print(f"Добавлен аккаунт: {readable}")


def make_record(args: ArgumentParser):
    record = {}

    if args.email:
        record['email'] = args.email
    else:
        raise ValueError('Адрес электронной почты не может быть пустым')

    if args.password:
        record['password'] = args.password
    else:
        raise ValueError('Пароль не может быть пустым')

    if args.imap_server:
        record['imap_server'] = args.imap_server
    else:
        server = args.email.split('@')[1]
        hostname = server.split('.')[0]
        
        if SERVERS.get(hostname):
            imap, port = SERVERS.get(hostname)
            record['imap_server'] = imap
            record['imap_port'] = port
        else:
            record['imap_server'] = f'imap.{server}'
    
    if args.imap_port:
        record['imap_port'] = args.imap_port
    else:
        if not record.get('imap_port'):
            record['imap_port'] = 993

    write_file(Path('accounts.json'), record)


def main(raw_args: Sequence[str] | None = None):
    parser = get_parser(raw_args)
    make_record(parser)


if __name__ == "__main__":
    main()
