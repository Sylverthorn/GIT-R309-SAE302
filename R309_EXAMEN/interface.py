#  https://github.com/Sylverthorn/EXAM_R309.git


import sys
from PyQt6.QtWidgets import *



import socket
import threading
import time

class Server:
    def __init__(self, port,Nbclients , hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts
        self.nbclient =  Nbclients
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.boucle = True

    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server connecté sur le port: " + str(self.port))

    def __reconnexion(self):
        self.__connect()

    def __envoi_message(self, message, client=None):
        try:
            client.send(message.encode())
        except ConnectionResetError:
            print("Client déconnecté.")
            self.boucle = False
            self.__reconnexion()

    def __recois(self, client=None):
        while self.boucle:
            try:
                message = client.recv(1024).decode()
                if message:
                    print(f"Message de client :", message)
                    
                    
                    réponse = "Bien reçu !"
                    threading.Thread(target=self.__envoi_message, args=(réponse, client,)).start()

                if message.lower() == "arret":
                    print("Déconnexion demandée par le client...")
                    
                    self.boucle = False
                    self.server_socket.close()
                    time.sleep(1)
                    break
                if message.lower() == "deco-server":
                    print(f"Déconnexion du client : {client}")
                    client.close()
                    break
                    

            except ConnectionResetError:
                print("Client déconnecté.")
                self.boucle = False
                client.close()
                break

    

    def accept(self):
        while self.boucle:
            try :
                client, address = self.server_socket.accept()
                print("Connexion client : " + str(address))
                
                client_thread = threading.Thread(target=self.__recois, args=(client,))
                client_thread.start()
            except OSError:
                print("Server arrêté.")
                break

    def start(self):
        self.__connect()
        self.accept()

    def arret(self):
        self.boucle = False

        self.server_socket.close()
        time.sleep(1)
        print("arret du serveur")





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        


        self.setWindowTitle("Conversion de temperature")
        self.setGeometry(200, 200, 500, 300)


        layout = QGridLayout()
        
        
        self.Serveur = QLineEdit("127.0.0.1")
        self.Port = QLineEdit("4200")
        self.Nbclients = QLineEdit('5')

        self.servlabel = QLabel("Serveur : ")
        self.portlabel = QLabel("Port : ")
        self.clientlabel = QLabel("Serveur : ")


        self.bouton = QPushButton("Demarrage du Serveur")
        self.text = QTextEdit(enabled=False)
    
        
        self.bouton_quitter = QPushButton("quitter")
        self.aide = QPushButton("?")

        self.addr = self.Serveur.text()
        self.port = self.Port.text()
        self.clients = self.Nbclients.text()

        layout.addWidget(self.servlabel, 0, 0)
        layout.addWidget(self.portlabel, 1, 0)
        layout.addWidget(self.clientlabel, 2, 0)

        layout.addWidget(self.Serveur, 0, 1)
        layout.addWidget(self.Port, 1, 1)
        layout.addWidget(self.Nbclients, 2, 1)
        layout.addWidget(self.text , 4, 1)


        
        layout.addWidget(self.bouton, 3, 1)



        layout.addWidget(self.bouton_quitter, 5, 1)
        



        self.bouton.clicked.connect(self.demarrage)
        self.aide.clicked.connect(self.dialog)
        self.bouton_quitter.clicked.connect(self.close)
            
        widget = QWidget()
            
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def dialog(self):
        QMessageBox.about(self, "Aide", "Ce programme permet de convertir une température en °C en °K et vice versa")

    def demarrage(self):
        texte = self.bouton.text()
        
        self.addr = self.Serveur.text()
        self.port = self.Port.text()
        self.clients = self.Nbclients.text()
        
        server =Server(int(self.port), int(self.clients) , self.addr)   

        if texte == 'Demarrage du Serveur':
            self.bouton.setText('Arreter le Serveur')
            
            servthread = threading.Thread(target=server.start,)
            servthread.start()
        
        elif texte == 'Arreter le Serveur':
            self.bouton.setText("Demarrage du Serveur")
            servthread = threading.Thread(target=server.arret,)
            servthread.start()


    
               


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())