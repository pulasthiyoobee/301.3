# client/ui.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QMessageBox
import requests

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 280, 150)
        self.setWindowTitle('Chat App')

        self.label1 = QLabel('Username:', self)
        self.label1.move(10, 10)
        self.username = QLineEdit(self)
        self.username.move(100, 10)

        self.label2 = QLabel('Password:', self)
        self.label2.move(10, 40)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.move(100, 40)

        self.register_btn = QPushButton('Register', self)
        self.register_btn.move(10, 80)
        self.register_btn.clicked.connect(self.register)

        self.login_btn = QPushButton('Login', self)
        self.login_btn.move(100, 80)
        self.login_btn.clicked.connect(self.login)

    def register(self):
        username = self.username.text()
        password = self.password.text()
        public_key = ""  # Generate or fetch public key
        response = requests.post('http://localhost:5000/register', json={'username': username, 'password': password, 'public_key': public_key})
        QMessageBox.information(self, 'Register', response.json()['message'])

    def login(self):
        username = self.username.text()
        password = self.password.text()
        response = requests.post('http://localhost:5000/login', json={'username': username, 'password': password})
        QMessageBox.information(self, 'Login', response.json()['message'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApp()
    ex.show()
    sys.exit(app.exec_())
