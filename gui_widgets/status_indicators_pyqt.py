import sys
import json
import paho.mqtt.client as paho
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt

statuses = ['Found Button', 'Pressed Button', 'Found Flag', 'Captured Flag']

class CircleIndicator(QWidget):
    def __init__(self, parent=None):
        super(CircleIndicator, self).__init__(parent)
        self.color = QColor('red')  # Default color

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setBrush(QBrush(self.color))
        qp.setRenderHint(QPainter.Antialiasing)
        qp.drawEllipse(0, 0, self.width()-1, self.height()-1)

    def set_color(self, color):
        self.color = QColor(color)
        self.update()  # Redraw the widget with new color

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 300, 700, 500)
        self.setWindowTitle('Circular Status Indicators')

        main_layout = QVBoxLayout()

        self.indicators = []

        for status in statuses:
            # Create a horizontal layout for each indicator and label
            h_layout = QHBoxLayout()

            indicator = CircleIndicator(self)
            indicator.setFixedSize(100, 100)  # Set fixed size for circle
            label = QLabel(status)
            label.setFixedWidth(300) 
            button = QPushButton('Send ' + status + ' Signal')
            button.setFixedWidth(300)
            button.clicked.connect(lambda _, s=status: publish_message({s: True}))

            h_layout.addWidget(indicator)
            h_layout.addWidget(label)  # Add label next to the circle
            h_layout.addWidget(button)  # Add button next to the label

            main_layout.addLayout(h_layout)
            self.indicators.append(indicator)

        self.setLayout(main_layout)
        self.show()

        # Example of setting colors
        self.indicators[0].set_color('red')
        self.indicators[1].set_color('red')
        self.indicators[2].set_color('red')
        self.indicators[3].set_color('red')

def publish_message(signal):
    msg = client.publish("team1/group1", json.dumps(signal), 1)
    msg.wait_for_publish(1)

def message_handling(client, userdata, msg:paho.MQTTMessage):
    payload = json.loads(msg.payload)
    for i, status in enumerate(statuses):
        if status in payload:
            if payload[status]:
                ex.indicators[i].set_color('green')
            else:
                ex.indicators[i].set_color('red')
    print("Message received -- ", payload)

def client_disconnected(client, userdata, rc):
    client.loop_stop()
    print(f"Disconnected with result code: {rc}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 18pt;} QPushButton{font-size: 14pt;}")
    ex = MainWindow()
    
    client = paho.Client(paho.CallbackAPIVersion.VERSION2)
    client.on_message = message_handling
    client.on_disconnect = client_disconnected
    
    if client.connect("127.0.0.1", 1883, 60) != 0:
        print("Couldn't connect to the mqtt broker")
        sys.exit(1)
    
    try:
        client.loop_start()   
        client.subscribe("team1/group1", 1)    
        print("Press CTRL+C to exit...") 
    except Exception as e:
        print(e) 
    
    sys.exit(app.exec_())
