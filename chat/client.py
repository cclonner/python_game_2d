import socket
from threading import Thread
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

IP = "127.0.0.1"
PORT = 9090


class Client:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.sock.connect((ip, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("ИМЯ", "впешите имя", parent=msg)
        self.gui_done = False
        self.running = True

        gui_threat = Thread(target=self.gui_loop)
        receive_threat = Thread(target=self.receive())
        gui_threat.start()
        receive_threat.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="ЧЯТ:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.configure(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="ВЫСЕР:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="ПУКНУТЬ", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.win.mainloop()
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"  # имя и сообщение с начала и до конца
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(2048).decode("utf-8")
                if message == "ИМЯ":
                    self.sock.send(self.nickname.encode("utf-8"))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state="disabled")
            except ConnectionAbortedError:
                break

            except:
                print("Ошибка")
                self.sock.close()
                break


client = Client(IP, PORT)
