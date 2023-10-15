from flask import Flask, render_template
import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configurações MQTT
MQTT_BROKER_HOST = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "MQTTINCBTempUmidDiogo"

# Configuração do banco de dados SQLite
DB_NAME = "mqtt_data.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Criar nova tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            payload TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Copiar dados da tabela antiga para a nova
    cursor.execute('INSERT INTO messages_new (topic, payload) SELECT topic, payload FROM messages')
    
    # Remover a tabela antiga
    cursor.execute('DROP TABLE IF EXISTS messages')
    
    # Renomear a nova tabela para o nome desejado
    cursor.execute('ALTER TABLE messages_new RENAME TO messages')
    
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
    cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC')
    result = cursor.fetchall()
    conn.close()
    return result

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    # Armazena cada mensagem no banco de dados com carimbo de data/hora
    insert_message(msg.topic, msg.payload.decode())
    print("Mensagem recebida do tópico {}: {}".format(msg.topic, msg.payload.decode()))

# Configurar o cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Criar a tabela no banco de dados (se ainda não existir)
create_table()

# Iniciar a thread do cliente MQTT
mqtt_client.loop_start()

# Rota principal que renderiza todas as mensagens do tópico
@app.route('/')
def index():
    # Obter todas as mensagens do banco de dados
    messages_from_db = get_messages()
    return render_template('index.html', messages=messages_from_db)

if __name__ == '__main__':
    app.run(debug=True)

