import json
import sys
import requests
from functools import partial

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QPushButton

from MainWindow import Ui_MainDialog


class MainWindowDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)

        self.getAllEffects()

    def getAllEffects(self):
        url = "http://localhost:8080/api/getalleffects"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            row = 0
            col = 0

            for item in data:
                button = QPushButton(item["effectName"])
                self.ui.gridLayout.addWidget(button, row, col)
                col += 1

                if col == 5:
                    col = 0
                    row += 1

                button.clicked.connect(partial(self.startEffect, item))
        else:
            print("Ошибка при выполнении запроса. Статус код:", response.status_code)

    def startEffect(self, item):
        import socket

        host = '192.168.0.78'
        port = 61024
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))

            data = json.dumps({"effect": item["effect"]})

            client_socket.send(data.encode())
            self.addPopularity(item)
            client_socket.close()
        except Exception as e:
            print(e)

    def addPopularity(self, item):
        effectName = item["effect"]
        url = f"http://localhost:8080/api/increasepopularity/{effectName}"
        requests.get(url)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_dialog = MainWindowDialog()
    main_dialog.exec()
    sys.exit(app.exec_())
