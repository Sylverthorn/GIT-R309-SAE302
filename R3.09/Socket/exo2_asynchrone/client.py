import socket
import threading
import time

class Client():
    def __init__(self, port, host='127.0.0.1'):
        self.port = port
        self.host = host
        self.client_socket = socket.socket()
        self.boucle = True

    def __connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            try:
                print("Connexion refusée. Le serveur ne fonctionne pas.")
                for i in range(5):
                    time.sleep(1)
                    print(".", end="")
                print()
                self.__connect()

            except KeyboardInterrupt:
                print("Arret du client ...")
                exit()

    def __reconnexion(self):
        print("Serveur en panne, reconnexion...")
        self.client_socket.close()
        self.client_socket = socket.socket()
        self.__connect()


    def __envoi_message(self):
        while self.boucle:
            try:
                message = input("Enter message: ")
                self.client_socket.send(message.encode())
                time.sleep(1)

                if message.lower() == "bye":
                    print("Déconnexion du client...")
                    self.client_socket.close()
                    self.boucle = False
                    break

                elif message.lower() == "arret":
                    print("Client et serveur s'arrêtent...")
                    self.client_socket.close()
                    self.boucle = False
                    break

            except ConnectionResetError:
                self.__reconnexion()
            
            except KeyboardInterrupt:
                print("Arret du client ...")
                self.client_socket.close()
                break

            
            except ConnectionAbortedError:
                break
                

    def __recois(self):
        while self.boucle:
            try:
                reply = self.client_socket.recv(1024).decode()
                print("\nRéponse du serveur:", reply)
                print('\nEnter message: ', end='')
            except ConnectionResetError:
                self.__reconexion()
            except ConnectionAbortedError:
                break



    def start(self):
        self.boucle = True
        self.__connect()

        send_thread = threading.Thread(target=self.__envoi_message)
        receive_thread = threading.Thread(target=self.__recois)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

if __name__ == "__main__":
    client = Client(12345)
    client.start()