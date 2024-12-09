import os
import sys
import socket
import threading
import subprocess

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
                message = client.recv(10000).decode()
                if message:
                    print(f"Message reçu : {message}")
                    fichier = self.fichier(client, message)
                    resultat = self.execute_script(fichier)
                    # Réponse au client
                    réponse = f"""resultat|┌──(root㉿)-[resultat] 
└─# {resultat}"""
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
                        os._exit(0)
                        
                print(f"Client connecté depuis {address}")
                threading.Thread(target=self.__recois, args=(client,)).start()
            except Exception as e:
                print("Erreur serveur secondaire :", e)
                break
    

    def fichier(self, client, message):
        try:
            fichier, contenu = message.split('|')
            nom_fichier = fichier.split('/')[-1]
            
            if os.name == 'nt':  # For Windows
                chemin_fichier = f"SAE 3.02\\fichiers à executer\\{fichier}"
            else:  # For Linux/Unix
                chemin_fichier = f"SAE 3.02/fichiers à executer/{fichier}"
                
            with open(chemin_fichier, 'w', encoding='utf-8') as file:
                file.write(contenu)

        except Exception as e:
            print("Erreur lors de l'enregistrement du fichier :", e)
            self.__envoi_message("Erreur lors de l'enregistrement du fichier.", client)

        return nom_fichier
    

    
    def python(self, fichier):
        try:
            result = subprocess.run(['python', fichier], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        except Exception as e:
            print("Erreur lors de l'exécution du script :", e)
            return "Erreur lors de l'exécution du script."
        finally:
            try:
                os.remove(fichier)
            except Exception as e:
                print("Erreur lors de la suppression du fichier Python :", e)


    def c(self, fichier):
        try:
            result = subprocess.run(['gcc', fichier, '-o', 'output'], capture_output=True, text=True)
            if result.returncode != 0:
                return result.stderr.strip()
            result = subprocess.run(['./output'], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        except Exception as e:
            print("Erreur lors de l'exécution du script C :", e)
            return "Erreur lors de l'exécution du script C."
        
        
    def java(self, fichier):
        try:
            compile_result = subprocess.run(['javac', fichier], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return compile_result.stderr.strip()
            class_file = fichier.replace('.java', '')
            path = os.path.dirname(class_file)
            class_file = class_file.split('\\')[-1]

            run_result = subprocess.run(['java', '-cp', path, class_file], capture_output=True, text=True)
            return run_result.stdout.strip() if run_result.returncode == 0 else run_result.stderr.strip()
        except Exception as e:
            print("Erreur lors de l'exécution du script Java :", e)
            return "Erreur lors de l'exécution du script Java."
        finally:
            try:
                os.remove(fichier)
                class_file_path = fichier.replace('.java', '.class')
                if os.path.exists(class_file_path):
                    os.remove(class_file_path)
            except Exception as e:
                print("Erreur lors de la suppression des fichiers Java :", e)
        
    def cpp(self, fichier):
        try:
            compile_result = subprocess.run(['g++', fichier, '-o', 'output'], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return compile_result.stderr.strip()
            run_result = subprocess.run(['./output'], capture_output=True, text=True)
            return run_result.stdout.strip() if run_result.returncode == 0 else run_result.stderr.strip()
        except Exception as e:
            print("Erreur lors de l'exécution du script C++ :", e)
            return "Erreur lors de l'exécution du script C++."

    def execute_script(self, fichier):

        if os.name == 'nt':  # For Windows
            chemin_fichier = f"SAE 3.02\\fichiers à executer\\{fichier}"
        else:
            chemin_fichier = f"SAE 3.02/fichiers à executer/{fichier}"

        if fichier.endswith('.py'):
            return self.python(chemin_fichier)
        elif fichier.endswith('.c'):
            return self.c(chemin_fichier)
        elif fichier.endswith('.java'):
            return self.java(chemin_fichier)
        elif fichier.endswith('.cpp'):
            return self.cpp(chemin_fichier)
        else:
            return "Type de fichier non supporté."
            
    

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
