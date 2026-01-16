import socket
import threading as th
from server.net import show_content
from server.net import Net


def greet(con, adr, host):
    request = con.recv(2_147_483_648)
    if request:
        con.send(show_content(request, adr, host))
        con.close()

def start(host):
    print("Start")
    while True:
        con = None
        con, adr = server.accept()
        if not con is None:
            th.Thread(target=greet, args=(con, adr, host)).start()

if __name__ == "__main__":
    host = socket.gethostname()
    print(host)
    port = 80
    server = socket.socket()
    server.bind((host, port))
    server.listen(2)
    Net.activation()
    start((host, port))
