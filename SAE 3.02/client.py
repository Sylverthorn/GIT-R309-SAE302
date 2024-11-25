import socket
import threading
import time

class Client():
    def __init__(self, port, host='127.0.0.1'):
        self.port = port
        self.host = host
        self.client_socket = socket.socket()
        self.boucle = True

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print('connexion ...')
        except ConnectionRefusedError:
            try:
                print("Connexion refusée. Le serveur ne fonctionne pas.")
                for _ in range(5):
                    time.sleep(1)
                    try:
                        self.client_socket.connect((self.host, self.port))
                    except ConnectionRefusedError:
                        print("Connexion refusée. Le serveur ne fonctionne pas.")


            except KeyboardInterrupt:
                print("Arret du client ...")
                exit()

    def __reconnexion(self):
        print("Serveur en panne, reconnexion...")
        self.client_socket.close()
        self.client_socket = socket.socket()
        self.connect()


    def __envoi_message(self, message):
        while self.boucle:
            try:
                
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

                

    def __recois_message(self):
        while self.boucle:
            try:
                reply = self.client_socket.recv(1024).decode()
                if reply:
                    if reply.lower() == "arret":
                        print("arret ...")
                        self.client_socket.close()
                        self.boucle = False
                        break
                    else :
                        print("Message du serveur:", reply)
                
            except ConnectionResetError:
                self.__reconnexion()
            except ConnectionAbortedError:
                break
            except OSError:
                print("client et serveur arreté.")
                break
    
    def envoi(self, message):
        send_thread = threading.Thread(target=self.__envoi_message)
        send_thread.start()

    def recois(self):
        receive_thread = threading.Thread(target=self.recois)
        receive_thread.start

    def arret(self):
        self.boucle = False
        self.client_socket.close()

    def start(self):
        self.boucle = True
        self.connect()

        send_thread = threading.Thread(target=self.__envoi_message)
        receive_thread = threading.Thread(target=self.recois)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

if __name__ == "__main__":
    client = Client(12345)
    client.start()