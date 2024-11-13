import socket
import threading
import time
class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts
        self.server_socket = socket.socket()
        self.connection = None
        self.boucle = True


    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server connecté sur le port: " + str(self.port))

        self.connection, address = self.server_socket.accept()
        print("Connexion client : " + str(address))


    def __reconnexion(self):
        self.server_socket.close()
        self.server_socket = socket.socket()
        self.__connect()



    def __envoi_message(self):
        while self.boucle:
            try:
                message = input("Enter message: ")
                self.connection.send(message.encode())
                time.sleep(1)

            
                if message.lower() == "arret":
                    print("Client et serveur s'arrêtent...")
                    self.server_socket.close()
                    self.boucle = False
                    break

            except ConnectionResetError:
                self.__reconnexion()
            
            except KeyboardInterrupt:
                print("Arret du client ...")
                self.client_socket.close()
                break


    def __recois(self):
        while self.boucle:
            try:
                message = self.connection.recv(1024).decode()
                print("\nMessage du client:", message)
                print('\nEnter message: ', end="")
                if message.lower() == "arret":
                    print("Déconnexion demandée par le client...")
                    self.boucle = False

                    self.connection.close()
                    self.server_socket.close()
                    break

            except ConnectionResetError:
                print("Client déconnecté.")
                self.boucle = False
                self.__reconnexion()
                break



    def start(self):
        self.__connect()


        send_thread = threading.Thread(target=self.__envoi_message)
        receive_thread = threading.Thread(target=self.__recois)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

if __name__ == "__main__":
    server = Server(12345)
    server.start()
