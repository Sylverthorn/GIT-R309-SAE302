import socket
import threading
import time
import random

class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        



    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server connecté sur le port: " + str(self.port))



    def __reconnexion(self):
        self.__connect()



    def __envoi_message(self, message, client=None, numero_client=None):
        try:
            if message == b'': 
                client.send(message)
            else:
                client.send(message.encode())

        except ConnectionResetError:
            print("Client déconnecté.")
            client.close()
            self.__reconnexion()
        except ConnectionAbortedError:
            pass



    def __recois(self, client=None, numero_client=None):
        while True:
            
            try:
                self.toujours_là(client, numero_client)
                message = client.recv(1024).decode()
                if message:
                    if message == b'':
                        pass
                    else:
                        print(f"Message de client_{numero_client} :", message)
                        réponse = "Bien reçu !"
                        threading.Thread(target=self.__envoi_message, args=(réponse, client, numero_client,)).start()


                #pour arrêter le serveur et tout les clients
                '''
                if message.lower() == "arret":
                    print("Déconnexion demandée par le client...")
                    
                        
                   
                    for client_thread in threading.enumerate():
                        if client_thread is not threading.current_thread():
                            try:
                                client_thread._target.__self__.__envoi_message("arret", client_thread._args[0])
                            except Exception as e:
                                print(f"Erreur lors de l'envoi du message d'arrêt: {e}")
                    self.server_socket.close()
                    time.sleep(1)
                    break
                    '''
                #pour déconnecter un client
                '''
                if message.lower() == "bye":
                    print(f"Déconnexion du client : {client}...")
                    client.close()
                    break
                ''' 

            except ConnectionResetError:
                print(f"Client_{numero_client} déconnecté.")
                client.close()
                break
            except ConnectionAbortedError:
                pass



    def accept(self):
        while True:
            numero_client = random.randint(1, 1000)
            try:
                client, address = self.server_socket.accept()
                print(f"Connexion client : client_{numero_client} " + str(address))
                
                client_thread = threading.Thread(target=self.__recois, args=(client, numero_client))
                client_thread.start()

            except OSError as e:
                print("Server arrêté.")
                print(e)
                break



    def toujours_là(self, client, numero_client):
        try:
            self.__envoi_message(b'', client)
            
        except ConnectionResetError:
            client.close()
            print(f"Client_{numero_client} déconnecté.")
            return



    def start(self):
        self.__connect()
        self.accept()

if __name__ == "__main__":
    server = Server(4200)
    server.start()
