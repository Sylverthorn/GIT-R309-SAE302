import socket
import threading
import time
import random
import subprocess
import platform


class Server:
    def __init__(self, port_client, port_serv, hosts='0.0.0.0'):
        self.hosts = hosts

        self.port_serv = port_serv
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.port_client = port_client
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.secondary_servers = []  # Liste des serveurs secondaires en cours
        self.max_taches = 2  # Nombre max de tâches par serveur secondaire
        self.initialisation_serveur_secondaire()

    
    def start_client_socket(self, host, port_client):
        self.client_socket.bind((host, port_client))
        self.client_socket.listen(1)
        print(f"Socket client en écoute sur {host}:{port_client}")

    def start_server_socket(self, host, port_serv):
        self.server_socket.bind((host, port_serv))
        self.server_socket.listen(1)
        print(f"Socket serveur en écoute sur {host}:{port_serv}")

    def accept_client(self):
        while True:
            numero_client = random.randint(1, 1000)
            try:
                client, address = self.client_socket.accept()
                print(f"Connexion Client_{numero_client} : " + str(address))
                client_thread = threading.Thread(target=self.__recois, args=(client, numero_client))
                client_thread.start()
            except Exception as e:
                print("Server arrêté.")
                print(e)
                break
    
    def accept_server(self):
        while True:
            numero_serveur = random.randint(1, 1000)
            try:
                server, address = self.server_socket.accept()
                print(f"Connexion Serveur_{numero_serveur} : {address}")
                self.secondary_servers.append({"socket": server,"id": numero_serveur, "état": "disponible"})
            except Exception as e:
                print("Server arrêté.")
                print(e)
                break

    def __envoi_message(self, message, client=None):
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




    def toujours_là(self, client, numero_client):
        time.sleep(1)
        try:
            self.__envoi_message('hello', client)
        except Exception as e:
            print(f"Client_{numero_client} déconnecté : {e}")

    def initialisation_serveur_secondaire(self):
        for _ in range(2):
            self.creation_servsecond()

    def est_disponible(self, server):
        try:
            server_second = server["socket"]
            server_second.send(b'ping')
            response = server_second.recv(1024)

            if response == b'pong':
                server["état"] = "disponible"
            elif response == b'pang':  # Si le serveur est saturé
                server["état"] = "saturé"
            else:
                server["état"] = "indisponible"  # Par défaut si la réponse est inattendue
        except Exception:
            server["état"] = "indisponible"  # Si erreur de connexion, le serveur est considéré indisponible
    def __dispo(self):
        while True:
            for server in self.secondary_servers:
                self.est_disponible(server)
            

    def handle_task(self, task, client):
        available_server = None
        print(self.secondary_servers)
        # Vérifier tous les serveurs secondaires
        for server in self.secondary_servers:
            if server["état"] == "disponible":
                available_server = server
                break
            

        if available_server:
            print('\n[+] Serveur secondaire disponible trouvé')
            self.envoi_tache(task, available_server["id"], available_server, client)
        else:
            print("[*] Aucun serveur secondaire disponible pour traiter la tâche.")
            self.__envoi_message("Aucun serveur secondaire disponible pour traiter la tâche.", client)

            


    def creation_servsecond(self):
        
            
        server_second_path = "SAE 3.02\\server_second.py"
        

        try:
            if platform.system() == "Windows":
                subprocess.Popen(["start", "cmd", "/k", "python", server_second_path,'127.0.0.1', str(self.port_serv), str(self.max_taches)], shell=True)
            elif platform.system() == "Linux":
                subprocess.Popen(["gnome-terminal", "--", "python3", 'server_second.py','127.0.0.1', str(self.port_serv), str(self.max_taches)])

            print(f"Nouveau serveur secondaire lancé") 
        except Exception as e:
            print(f"Erreur lors du lancement du serveur secondaire : {e}")

        
        



    def envoi_tache(self, task, numero_serv, available_server, client):
        available_server['socket'].sendall(task.encode('utf-8'))
        print(f"Tâche déléguée au serveur secondaire {numero_serv}")
        time.sleep(1)
        try:
            response = available_server["socket"].recv(10000).decode()
        except Exception as e:
            print(f"\n[!] Erreur lors de la réception de la réponse du serveur secondaire {numero_serv} : {e}")
            response = 'indisponible'

        if response == 'indisponible':
            print(f"Serveur secondaire {numero_serv} indisponible.")
            available_server["état"] = "indisponible"
            threading.Thread(target=self.handle_task, args=(task, client)).start()
            return
        else: 
            available_server["état"] = "disponible"  
            print(f"\n[!] Réponse du serveur secondaire {numero_serv} : {response}")
            self.__envoi_message(response, client)
        
        
        

    def start(self):
        self.start_client_socket(self.hosts, self.port_client)
        self.start_server_socket(self.hosts, self.port_serv)
        threading.Thread(target=self.accept_client).start()
        threading.Thread(target=self.accept_server).start()
        #threading.Thread(target=self.__dispo).start()


if __name__ == "__main__":
    server = Server(4200, 5200)
    server.start()

    print("Serveur lancé. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
