import socket
import threading

class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts
        self.server_socket = socket.socket()
        self.connection = None
        self.boucle = True

# fonction qui connecte le serveur et le client

    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server connecté sur le port: " + str(self.port))




    def __reconnexion(self):
        self.__connect()


# fonction qui envoi un message au client

    def __envoi_message(self, message, client=None):
        try:
            client.send(message.encode())

        except (ConnectionResetError, BrokenPipeError):
            print("Client déconnecté.")
            self.boucle = False
            self.__reconnexion()

# fonction qui recoit les messages du client et les traites

    def __recois(self, client=None):
        while self.boucle:
            try:
                message = client.recv(1024).decode()
                if message:
                    print("Message du client:", message)

                    réponse = "Bien reçu !"
                    threading.Thread(target=self.__envoi_message , args=(réponse, client,)).start()

                if message.lower() == "arret":
                    print("Déconnexion demandée par le client...")
                    self.boucle = False

                    client.close()
                    self.server_socket.close()
                    break

            except ConnectionResetError:
                print("Client déconnecté.")
                self.boucle = False
                self.__reconnexion()
                break


# fonction qui lance le serveur

    def start(self):
        self.__connect()

        while True:
            client, address = self.server_socket.accept()
            print("Connexion client : " + str(address))
        
            receive_thread = threading.Thread(target=self.__recois, args=(client,))
            receive_thread.start()

            

if __name__ == "__main__":
    server = Server(12345)
    server.start()
