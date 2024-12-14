import socket
import threading
import time
import random
import subprocess
import platform


class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.secondary_servers = []  # Liste des serveurs secondaires en cours
        self.max_taches = 2  # Nombre max de tâches par serveur secondaire
        self.initialisation_serveur_secondaire()


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
        except Exception as e:
            print(e)

    def __recois(self, client=None, numero_client=None):
        while True:
            
            self.toujours_là(client, numero_client)
            try:
                message = client.recv(10000).decode(errors='ignore')
                
                if message:
                    print(f"Message de client_{numero_client} :", message)
                    threading.Thread(target=self.handle_task, args=(message, client,)).start()
            except Exception as e:
                print(f"Client_{numero_client} déconnecté : {e}")
                client.close()
                break

    def accept(self):
        while True:
            numero_client = random.randint(1, 1000)
            try:
                client, address = self.server_socket.accept()
                print(f"Connexion client : client_{numero_client} " + str(address))
                client_thread = threading.Thread(target=self.__recois, args=(client, numero_client))
                client_thread.start()
            except Exception as e:
                print("Server arrêté.")
                print(e)
                break

    def toujours_là(self, client, numero_client):
        time.sleep(1)
        try:
            self.__envoi_message('hello', client)
        except Exception as e:
            print(f"Client_{numero_client} déconnecté : {e}")

    def initialisation_serveur_secondaire(self):
        for i in range(2):
            self.creation_servsecond()

    def est_disponible(self, server):
        try:
            secondary_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secondary_server.connect(('127.0.0.1', server['port']))
            secondary_server.send(b'ping')
            response = secondary_server.recv(1024)
            secondary_server.close()
            return True if response.decode() == 'pong' else False
        except Exception:
            return False

    def handle_task(self, task, client):
        available_server = None
        
        for server in self.secondary_servers:
            print(f"debug 93 {server}")
            if server["état"] == "disponible":
                if self.est_disponible(server):
                    available_server = server
                    print(f"debug 0 {available_server}")
                    break
                else:
                    server["état"] = "indisponible"

        if not available_server:
            for server in self.secondary_servers:
                if server["état"] == "indisponible":
                    if self.est_disponible(server):
                        available_server = server
                        server["état"] = "disponible"
                        break
        # Envoyer la tâche au serveur secondaire disponible
        if available_server and self.est_disponible(available_server): # Attendre avant d'envoyer la tâche pour s'assurer que le serveur secondaire est prêt
            print (f"debug 2 {available_server}")
            self.envoi_tache(task, available_server, client)
            return
        else:
            print("Aucun serveur secondaire disponible pour traiter la tâche.")
            self.__envoi_message("Aucun serveur secondaire disponible pour traiter la tâche.", client)
            return
            


    def creation_servsecond(self):
        new_port = random.randint(5000, 6000)
            
        server_second_path = "SAE 3.02\\server_second.py"
        

        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(["start", "cmd", "/k", "python", server_second_path, str(new_port), str(self.max_taches)], shell=True)
            elif platform.system() == "Linux":
                process = subprocess.Popen(["gnome-terminal", "--", "python3", 'server_second.py', str(new_port), str(self.max_taches)])
                

            état = "disponible"
            
        except Exception as e:
            print(f"Erreur lors du lancement du serveur secondaire : {e}")

        print(f"Nouveau serveur secondaire lancé sur le port {new_port}")
        new_server = {'port': new_port, "état": état, 'process': process}
        self.secondary_servers.append(new_server)

        return new_server
        

        
        
    


    def envoi_tache(self, task , available_server, client):
        secondary_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secondary_server.connect(('127.0.0.1', available_server['port']))
        secondary_server.send(task.encode())
        
        response = secondary_server.recv(1024).decode()
        self.__envoi_message(response, client)
        
        
        
        print(f"Tâche déléguée au serveur secondaire sur le port {available_server['port']}")
        return secondary_server

    def start(self):
        self.__connect()
        self.accept()


if __name__ == "__main__":
    server = Server(4200)
    server.start()