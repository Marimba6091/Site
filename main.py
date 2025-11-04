import socket
import threading as th
from server.net import Net, show_content


def greet(con, adr, host):
    request = con.recv(1024)
    if request:
        con.send(show_content(request, adr, host))
        con.close()

def start(host):
    while True:
        con = None
        con, adr = server.accept()
        if not con is None:
            th.Thread(target=greet, args=(con, adr, host)).start()

if __name__ == "__main__":
    host = "26.105.156.176"
    port = 80
    server = socket.socket()
    server.bind((host, port))
    server.listen(2)
    Net.activation()
    start((host, port))
