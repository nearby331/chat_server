import socket
from threading import Thread
import configparser

config = configparser.ConfigParser()
config.read("server.ini")

conf = config["Main"]

SERVER_HOST = str(conf["host"])
SERVER_PORT = int(conf["port"])
separator_token = conf["separator"]
server_token = conf["token"]

client_sockets = set()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs, addr):
    while True:
        try:
            msg = cs.recv(1024).decode()
        except Exception as e:
            print(f"[-] Disconnected {addr}")
            client_sockets.remove(cs)
        else:
            msg = msg.replace(separator_token, ": ")
        for client_socket in client_sockets:
            client_socket.send(msg.encode())

def wait_for_token(cs, addr):
    while True:
        try:
            msg = cs.recv(1024).decode()
        except Exception as e:
            print(f"[-] Disconnected {addr}")
        else:
            try:
                token = msg.split(separator_token)[1]
                if token == server_token:
                    return True
                else:
                    return False
            except:
                return False

while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected, receiving a token...")
    tt = wait_for_token(client_socket, client_address)
    if tt == True:
        print(f"[*] [{client_address}] Token correct, connecting...")
    else:
        print(f"[*] [{client_address}] Incorrect token!")
        client_socket.close()
        continue
    client_sockets.add(client_socket)
    client_socket.send("Welcome to Main chat!\n".encode())
    t = Thread(target=listen_for_client, args=(client_socket, client_address))
    t.daemon = True
    t.start()

for cs in client_sockets:
    cs.close()
s.close()