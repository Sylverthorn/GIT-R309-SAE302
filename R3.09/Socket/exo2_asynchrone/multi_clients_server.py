import socket
import threading
import time

class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.boucle = True

    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server connecté sur le port: " + str(self.port))

    def __reconnexion(self):
        self.__connect()

    def __envoi_message(self, message, client=None):
        try:
            client.send(message.encode())
        except ConnectionResetError:
            print("Client déconnecté.")
            self.boucle = False
            self.__reconnexion()

    def __recois(self, client=None):
        while self.boucle:
            try:
                message = client.recv(1024).decode()
                if message:
                    print(f"Message de {client} :", message)
                    réponse = "Bien reçu !"
                    threading.Thread(target=self.__envoi_message, args=(réponse, client,)).start()

                if message.lower() == "arret":
                    print("Déconnexion demandée par le client...")
                    self.boucle = False
                    self.server_socket.close()
                    time.sleep(1)
                    
                    break
                if message.lower() == "bye":
                    print(f"Déconnexion du client : {client}...")
                    client.close()
                    break
                    

            except ConnectionResetError:
                print("Client déconnecté.")
                self.boucle = False
                client.close()
                break

    def handle_client(self, client):
        self.__recois(client)

    def accept(self):
        while self.boucle:
            client, address = self.server_socket.accept()
            print("Connexion client : " + str(address))
            
            client_thread = threading.Thread(target=self.handle_client, args=(client,))
            client_thread.start()

    def start(self):
        self.__connect()
        self.accept()

if __name__ == "__main__":
    server = Server(12345)
    server.start()
