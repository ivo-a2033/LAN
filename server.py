import socket, pickle
import threading


print("Server is Listening.....")
HOST = 'localhost'
PORT = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)

def exchange_data():
    i=0
    while True:
        # Receive data
        data = conn.recv(4096).decode("utf-8")
        print(data)
        #Send new data
        conn.send(("response").encode("utf-8"))
        if data == "close":
            break
    conn.close()

new_thread = threading.Thread(target=exchange_data)
new_thread.start()