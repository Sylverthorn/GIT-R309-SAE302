import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor
from client import *
import threading
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        


        self.setWindowTitle("Conversion de temperature")
        self.setGeometry(200, 200, 500, 500)


        layout = QGridLayout()
        

        self.Serveur = QLineEdit("127.0.0.1")
        self.Port = QLineEdit("4200")

        self.servlabel = QLabel("Serveur : ")
        self.portlabel = QLabel("Port : ")
       

        self.bouton = QPushButton("Connexion")
        self.text = QTextEdit()
        self.bouton_envoyer = QPushButton("Envoyer")
    
        
        self.bouton_quitter = QPushButton("quitter")

        self.text_log = QTextEdit(readOnly=True)
        self.text_log.setPlaceholderText("Logs...")
        self.text_log.setFixedHeight(100)
        self.text_log.verticalScrollBar().setValue(self.text_log.verticalScrollBar().maximum())
        


        self.addr = self.Serveur.text()
        self.por = self.Port.text()
        self.client = Client(int(self.por) , self.addr) 

        
                # Redirection des prints vers QTextEdit
        self.redirect_stdout(self.text_log)



        layout.addWidget(self.servlabel, 0, 0)
        layout.addWidget(self.portlabel, 1, 0)
        

        layout.addWidget(self.Serveur, 0, 1)
        layout.addWidget(self.Port, 1, 1)

        layout.addWidget(self.bouton, 4, 0 ,1 , 2)
        layout.addWidget(self.text , 5, 0, 1, 2)


        layout.addWidget(self.bouton_quitter, 6, 0)
        layout.addWidget(self.bouton_envoyer, 6, 1)

        layout.addWidget(self.text_log, 7, 0, 1, 2)
    

        threading.Thread(target=self.state).start()

        self.bouton.clicked.connect(self.thread_demarrage)
        self.bouton_quitter.clicked.connect(self.ferme)
        self.bouton_envoyer.clicked.connect(self.envoyer_message)
            
        widget = QWidget()
            
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def ferme(self):
        threading.Thread(target=self.client.quitter).start()
        super().close()
        os._exit(0)

    def demarrage(self):
    
        if self.client.state == 'shutdown':
            self.bouton.setText('Déconnexion')
            self.client.connect()
        
        elif self.client.state == 'running':
            self.bouton.setText("Connexion")
            self.client.arret()

    def envoyer_message(self):
        message = self.text.toPlainText()
        self.client.envoi(message)
        self.text.clear()


    def thread_demarrage(self):
        thread = threading.Thread(target=self.demarrage)
        thread.start()


    def  state(self):
        while True:
            if self.client.state == 'shutdown':
                self.bouton.setText('Connexion')
            elif self.client.state == 'running':
                self.bouton.setText('Déconnexion')
            time.sleep(1)

    def redirect_stdout(self, text_edit):
        """Redirige sys.stdout pour écrire dans le QTextEdit."""
        def write_to_text_edit(text):
            print_sans_n = text.replace("\n", "").strip()  # Retirer les sauts de ligne
            if print_sans_n:  # Si le texte n'est pas vide
                text_edit.append(print_sans_n)  # Ajouter le texte à QTextEdit
                text_edit.moveCursor(QTextCursor.MoveOperation.End)  # Déplacer le curseur à la fin
                text_edit.ensureCursorVisible()  # S'assurer que le curseur est visible

        sys.stdout.write = write_to_text_edit

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

    window = MainWindow()
    window.show()
    app.exec()