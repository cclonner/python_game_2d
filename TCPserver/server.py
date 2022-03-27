import socket, time
import threading

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)
ip = str("192.168.12.10")
port = int(6666)
server.bind(
    (ip, port)
)
server.listen(10)
print(f"Сервер {ip}:{port} ждет подключений")

users = []


def send_all(data, user):
    for addr in users:
        if addr == user:
            continue
        addr.send(data)


def listen_user(user, address):
    print("ждем сообщений ")

    while True:
        data = user.recv(2048)
        """if not data:
            continue"""
        id = str(f'{address[1]}:').encode("utf-8")
        data = id + data
        itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
        print(f"[" + itsatime + f"]/ {data}", end="")
        send_all(data, user)


def start_server():
    while True:
        user_socket, address = server.accept()  # блокирует запуск других функций

        print(f"Пользователь {address[1]} подключился")
        users.append(user_socket)
        # addrs.append(address)
        listen_accepted_user = threading.Thread(
            # вкоючаем многопоточность, и включаем функ listen_user и с аргументом user, используем args что бы использовать аргумент
            target=listen_user,
            args=(user_socket, address,)
        )

        listen_accepted_user.start()


if __name__ == "__main__":
    start_server()
