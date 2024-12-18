import sys
import os
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QCheckBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from server import Server


class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serveur Maître - Configuration")
        self.resize(700, 500)

        self.server = None
        self.local_mode = False

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.config_fields = {}
        self.init_config_fields(main_layout)

        self.start_stop_button = QPushButton("Démarrer le Serveur")
        self.start_stop_button.clicked.connect(self.toggle_server)
        main_layout.addWidget(self.start_stop_button)

        self.quit_button = QPushButton("Quitter l'Application")
        self.quit_button.clicked.connect(self.close)
        main_layout.addWidget(self.quit_button)

        main_layout.addWidget(QLabel("Liste des Serveurs Secondaires :", font=QFont("Arial", 12, QFont.Weight.Bold)))
        self.server_list = QListWidget()
        main_layout.addWidget(self.server_list)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_server_list)

    def init_config_fields(self, layout):
        fields = [
            ("Port Client", "4200"),
            ("Port Serveur", "5200"),
            ("Serveur Local", "True"),
            ("Nombre Serveurs Secondaires", "2"),
            ("Adresse IP Maitre", "127.0.0.1"),
            ("Nb Tâches Max", "10"),
            ("CPU Max", "10")
        ]

        self.labels = {}

        for label, default_value in fields:
            h_layout = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 10))
            self.labels[label] = lbl

            if label == "Serveur Local":
                self.local_toggle = QCheckBox("Activer")
                self.local_toggle.setChecked(default_value == "True")
                self.local_toggle.stateChanged.connect(self.toggle_local_mode)
                h_layout.addWidget(lbl)
                h_layout.addWidget(self.local_toggle)
            else:
                field = QLineEdit(default_value)
                self.config_fields[label] = field
                h_layout.addWidget(lbl)
                h_layout.addWidget(field)

                if label in ["Nombre Serveurs Secondaires", "Adresse IP Maitre", "Nb Tâches Max", "CPU Max"]:
                    lbl.setVisible(self.local_toggle.isChecked())
                    field.setVisible(self.local_toggle.isChecked())

            layout.addLayout(h_layout)

    def toggle_local_mode(self):
        self.local_mode = self.local_toggle.isChecked()
        for label in ["Nombre Serveurs Secondaires", "Adresse IP Maitre", "Nb Tâches Max", "CPU Max"]:
            self.config_fields[label].setVisible(self.local_mode)
            self.labels[label].setVisible(self.local_mode)

    def toggle_server(self):
        if self.server:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        try:
            port_client = int(self.config_fields["Port Client"].text())
            port_server = int(self.config_fields["Port Serveur"].text())
            local = self.local_toggle.isChecked()
            nb_servers = int(self.config_fields["Nombre Serveurs Secondaires"].text()) if local else 0
            ip_maitre = self.config_fields["Adresse IP Maitre"].text()
            nb_taches_max = int(self.config_fields["Nb Tâches Max"].text()) if local else 0
            cpu_max = int(self.config_fields["CPU Max"].text()) if local else 0

            self.server = Server(ip_maitre, nb_taches_max, cpu_max, port_client, port_server, str(local), nb_servers)
            threading.Thread(target=self.server.start).start()

            self.timer.start(1000)
            self.start_stop_button.setText("Arrêter le Serveur")
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur : {e}")

    def stop_server(self):
        if self.server:
            self.server.client_socket.close()
            self.server.server_socket.close()
            self.server = None

        self.timer.stop()
        self.server_list.clear()
        self.start_stop_button.setText("Démarrer le Serveur")

    def update_server_list(self):
        self.server_list.clear()
        if self.server and self.server.secondary_servers:
            for server in self.server.secondary_servers:
                server_id = server["id"]
                status = server["état"]
                self.server_list.addItem(f"🖥️ Serveur #{server_id} | État : {status.capitalize()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
    else:
        print(f"Le fichier style.qss est introuvable à : {qss_path}")

    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec())
