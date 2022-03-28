import socket, time
import threading

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)
ip = "127.0.0.1"
port = 9090
server.bind(
    (ip, port)
)
server.listen(10)
print(f"Сервер {ip}:{port} ждет подключений")

clients = []
nicknames = []


def broadcast(data):
    for user_socket in clients:
        user_socket.send(data)


def handle(user_socket):
    print("ждем сообщений ")

    while True:
        try:
            data = user_socket.recv(2048)

            id = (f"{nicknames[clients.index(user_socket)]} пернул >> {user_socket} :")
            itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
            print(f"[" + itsatime + f"]/ {id}", end="")
            broadcast(data)

        except:
            index = clients.index(user_socket)
            clients.remove(user_socket)
            user_socket.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


def receive():
    while True:
        user_socket, address = server.accept()  # блокирует запуск других функций
        print(f"Пользователь {str(address[1])} подключился")
        #clients.append(user_socket)

        user_socket.send("ИМЯ".encode("utf-8"))
        nickname = user_socket.recv(2048)

        nicknames.append(nickname)
        clients.append(user_socket)

        print(f"Пользователь С никнеймом {str(nickname)}")
        broadcast(f"{nickname} на сервере\n".encode("utf-8"))
        user_socket.send("Добро пожаловать на сервер Шизофрения".encode("utf-8"))

        thread = threading.Thread(
            # вкоючаем многопоточность, и включаем функ listen_user и с аргументом user, используем args что бы использовать аргумент
            target=handle,
            args=(user_socket,)
        )
        thread.start()

receive()