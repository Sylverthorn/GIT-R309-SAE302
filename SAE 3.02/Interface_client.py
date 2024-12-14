import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QTextCursor, QFont
from client import *
import threading
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.nom_fichier = None
        self.client = Client() 

        self.setWindowTitle("CLient")
        self.setGeometry(200, 200, 800, 400)

        # Widgets pour le premier grid
        self.servlabel = QLabel("Serveur : ")
        self.Serveur = QLineEdit("127.0.0.1")
        self.portlabel = QLabel("Port : ")
        self.Port = QLineEdit("4200")
        self.bouton = QPushButton("Connexion")
        self.fichier = QPushButton("Fichier")
        self.text = QTextEdit()
        self.bouton_envoyer = QPushButton("Envoyer")
        self.bouton_quitter = QPushButton("Quitter")

        # Widgets pour le deuxième grid
        self.resutat = QTextEdit(readOnly=True)
        self.text_log = QTextEdit(readOnly=True)
        self.text_log.setPlaceholderText("Logs...")
        self.text_log.setFixedHeight(100)
        

        # Premier grid layout
        grid_left = QGridLayout()
        grid_left.addWidget(self.servlabel, 0, 0)
        grid_left.addWidget(self.Serveur, 0, 1)
        grid_left.addWidget(self.portlabel, 1, 0)
        grid_left.addWidget(self.Port, 1, 1)
        grid_left.addWidget(self.bouton, 2, 0, 1, 2)
        grid_left.addWidget(self.fichier, 3, 0, 1, 2)
        grid_left.addWidget(self.text, 4, 0, 1, 2)
        grid_left.addWidget(self.bouton_envoyer, 5, 1)
        grid_left.addWidget(self.bouton_quitter, 5, 0)

        # Deuxième grid layout
        grid_right = QGridLayout()
        grid_right.addWidget(self.resutat, 0, 0, 4, 1)
        grid_right.addWidget(self.text_log, 4, 0)
        
        # Layout principal pour aligner les deux grids
        main_layout = QHBoxLayout()
        main_layout.addLayout(grid_left)
        main_layout.addLayout(grid_right)

        

        
        threading.Thread(target=self.state).start()
        threading.Thread(target=self.redirect_stdout).start()
        threading.Thread(target=self.resultat).start()

        self.bouton.clicked.connect(self.thread_demarrage)
        self.bouton_quitter.clicked.connect(self.ferme)
        self.bouton_envoyer.clicked.connect(self.envoyer_message)
        self.fichier.clicked.connect(self.choisir_fichier)


        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)


    def ferme(self):
        threading.Thread(target=self.client.quitter).start()
        super().close()
        os._exit(0)

    def demarrage(self):
    
        if self.client.state == 'shutdown':
            self.bouton.setText('Déconnexion')
            self.client.connect()

            self.text.setReadOnly(False)
            self.bouton_envoyer.setEnabled(True)
            
        
        elif self.client.state == 'running':
            self.bouton.setText("Connexion")
            self.client.arret()

            self.text.setReadOnly(True)
            self.bouton_envoyer.setEnabled(False)
            

    def envoyer_message(self):
        if self.nom_fichier:
            with open(self.nom_fichier, 'w', encoding='utf-8') as file:
                file.write(self.text.toPlainText())
        message = self.text.toPlainText()
        if self.nom_fichier:
            fichier = self.nom_fichier.split('/')[-1]
            self.client.envoi(fichier + "|" + message)
        else:
            self.client.envoi(message)

        self.text.clear()
        self.nom_fichier = None


    def thread_demarrage(self):
        self.addr = self.Serveur.text()
        self.por = self.Port.text()
        self.client.host = self.addr
        self.client.port = int(self.por)
        thread = threading.Thread(target=self.demarrage)
        thread.start()


    def  state(self):
        while True:
            if self.client.state == 'shutdown':
                self.bouton.setText("Connexion")
                self.text.setReadOnly(True)
                self.text.setPlaceholderText("Veuillez vous connecter au serveur pour commencer.")

                self.bouton_envoyer.setEnabled(False)
                self.bouton_envoyer.setStyleSheet("background-color: grey;")

                self.fichier.setEnabled(False)
                self.fichier.setStyleSheet("background-color: grey;")
                


            elif self.client.state == 'running':
                self.bouton.setText('Déconnexion')
                self.text.setReadOnly(False)
                self.text.setPlaceholderText("")
                self.bouton_envoyer.setEnabled(True)
                self.bouton_envoyer.setStyleSheet("")

                self.fichier.setEnabled(True)
                self.fichier.setStyleSheet("")
                
                

            time.sleep(1)

    def choisir_fichier(self):
        
        options = QFileDialog.Option.ReadOnly  
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un fichier",             
            "",                                
            
            options=options
        )
        if file_name and os.path.isfile(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as file:  
                    self.text.setPlainText(file.read()) 
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier : {e}")
        else:
            print("Aucun fichier sélectionné ou le chemin sélectionné est un dossier.")
        
        self.nom_fichier = file_name


    def redirect_stdout(self):
        """Redirige sys.stdout pour écrire dans le QTextEdit."""
        def write_to_text_edit(text):
            print_sans_n = text.replace("\n", "").strip()  # Retirer les sauts de ligne
            if print_sans_n:  # Si le texte n'est pas vide
                self.text_log.append(print_sans_n)  # Ajouter le texte à QTextEdit
                self.text_log.moveCursor(QTextCursor.MoveOperation.End)  # Déplacer le curseur à la fin
                self.text_log.ensureCursorVisible()  # S'assurer que le curseur est visible

        sys.stdout.write = write_to_text_edit

    def resultat(self):
        try:
            while True:
                if self.client.resultat:
                    self.resutat.append(self.client.resultat)
                    
                    self.resutat.ensureCursorVisible()
                    self.client.resultat = None
        except Exception:            
            pass

    def closeEvent(self, event):
        self.client.quitter()
        QApplication.quit()
        event.accept()
'''
    def load_servers(self):
        try:
            with open("servers.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_servers(self, servers):
        with open("servers.json", "w") as file:
            json.dump(servers, file, indent=4)

    def add_server(self, addr, port):
        servers = self.load_servers()
        servers.append({"addr": addr, "port": port})
        self.save_servers(servers)

    def remove_server(self, addr, port):
        servers = self.load_servers()
        servers = [server for server in servers if server["addr"] != addr or server["port"] != port]
        self.save_servers(servers)
'''
               


if __name__ == "__main__":
    app = QApplication([])

    # Chargement du style
    qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
    else:
        print(f"Le fichier style.qss est introuvable à : {qss_path}")

    # Set a valid font family
    app.setFont(QFont("Sans Serif", 10))
    window = MainWindow()
    window.show()
    app.exec()