import socket
import threading
import time
import random
import subprocess
import platform
import sys
import os


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
        self.liste_clients = []

        self.serveurs_secondaires = [] 
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
                self.liste_clients.append({"socket": client})
                client_thread.start()
            except Exception as e:
                break
    
    def accept_server(self):
        while True:
            numero_serveur = random.randint(1, 1000)
            try:
                server, address = self.server_socket.accept()
                print(f"{GREEN} [!] Connexion Serveur_{numero_serveur} : {address}")
                self.serveurs_secondaires.append({"socket": server,"id": numero_serveur, "état": "disponible"})
            except Exception as e:
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
                    threading.Thread(target=self.load_balancing, args=(message, client,)).start()
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

            

    def load_balancing(self, task, client):
        available_server = None
        
        for server in self.serveurs_secondaires:
            if server["état"] == "disponible":
                available_server = server
                break
            

        if available_server:
            print(f'{GREEN}\n[+] Serveur secondaire disponible trouvé')
            self.envoi_tache(task, available_server["id"], available_server, client)
        else:
            print(f"{RED}[-] Aucun serveur secondaire disponible pour traiter la tâche.")
            self.__envoi_message(f"{RED} [-] Aucun serveur secondaire disponible pour traiter la tâche.", client)

            




    def creation_servsecond(self):
        server_second_path = "server_second.py"

        try:
            if platform.system() == "Windows":
                subprocess.Popen(["start", "cmd", "/k", "python", server_second_path, self.ip, str(self.port_serv), str(self.max_taches), str(self.cpu_max)], shell=True)

            elif platform.system() == "Linux":
                # Liste des terminaux avec leurs options pour exécuter une commande
                terminals = {
                    "gnome-terminal": ["--"],
                    "x-terminal-emulator": ["-e"],
                    "konsole": ["-e"],
                    "xfce4-terminal": ["-x"],
                    "lxterminal": ["-e"],
                    "mate-terminal": ["--"],
                    "termite": ["-e"],
                    "alacritty": ["-e"],
                    "urxvt": ["-e"],
                    "xterm": ["-e"]
                }

                for terminal, options in terminals.items():
                    try:
                        # Tente d'utiliser le terminal avec ses options
                        subprocess.Popen([terminal, *options, "python3", server_second_path, self.ip, str(self.port_serv), str(self.max_taches), str(self.cpu_max)])
                        print(f"Serveur lancé avec {terminal}")
                        break  # Si succès, on sort de la boucle
                    except FileNotFoundError:
                        continue  # Passe au terminal suivant
                else:
                    raise EnvironmentError("Aucun terminal compatible trouvé sur votre système.")

            print(f"Nouveau serveur secondaire lancé")
        except Exception as e:
            print(f"Erreur lors du lancement du serveur secondaire : {e}")


            
        



    def envoi_tache(self, task, numero_serv, available_server, client):
        
        try:
            available_server['socket'].sendall(task.encode('utf-8'))
            print(f"{BLUE}[==>] Tâche déléguée au serveur secondaire {numero_serv}")
            time.sleep(1)
        except Exception as e:
            print(f"{RED}[!] Erreur lors de l'envoi de la tâche au serveur secondaire {numero_serv} : {e}")
            available_server["état"] = "indisponible"
            threading.Thread(target=self.load_balancing, args=(task, client)).start()
            return
        
        try:
            response = available_server["socket"].recv(10000).decode()
        except Exception as e:
            print(f"{RED}\n[!] Erreur lors de la réception de la réponse du serveur secondaire {numero_serv} : {e}")
            response = 'indisponible'
        try:
            if response.split('|')[0] == "indisponible" or response == 'indisponible':
                print(f"{RED}[!] Serveur secondaire {numero_serv} indisponible.")
                a = response.split('indisponible|')[1]
                print(f'{RESET}------------------- {a} -------------------')
                available_server["état"] = "indisponible"
                threading.Thread(target=self.load_balancing, args=(a, client)).start()
                return
            else: 
                available_server["état"] = "disponible"  
                print(f"{BLUE}\n[<--] Réponse du serveur secondaire {numero_serv} {RESET}:\n {response}")
                self.__envoi_message(response, client)
        except:
            pass

    def stop(self):
        print(f"{RESET}\nArrêt du serveur.")
        for server in self.serveurs_secondaires:
            try:
                server['socket'].send("shutdown".encode())
                server['socket'].close()
            except Exception as e:
                print(f"Erreur lors de l'arrêt du serveur secondaire : {e}")
        for client in self.liste_clients:
            try:
                client['socket'].send("shutdown".encode())
                client['socket'].close()
            except Exception as e:
                print(f"Erreur lors de l'arrêt du client : {e}")
        time.sleep(1)
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
