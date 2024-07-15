# client/main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QTextEdit, QMessageBox
import socketio
import requests
from encryption import generate_keys, encrypt_message, decrypt_message

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.private_key, self.public_key = generate_keys()
        self.sio = socketio.Client()
        self.sio.on('message', self.receive_message)
        self.sio.connect('http://localhost:5000')

    def initUI(self):
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Chat App')

        self.label1 = QLabel('Username:', self)
        self.label1.move(10, 10)
        self.username = QLineEdit(self)
        self.username.move(100, 10)

        self.label2 = QLabel('Recipient:', self)
        self.label2.move(10, 40)
        self.recipient = QLineEdit(self)
        self.recipient.move(100, 40)

        self.label3 = QLabel('Message:', self)
        self.label3.move(10, 70)
        self.message = QLineEdit(self)
        self.message.move(100, 70)

        self.send_btn = QPushButton('Send', self)
        self.send_btn.move(10, 100)
        self.send_btn.clicked.connect(self.send_message)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.move(10, 140)
        self.chat_display.resize(380, 140)

    def send_message(self):
        recipient = self.recipient.text()
        message = self.message.text()
        
        response = requests.post('http://localhost:5000/get_public_key', json={'username': recipient})
        if response.json()['status'] == 'success':
            public_key = response.json()['public_key']
            encrypted_message = encrypt_message(message, public_key)
            self.sio.emit('message', {'recipient': recipient, 'message': encrypted_message})
            self.chat_display.append(f'You: {message}')
            self.message.clear()
        else:
            QMessageBox.information(self, 'Error', 'Recipient not found.')

    def receive_message(self, data):
        sender = data['sender']
        encrypted_message = data['message']
        message = decrypt_message(encrypted_message, self.private_key)
        self.chat_display.append(f'{sender}: {message}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApp()
    ex.show()
    sys.exit(app.exec_())
