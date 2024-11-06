"""
Добавляет аккаунты электронной почты в интерактивном режиме.
"""
from core.utils import add_account_cli as cli


def multiline_input(prompt: str, break_on: str = None):
    """
    Многострочный ввод от пользователя.

    Usage:
        ```
        lines = multiline_input("Введите имена игроков построчно: ", break_on = 'q!')
        # > Введите имена игроков построчно:
        # Иван
        # Петр
        # Сергей
        # q!
        print(lines)
        # ['Иван', 'Петр', 'Сергей']
        ```

    Parameters:
        - prompt (str): текст запроса. Например: "Введите имена игроков построчно:".
        - break_on (str): символ или слово, определяющее конец ввода.

    Returns:
        - str: введенная строка.
    """
    lineno = 0
    max_prefix_spacing = 4
    space = ' '

    def get_prefix():
        # 1.    | count 1, 4 - 1 = 3
        # 10.   | count 2, 4 - 2 = 2
        # 100.  | count 3, 4 - 3 = 1
        # 1000. | count 4, 4 - 4 = 0
        count = len(str(lineno))
        multiplier = (max_prefix_spacing - count) + 1
        spacing = f"{space * multiplier}"

        return f"{lineno}.{spacing}|  "


    if not break_on:
        break_on = ''

    print(prompt)

    while True:
        lineno += 1
        prefix = get_prefix()

        line = input(prefix)
        
        if line == break_on:
            break
        yield line.strip()


def main():
    print("> Добавьте аккаунты электронной почты построчно")
    print('в формате "email, password, imap_server (необязательно), imap_port (необязательно)"')
    print("Например: my_mail@gmail.com, 123456, imap.gmail.com, 993")
    lines = multiline_input('Нажмите Enter для выхода...', break_on = None)

    for line in lines:
        components = line.split(',')
        components = list(map(lambda x: x.strip(), components))

        email = components[0] if len(components) > 0 else None
        password = components[1] if len(components) > 1 else None
        imap_server = components[2] if len(components) > 2 else None
        imap_port = components[3] if len(components) > 3 else None
        
        cmds = []
        if email: cmds.append(f'-e {email}')
        if password: cmds.append(f'-p {password}')
        if imap_server: cmds.append(f'-is {imap_server}')
        if imap_port: cmds.append(f'-ip {imap_port}')

        if len(cmds) > 0:
            try:
                cli.main(raw_args=cmds)
            except Exception as e:
                print(f"Ошибка добавления аккаунта: {e}")
        else:
            print("Не удалось добавить аккаунт")


if __name__ == '__main__':
    main()
