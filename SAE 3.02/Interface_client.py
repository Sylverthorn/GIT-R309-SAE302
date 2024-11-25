# import sys
from PyQt6.QtWidgets import *
from client import *
import threading

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
    
        
        self.bouton_quitter = QPushButton("quitter")
        


        layout.addWidget(self.servlabel, 0, 0)
        layout.addWidget(self.portlabel, 1, 0)
        

        layout.addWidget(self.Serveur, 0, 1)
        layout.addWidget(self.Port, 1, 1)

        layout.addWidget(self.bouton, 4, 0 ,1 , 2)
        layout.addWidget(self.text , 5, 0, 1, 2)


        layout.addWidget(self.bouton_quitter, 5, 0)
        



        self.bouton.clicked.connect(self.demarrage)

        self.bouton_quitter.clicked.connect(self.close)
            
        widget = QWidget()
            
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)



    def demarrage(self):
        texte = self.bouton.text()
        
        self.addr = self.Serveur.text()
        self.port = self.Port.text()
        
        
        client = Client(int(self.port) , self.addr)   


        if texte == 'Connexion':
            self.bouton.setText('Déconnexion')
            
            thread = threading.Thread(target=client.connect)
            thread.start()
        
        elif texte == 'Déconnexion':
            self.bouton.setText("Connexion")
            thread = threading.Thread(target=client.arret,)
            thread.start()


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

               

import os
import json
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