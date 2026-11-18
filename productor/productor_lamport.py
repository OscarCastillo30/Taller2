import pika
import uuid
import json
import time

# Reloj lógico de Lamport local del nodo
lamport_clock = 0
NODE_ID = "Agente-Node-02"
BROKER_IP = "100.74.54.112"

def conectar_broker():
    try:
        creds = pika.PlainCredentials("admin", "admin")
        params = pika.ConnectionParameters(
            host=BROKER_IP,
            credentials=creds,
            connection_attempts=1,
            socket_timeout=3
        )
        return pika.BlockingConnection(params)
    except pika.exceptions.ProbableAuthenticationError:
        params = pika.ConnectionParameters(
            host=BROKER_IP,
            connection_attempts=1,
            socket_timeout=3
        )
        return pika.BlockingConnection(params)

def enviar_evento_lamport(cola, datos):
    global lamport_clock
    # 1. Incrementar el reloj lógico local antes de un evento propio
    lamport_clock += 1

    mensaje_id = str(uuid.uuid4())
    payload = {
        "message_id": mensaje_id,
        "node_id": NODE_ID,
        "lamport_time": lamport_clock,  # Valor actual del reloj de Lamport
        "data": datos
    }
    body = json.dumps(payload)

    for intento in range(1, 6):
        try:
            connection = conectar_broker()
            channel = connection.channel()
            channel.confirm_delivery()
            channel.queue_declare(queue=cola, durable=True)

            channel.basic_publish(
                exchange='',
                routing_key=cola,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True
            )
            print(f"[PRODUCTOR {NODE_ID}] Enviado -> Lamport Time: {lamport_clock} (ID: {mensaje_id[:8]})")
            connection.close()
            return True

        except Exception as e:
            espera = 2 ** intento
            print(f"[REINTENTO {intento}/5] Broker no disponible ({type(e).__name__}). Reintentando en {espera}s...")
            time.sleep(espera)

    print(f"[ERROR] No se pudo enviar el mensaje Lamport={lamport_clock}")
    return False

if __name__ == '__main__':
    # Simular 3 eventos concurrentes desde Agente-Node-02 hacia la cola 'metrics'
    for carga in [65.4, 71.2, 58.9]:
        enviar_evento_lamport('metrics', {"cpu_load": carga})
        time.sleep(0.5)
