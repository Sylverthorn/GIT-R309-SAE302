import socket
import threading
import time
import os

class Client():
    def __init__(self, port, host='127.0.0.1'):
        self.port = port
        self.host = host
        self.client_socket = socket.socket()
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.state = "shutdown"

    def connect(self):
        self.state = "in progress"
        print("Client en marche !")
        print("Connexion au serveur ...")
        try:
            self.client_socket.connect((self.host, self.port))
            print('Connexion établie avec le serveur')
            self.state = "running"
            self.recois()
            


        except ConnectionRefusedError:
            
                print("Connexion refusée. Le serveur ne fonctionne pas.")
                i = 0
                while i != 5:
                    time.sleep(0.3)

                    if self.state == "shutdown":
                        break

                    else:
                        try:
                            self.client_socket.connect((self.host, self.port))
                            print('Connexion établie avec le serveur')
                            self.state = "running"
                            self.recois()
                            
                            break
                        except ConnectionRefusedError:
                            print("Connexion refusée. Le serveur ne fonctionne pas.")
                            i += 1

                        if i == 5:
                            print("Connexion impossible, le serveur ne fonctionne pas.")
                            self.state = "shutdown"
                            self.client_socket.close()
                            return
        except OSError:
            self.__reconnexion()



    def __reconnexion(self):
        print("Serveur en panne, reconnexion...")
        self.client_socket.close()
        self.state = "shutdown"
        self.client_socket = socket.socket()
        self.connect()


    def __envoi_message(self, message):
            try:
                if message == b'': 
                    self.client_socket.send(message)
                else:
                    self.client_socket.send(message.encode())

                time.sleep(0.3)

                '''  arret à partir du terminal

                if message.lower() == "bye":
                    print("Déconnexion du client...")
                    self.client_socket.close()
                    break

                elif message.lower() == "arret":
                    print("Client et serveur s'arrêtent...")
                    self.client_socket.close()
                    self.boucle = False
                    break
                '''
            except ConnectionResetError:
                self.__reconnexion()
            
            except KeyboardInterrupt:
                print("efsdfArret du client ...")
                self.client_socket.close()
                self.state = "shutdown"
                return
            except OSError:
                pass

                

    def __recois_message(self):
        while True:
            

            if self.state == "shutdown":
                break
            try:
                reply = self.client_socket.recv(1024).decode()
                if reply:
                    if reply.lower() == "hello" or reply.lower() == "hellohello":
                        pass
                    else :
                        print("Message du serveur:", reply)
                
            except ConnectionResetError:
                self.__reconnexion()
            except ConnectionAbortedError:
                self.state = "shutdown"
                break
            except OSError:
                self.state = "shutdown"
                break
    



    

    def envoi(self, message):
        send_thread = threading.Thread(target=self.__envoi_message, args=(message,))
        send_thread.start()

    def recois(self):
        receive_thread = threading.Thread(target=self.__recois_message)
        receive_thread.start()

    def arret(self):
        self.state = "shutdown"
        try :
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            print("Arret du client ...")
            
        except Exception as e:
            time.sleep(1.5)
            print("Arret du client ...")
            self.state = "shutdown"
            return

    def quitter(self):
        self.arret()
        print("Client arrêté proprement.")
        os._exit(0)



    



if __name__ == "__main__":
    client = Client(12345)
    