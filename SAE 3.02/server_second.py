import os
import sys
import socket
import threading
import subprocess
import random
import time

import psutil

class Server:
    def __init__(self, master_host, master_port, nb_taches, cpu=2):
        self.master_host = master_host
        self.master_port = master_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.nb_taches = nb_taches
        self.cpu_max = cpu
        self.usage_cpu = 0
        self.file_attente = []

    def __connect(self):
            print(f"Serveur secondaire démarré")
            self.register_to_master()
            time.sleep(2)
            threading.Thread(target=self.__recois).start()
            
            threading.Thread(target=self.file_execution).start()

    def register_to_master(self):
        while True:
            essai = 0
            try:
                    self.server_socket.connect((self.master_host, self.master_port))
                    print(f"Enregistré auprès du serveur maître {self.master_host}:{self.master_port}")
                    break
            except Exception as e:
                if essai == 5:
                    print(f"Impossible de se connecter au serveur maître : {e}. Arrêt du serveur secondaire.")
                    self.server_socket.close()
                    sys.exit(1)

                print(f"Impossible de se connecter au serveur maître : {e}. Nouvel essai dans 5 secondes.")
                time.sleep(5)
                essai += 1


    def __envoi_message(self, message):
        try:
            self.server_socket.send(message.encode())
        except Exception as e:
            print(e)

    def utilisation_cpu(self):
        
        process = psutil.Process(os.getpid())  
        while True:
            cpu_usage = process.cpu_percent(interval=1) / psutil.cpu_count() 
            self.cpu = round(cpu_usage, 2)
            time.sleep(1) 


    def __recois(self):
        while True:
            try:
                message = self.server_socket.recv(10000).decode()
            except ConnectionResetError as e:
                print(f" [!] Connexion perdue avec le serveur maître : {e}")
                self.server_socket.close()
                sys.exit(1)
                break

            if message:
                if message == 'shutdown':
                    print("\nArret du Server Secondaire")
                    self.server_socket.close()
                    sys.exit(0)

                if message.startswith('script|'):
                    if self.usage_cpu > self.cpu_max:
                        print("CPU saturé, veuillez patienter.")
                        self.__envoi_message("indisponible")
                        
                    elif len(self.file_attente) < self.nb_taches:
                        self.file_attente.append(message)

                        print(f"\n[Script reçu] ")
                        print("[+] ajouté à la file d'attente")
                        print(f"[?] Nombre de tâches en attente : {len(self.file_attente)}")
                        print(self.file_attente)
                    
                    else:
                        print("Tâches saturées, veuillez patienter.")
                        self.__envoi_message("indisponible")


    def file_execution(self):
        while True:
            if len(self.file_attente) > 0:
                for message in self.file_attente:
                    fichier = self.fichier(message)
                    resultat = self.execute_script(fichier)
                    print('\n!! Execution terminé !!')
                    self.file_attente.remove(message)
                    print(f"[?] Nombre de tâches en attente : {len(self.file_attente)}")
                    
                    # Réponse au client
                    réponse = f"""resultat|┌──(root㉿)-[resultat] 
└─# {resultat}"""
                    self.__envoi_message(réponse)
                    
            time.sleep(1)  # Petite pause pour permettre aux autres messages de passer


    def fichier(self, message):
        try:
            _, fichier, contenu = message.split('|')
            nom, extension = fichier.split('.')
            if extension == 'java':
                pass
            else:
                rand = random.randint(1, 1000)
                fichier = f"{nom}_{rand}.{extension}"

            if os.name == 'nt':  # For Windows
                try:
                    chemin_fichier = f"SAE 3.02/fichiers à executer/{fichier}"
                    
                except:
                    chemin_fichier = f"SAE 3.02/fichiers à executer/{fichier}"

            else:  # For Linux/Unix
                chemin_fichier = f"fichiers_a_executer/{fichier}"

            with open(chemin_fichier, 'w', encoding='utf-8') as file:
                file.write(contenu)

        except Exception as e:
            print("Erreur lors de l'enregistrement du fichier :", e)
            self.__envoi_message("Erreur lors de l'enregistrement du fichier.")

        return fichier

    def python(self, fichier):
        try:
            if os.name == 'nt':  # For Windows
                result = subprocess.run(['python', fichier], capture_output=True, text=True)
            else:
                result = subprocess.run(['python3', fichier], capture_output=True, text=True)

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
        finally:
            try:
                os.remove(fichier)
                if os.path.exists('output'):
                    os.remove('output')
            except Exception as e:
                print("Erreur lors de la suppression des fichiers C :", e)

    def java(self, fichier):
        try:
            compile_result = subprocess.run(['javac', fichier], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return compile_result.stderr.strip()
            class_file = fichier.replace('.java', '')
            path = os.path.dirname(class_file)
            class_file = class_file.split('\\')[-1] if os.name == 'nt' else class_file.split('/')[-1]

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
        finally:
            try:
                os.remove(fichier)
                if os.path.exists('output'):
                    os.remove('output')
            except Exception as e:
                print("Erreur lors de la suppression des fichiers C++ :", e)

    def execute_script(self, fichier):
        if os.name == 'nt':  # For Windows
            try:
                chemin_fichier = f"fichiers à executer/{fichier}"  
            except:
                chemin_fichier = f"SAE 3.02//fichiers à executer//{fichier}"

        else:
            chemin_fichier = f"fichiers à executer/{fichier}"

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
        

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage : python server_second.py <master_host> <master_port> <nb_taches>")
        sys.exit(1)
        

    
    print("==========================================")
    print("          Serveur Secondaire              ")
    print("==========================================")
    print(f"Serveur maître : {sys.argv[1]}")
    print(f"Port maître : {sys.argv[2]}")
    print(f"Nombre de tâches max : {sys.argv[3]}")
    print(f"CPU max : {sys.argv[4]}")
    print("==========================================")

    serveur_maitre = sys.argv[1]
    port_maitre = int(sys.argv[2])
    nb_taches = int(sys.argv[3])
    cpu_max = int(sys.argv[4])

    server = Server(serveur_maitre, port_maitre, nb_taches, cpu_max)
    server.start()