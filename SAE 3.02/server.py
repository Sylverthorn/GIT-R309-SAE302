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
        self.max_taches = 5  # Nombre max de tâches par serveur secondaire

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

    def handle_task(self, task, client):
        available_server = None
        for server in self.secondary_servers:
            if server['tasks'] < self.max_taches:
                available_server = server
                break

        if not available_server:
            # Si aucun serveur disponible, lancer un nouveau serveur secondaire
            available_server = self.creation_servsecond(available_server)

        # Envoyer la tâche au serveur secondaire disponible
        
        try:  
            time.sleep(4)  # Attendre avant d'envoyer la tâche pour s'assurer que le serveur secondaire est prêt
            self.envoi_tache(task, available_server, client)
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de la tâche au serveur sur le port {available_server['port']} : {e}")
            try:
                self.secondary_servers.remove(available_server)
            except Exception:
                pass
            self.handle_task(task, client)
    


    def creation_servsecond(self, available_server):
        new_port = random.randint(5000, 6000)
            
        server_second_path = "SAE 3.02\\server_second.py"
        

        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(["start", "cmd", "/k", "python", server_second_path, str(new_port), str(self.max_taches)], shell=True)
            elif platform.system() == "Linux":
                process = subprocess.Popen(["gnome-terminal", "--", "python3", 'server_second.py', str(new_port), str(self.max_taches)])
                


            
        except Exception as e:
            print(f"Erreur lors du lancement du serveur secondaire : {e}")

        print(f"Nouveau serveur secondaire lancé sur le port {new_port}")
        self.secondary_servers.append({'port': new_port, 'tasks': 0, 'process': process})
        available_server = self.secondary_servers[-1]

        
        return available_server
    


    def envoi_tache(self, task , available_server, client):
        secondary_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secondary_server.connect(('127.0.0.1', available_server['port']))
        secondary_server.send(task.encode())
        
        response = secondary_server.recv(1024).decode()
        self.__envoi_message(response, client)
        
        available_server['tasks'] += 1
        print(f"Tâche déléguée au serveur secondaire sur le port {available_server['port']}")
        return secondary_server

    def start(self):
        self.__connect()
        self.accept()


if __name__ == "__main__":
    server = Server(4200)
    server.start()