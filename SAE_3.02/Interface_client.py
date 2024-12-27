import sys
import os
import time
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QTextCursor, QFont
from client import *


class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str)

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

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # Connexions des boutons
        self.bouton.clicked.connect(self.thread_demarrage)
        self.bouton_quitter.clicked.connect(self.ferme)
        self.bouton_envoyer.clicked.connect(self.envoyer_message)
        self.fichier.clicked.connect(self.choisir_fichier)

        # Signaux
        self.log_signal.connect(self.log_message)
        self.result_signal.connect(self.update_results)

        # Démarrage des threads
        self.state_thread = threading.Thread(target=self.monitor_state, daemon=True)
        self.result_thread = threading.Thread(target=self.monitor_results, daemon=True)
        self.state_thread.start()
        self.result_thread.start()

    def ferme(self):
        self.client.quitter()
        QApplication.quit()

    def demarrage(self):
        try:
            if self.client.state == 'shutdown':
                self.client.connect()
            elif self.client.state == 'running':
                self.client.arret()
        except Exception as e:
            self.log_signal.emit(f"Erreur lors du démarrage : {e}")

    def envoyer_message(self):
        try:
            if self.nom_fichier:
                with open(self.nom_fichier, 'w', encoding='utf-8') as file:
                    file.write(self.text.toPlainText())

            message = self.text.toPlainText()
            if self.nom_fichier:
                fichier = os.path.basename(self.nom_fichier)
                self.client.envoi(f"script|{fichier}|{message}")
            else:
                self.client.envoi(message)

            self.text.clear()
            self.nom_fichier = None
        except Exception as e:
            self.log_signal.emit(f"Erreur lors de l'envoi du message : {e}")

    def thread_demarrage(self):
        self.client.host = self.Serveur.text()
        self.client.port = int(self.Port.text())
        threading.Thread(target=self.demarrage, daemon=True).start()

    def monitor_state(self):
        while True:
            state = self.client.state
            if state == 'shutdown':
                self.bouton.setText("Connexion")
                self.text.setReadOnly(True)
                self.bouton_envoyer.setEnabled(False)
                self.fichier.setEnabled(False)
            elif state == 'running':
                self.bouton.setText("Déconnexion")
                self.text.setReadOnly(False)
                self.bouton_envoyer.setEnabled(True)
                self.fichier.setEnabled(True)
            time.sleep(1)

    def monitor_results(self):
        while True:
            if self.client.resultat:
                self.result_signal.emit(self.client.resultat)
                self.client.resultat = None
            time.sleep(0.5)

    def choisir_fichier(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier", "", "Tous les fichiers (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.text.setPlainText(file.read())
                self.nom_fichier = file_name
            except Exception as e:
                self.log_signal.emit(f"Erreur lors de la lecture du fichier : {e}")

    def log_message(self, message):
        self.text_log.append(message)
        self.text_log.moveCursor(QTextCursor.MoveOperation.End)

    def update_results(self, result):
        self.resutat.append(result)
        self.resutat.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, event):
        self.ferme()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as style_file:
            app.setStyleSheet(style_file.read())

    app.setFont(QFont("Sans Serif", 10))
    window = MainWindow()
    window.show()
    app.exec()
