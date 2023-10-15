from flask import Flask, render_template
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Configurações MQTT
MQTT_BROKER_HOST = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "MQTTINCBTempUmidDiogo"

# Variável global para armazenar a última mensagem do tópico
last_message = ""

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global last_message
    last_message = msg.payload.decode()
    print("Mensagem recebida do tópico {}: {}".format(MQTT_TOPIC, last_message))

# Configurar o cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Iniciar a thread do cliente MQTT
mqtt_client.loop_start()

# Rota principal que renderiza a última mensagem do tópico
@app.route('/')
def index():
    return render_template('index.html', message=last_message)

if __name__ == '__main__':
    app.run(debug=True)
