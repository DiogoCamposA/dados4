from flask import Flask, render_template
import paho.mqtt.client as mqtt
import sqlite3

app = Flask(__name__)

# Configurações MQTT
MQTT_BROKER_HOST = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "MQTTINCBTempUmidDiogo"

# Variável global para armazenar a última mensagem do tópico
last_message = ""

# Configuração do banco de dados SQLite
DB_NAME = "mqtt_data.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            payload TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_message(topic, payload):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (topic, payload) VALUES (?, ?)
    ''', (topic, payload))
    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global last_message
    last_message = msg.payload.decode()
    print("Mensagem recebida do tópico {}: {}".format(MQTT_TOPIC, last_message))
    
    # Inserir a mensagem no banco de dados
    insert_message(MQTT_TOPIC, last_message)

# Configurar o cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Criar a tabela no banco de dados (se ainda não existir)
create_table()

# Iniciar a thread do cliente MQTT
mqtt_client.loop_start()

# Rota principal que renderiza a última mensagem do tópico
@app.route('/')
def index():
    # Obter a última mensagem do banco de dados
    message_from_db = get_messages()
    return render_template('index.html', message=message_from_db)

if __name__ == '__main__':
    app.run(debug=True)

