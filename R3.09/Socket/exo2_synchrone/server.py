import socket

port = 12345    
reply = "reply Hello, World!"

hosts = '0.0.0.0'

server_socket = socket.socket()
server_socket.bind((hosts, port))
print("Server connecté sur le port: " + str(port))

while True:
    server_socket.listen(1)
    connection, address = server_socket.accept()
    print("Connection client : " + str(address))

    while True:
        try:
            message = connection.recv(1024).decode()
            print("Message du client: " + message)

            if message.lower() == "arret":
                print("deconnection...")
                connection.close()
                server_socket.close()
                exit()
            else:
                connection.send(reply.encode())
        except ConnectionAbortedError:
            print("Client déconnecté.")
            break
    



