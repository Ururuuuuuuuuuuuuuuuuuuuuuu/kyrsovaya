import json
import sys
import requests
from functools import partial

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QLabel
from pymongo import MongoClient, DESCENDING

from MainWindow import Ui_MainDialog


def getAllEffects():
    mongo = MongoClient("mongodb+srv://sovyshka:ujdyfdnhzgjxre@cluster0.rpsi7sd.mongodb.net/")
    database = mongo["leddb"]
    collection = database["visualeffects"]

    document = collection.find("effect")

    return document


class MainWindowDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)

        self.printEffects()

    def printEffects(self):
        mongo = MongoClient("mongodb+srv://sovyshka:ujdyfdnhzgjxre@cluster0.rpsi7sd.mongodb.net/")
        database = mongo["leddb"]
        collection = database["visualeffects"]

        cursor = collection.find().sort("popularity", DESCENDING)

        row = 0
        col = 0

        for item in cursor:
            layout = QVBoxLayout()

            button = QPushButton(item.get('name'))
            button.setFixedSize(200, 30)
            button.setStyleSheet("background: #2B2D2F;\n"
                                 "color: #71DFBE;\n"
                                 "border-radius: 4px;\n"
                                 "font: bold 1.25rem/1 poppins;\n"
                                 )

            image_label = QLabel()
            pixmap = QMovie(f"gif/{item.get('image')}.gif")
            image_label.setMovie(pixmap)
            pixmap.start()

            layout.addWidget(image_label, alignment=Qt.AlignHCenter)
            layout.addWidget(button, alignment=Qt.AlignHCenter)

            widget = QWidget()
            widget.setLayout(layout)
            widget.setStyleSheet("QPushButton{border: 1px solid #71DFBE;}")
            layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

            self.ui.gridLayout.addWidget(widget, row, col)
            col += 1

            if col == 5:
                col = 0
                row += 1

            button.clicked.connect(partial(self.startEffect, item))

    def startEffect(self, item):
        import socket

        host = '192.168.0.78'
        port = 61024
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))

            data = json.dumps({"effect": item.get('effect')})

            client_socket.send(data.encode())
            client_socket.close()
            self.addPopularity(item)

        except Exception as e:
            print(e)

    def addPopularity(self, item):
        mongo = MongoClient("mongodb+srv://sovyshka:ujdyfdnhzgjxre@cluster0.rpsi7sd.mongodb.net/")
        database = mongo["leddb"]
        collection = database["visualeffects"]

        query = {"effect": item.get('effect')}
        document = collection.find_one(query)

        if document:
            new_popularity = document.get("popularity", 0) + 1
            collection.update_one(query,
                                  {"$set":
                                      {
                                          "popularity": new_popularity
                                      }
                                  })


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_dialog = MainWindowDialog()
    main_dialog.exec()
    sys.exit(app.exec_())
