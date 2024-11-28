import socket
import threading
import time

class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            self.toujours_là(client)
            try:
                message = client.recv(1024).decode()
                if message:
                    print(f"Message de client{client} :", message)
                    réponse = "Bien reçu !"
                    threading.Thread(target=self.__envoi_message, args=(réponse, client,)).start()

                if message.lower() == "arret":
                    print("Déconnexion demandée par le client...")
                    
                        
                   
                    for client_thread in threading.enumerate():
                        if client_thread is not threading.current_thread():
                            try:
                                client_thread._target.__self__.__envoi_message("arret", client_thread._args[0])
                            except Exception as e:
                                print(f"Erreur lors de l'envoi du message d'arrêt: {e}")
                    self.boucle = False
                    self.server_socket.close()
                    time.sleep(1)
                    break
                if message.lower() == "bye":
                    print(f"Déconnexion du client : {client}...")
                    client.close()
                    break
                    

            except ConnectionResetError:
                print(f"Client déconnecté : {client}")
                self.boucle = False
                break

    def handle_client(self, client):
        self.__recois(client)

    def accept(self):
        while self.boucle:
            try:
                client, address = self.server_socket.accept()
                print("Connexion client : " + str(address))
                
                client_thread = threading.Thread(target=self.handle_client, args=(client,))
                client_thread.start()

            except OSError as e:
                print("Server arrêté.")
                print(e)
                break

    def toujours_là(self, client):
        try:
            self.__envoi_message('hello', client)
        except ConnectionResetError:
            self.boucle = False
            print(f"Client déconnecté : {client}")
            return

    def start(self):
        self.__connect()
        self.accept()

if __name__ == "__main__":
    server = Server(4200)
    server.start()
