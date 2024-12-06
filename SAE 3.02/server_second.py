import sys
import socket
import threading

class Server:
    def __init__(self, port, nb_taches, hosts='0.0.0.0'):
        self.port = port
        self.nb_taches = nb_taches
        self.hosts = hosts
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.task_count = 0
        self.lock = threading.Lock()

    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server Secondaire connecté sur le port: " + str(self.port))

    def __envoi_message(self, message, client=None):
        try:
            client.send(message.encode())
        except Exception as e:
            print(e)

    def __recois(self, client):
        while True:
            try:
                message = client.recv(1024).decode()
                if message:
                    print(f"Message reçu : {message}")
                    # Réponse au client
                    réponse = f"resultat|Traitement effectué sur serveur secondaire {self.port}."
                    self.__envoi_message(réponse, client)
            except Exception as e:
                print("Client déconnecté :", e)
                client.close()
                break

    def accept(self):
        while True:
            try:
                client, address = self.server_socket.accept()
                with self.lock:
                    self.task_count += 1
                    if self.task_count >= self.nb_taches:
                        print("Nombre de tâches atteint. Arrêt du serveur.")
                        self.server_socket.close()
                        sys.exit(0)
                print(f"Client connecté depuis {address}")
                threading.Thread(target=self.__recois, args=(client,)).start()
            except Exception as e:
                print("Erreur serveur secondaire :", e)
                break

    def start(self):
        self.__connect()
        self.accept()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python server_second.py <port> <nb_taches>")
        sys.exit(1)

    port = int(sys.argv[1])
    nb_taches = int(sys.argv[2])
    server = Server(port, nb_taches)
    server.start()
