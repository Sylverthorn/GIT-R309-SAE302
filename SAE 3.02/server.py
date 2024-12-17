import socket
import threading
import time
import random
import subprocess
import platform
import sys


RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'
class Server:
    def __init__(self,ip, max_taches, cpu=10, port_client=4200, port_serv=5200, local=True, nb_server=2 ,hosts='0.0.0.0'):
        self.hosts = hosts
        self.ip = ip
        self.port_serv = port_serv
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.port_client = port_client
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.secondary_servers = [] 
        self.max_taches = max_taches
        self.cpu_max = cpu
        self.nb_server = nb_server

        self.local = local
        if self.local == "True":
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
                print(f"{GREEN}[!] Connexion Client_{numero_client} : " + str(address))
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
                print(f"{GREEN} [!] Connexion Serveur_{numero_serveur} : {address}")
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
                    print(f"{BLUE} [<--] Message de client_{numero_client} : {RESET}\n", message)
                    threading.Thread(target=self.handle_task, args=(message, client,)).start()
            except Exception as e:
                print(f"{RED} [!] Client_{numero_client} déconnecté : {e}")
                client.close()
                break




    def toujours_là(self, client, numero_client):
        time.sleep(1)
        try:
            self.__envoi_message('hello', client)
        except Exception as e:
            print(f"{RED} [!] Client_{numero_client} déconnecté")

    def initialisation_serveur_secondaire(self):
        for _ in range(self.nb_server):
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
        
        for server in self.secondary_servers:
            if server["état"] == "disponible":
                available_server = server
                break
            

        if available_server:
            print(f'{GREEN} \n[+] Serveur secondaire disponible trouvé')
            self.envoi_tache(task, available_server["id"], available_server, client)
        else:
            print(f"{RED} [-] Aucun serveur secondaire disponible pour traiter la tâche.")
            self.__envoi_message(f"{RED} [-] Aucun serveur secondaire disponible pour traiter la tâche.", client)

            


    def creation_servsecond(self):
        
            
        server_second_path = "server_second.py"
        

        try:
            if platform.system() == "Windows":
                try:
                    subprocess.Popen(["start", "cmd", "/k", "python", server_second_path, self.ip, str(self.port_serv), str(self.max_taches), str(self.cpu_max)], shell=True)
                except:
                    subprocess.Popen(["start", "cmd", "/k", "python", "server_second.py", self.ip, str(self.port_serv), str(self.max_taches), str(self.cpu_max)], shell=True)

            elif platform.system() == "Linux":
                subprocess.Popen(["gnome-terminal", "--", "python3", 'server_second.py', self.ip, str(self.port_serv), str(self.max_taches), str(self.cpu_max)])

            print(f"Nouveau serveur secondaire lancé") 
        except Exception as e:
            print(f"Erreur lors du lancement du serveur secondaire : {e}")

        
        



    def envoi_tache(self, task, numero_serv, available_server, client):
        available_server['socket'].sendall(task.encode('utf-8'))
        print(f"{BLUE} [==>] Tâche déléguée au serveur secondaire {numero_serv}")
        time.sleep(1)
        try:
            response = available_server["socket"].recv(10000).decode()
        except Exception as e:
            print(f"{RED} \n[!] Erreur lors de la réception de la réponse du serveur secondaire {numero_serv} : {e}")
            response = 'indisponible'

        if response == 'indisponible':
            print(f"{RED} [!]Serveur secondaire {numero_serv} indisponible.")
            available_server["état"] = "indisponible"
            threading.Thread(target=self.handle_task, args=(task, client)).start()
            return
        else: 
            available_server["état"] = "disponible"  
            print(f"{BLUE} \n[<--] Réponse du serveur secondaire {numero_serv} {RESET}:\n {response}")
            self.__envoi_message(response, client)
        
    def stop(self):
        print("\nArrêt du serveur.")
        for server in self.secondary_servers:
            server['socket'].send("shutdown")
        self.client_socket.close()
        self.server_socket.close()
        sys.exit(0)

        

    def start(self):
        self.start_client_socket(self.hosts, self.port_client)
        self.start_server_socket(self.hosts, self.port_serv)
        threading.Thread(target=self.accept_client).start()
        threading.Thread(target=self.accept_server).start()
        #threading.Thread(target=self.__dispo).start()

if __name__ == "__main__":

    if len(sys.argv) != 8:
        print("Usage : python server_second.py <master_host> <master_port> <nb_taches>")
        sys.exit(1)
        
    print("==========================================")
    print("          Serveur Maître                  ")
    print("==========================================")
    print(f"Adresse IP     : {sys.argv[1]}")
    print(f"Port client    : {sys.argv[5]}")
    print(f"Port client    : {sys.argv[4]}")
    print(f"Nb tâches max  : {sys.argv[2]}")
    print(f"CPU max        : {sys.argv[3]}")
    print(f"Nb serveurs 2d : {sys.argv[7]}")
    print(f"serveurs local : {sys.argv[6]}")
    print("==========================================")

    ip_maitre = sys.argv[1]
    port_client = int(sys.argv[2])
    port_serveur = int(sys.argv[3])
    nb_taches = int(sys.argv[4])
    cpu_max = int(sys.argv[5])
    local = sys.argv[6] 
    nb_serv = int(sys.argv[7])

    server = Server(ip_maitre, nb_taches, cpu_max, port_client, port_serveur, local, nb_serv)
    server.start()

    print("Serveur lancé. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        server.client_socket.close()
        server.server_socket.close()
        sys.exit(0)
