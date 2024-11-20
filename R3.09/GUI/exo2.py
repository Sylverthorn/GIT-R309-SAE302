import sys
from PyQt6.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        


        self.setWindowTitle("Conversion de temperature")
        self.setGeometry(200, 200, 500, 300)


        layout = QGridLayout()
        
        layout.addWidget(QLabel("Temperature : "), 0, 0)
        self.text = QLineEdit()
        self.resultat = QLineEdit(enabled=False)
        self.label = QLabel("Conversion : ")
        self.bouton = QPushButton("convertir")
        self.celsius = QLabel("°C")
        self.kelvin = QLabel("°K")
        
        self.bouton_quitter = QPushButton("quitter")
        self.aide = QPushButton("?")
        self.combo = QComboBox(self)
        self.combo.addItem("°C --> °K")
        self.combo.addItem("°K --> °C")



        layout.addWidget(self.text, 0, 1)
        layout.addWidget(self.celsius, 0, 2)

        layout.addWidget(self.bouton, 1, 1)
        layout.addWidget(self.combo, 1, 2)

        layout.addWidget(self.label, 2, 0)
        layout.addWidget(self.resultat, 2, 1)
        layout.addWidget(self.kelvin, 2, 2)


        layout.addWidget(self.bouton_quitter, 4, 0)
        layout.addWidget(self.aide, 4, 2)


        self.combo.activated.connect(self.combobox)
        self.bouton.clicked.connect(self.convertir)
        self.bouton_quitter.clicked.connect(self.close)
        self.aide.clicked.connect(self.dialog)
        self.text.returnPressed.connect(self.bouton.click)
            
        widget = QWidget()
            
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def dialog(self):
        QMessageBox.about(self, "Aide", "Ce programme permet de convertir une température en °C en °K et vice versa")

    def combobox(self):
        if self.combo.currentText() == "°C --> °K":
            self.celsius.setText("°C")
            self.kelvin.setText("°K")
        else:
            self.celsius.setText("°K")
            self.kelvin.setText("°C")

    def convertir(self):
                if self.combo.currentText() == "°C --> °K":
                    try:
                        temp = float(self.text.text())
                        if temp < -273.15:
                            self.resultat.setText("Erreur: température inférieure à -273.15°C")
                            QMessageBox.about(self, "ERREUR", "température inférieure à -273.15°C")
                        else:
                            temp = temp + 273.15
                            self.resultat.setText(str(temp))
                    except ValueError:
                        self.resultat.setText("Erreur: température invalide") 
                        QMessageBox.about(self, "ERREUR", "température invalide")    

                else:
                    try:
                        temp = float(self.text.text())
                        if temp < 0:
                            self.resultat.setText("Erreur: température inférieure à 0°K")
                            QMessageBox.about(self, "ERREUR", "température inférieure à 0°K")  
                        else:
                            temp = temp - 273.15
                            self.resultat.setText(str(temp))
                    except ValueError:
                        self.resultat.setText("Erreur: température invalide")  
                        QMessageBox.about(self, "ERREUR", "température invalide")  
                



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())