import pika
import uuid
import json
import time

BROKER_IP = "100.74.54.112"
NODE_ID = "Agente-02"
lamport_clock = 0

def tick_lamport():
    global lamport_clock
    lamport_clock += 1
    return lamport_clock

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

def enviar_mensaje(cola, datos, mensaje_id=None, lamport_val=None):
    if mensaje_id is None:
        mensaje_id = str(uuid.uuid4())
    if lamport_val is None:
        lamport_val = tick_lamport()

    payload = {
        "message_id": mensaje_id,
        "lamport_timestamp": lamport_val,
        "node_id": NODE_ID,
        "data": datos
    }
    body = json.dumps(payload)

    for intento in range(1, 6):
        try:
            connection = conectar_broker()
            channel = connection.channel()

            # Confirmación de publicación del broker (Sección 3.2)
            channel.confirm_delivery()

            # Declarar la cola como durable
            channel.queue_declare(queue=cola, durable=True)

            # Publicar con persistencia
            channel.basic_publish(
                exchange='',
                routing_key=cola,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True
            )
            print(f"[PRODUCTOR] Mensaje {mensaje_id} confirmado en '{cola}' | Lamport={lamport_val}")
            connection.close()
            return mensaje_id

        except Exception as e:
            espera = 2 ** intento
            print(f"[REINTENTO {intento}/5] Broker desconectado ({type(e).__name__}). Reintentando en {espera}s...")
            time.sleep(espera)

    print("[ERROR CRÍTICO] No se pudo conectar al broker RabbitMQ tras 5 intentos.")
    return None

if __name__ == '__main__':
    # 1. Publicar en las tres colas requeridas en el taller
    mid = enviar_mensaje('metrics', {"node_id": NODE_ID, "cpu_usage": 45.2})
    enviar_mensaje('allocations', {"node_id": NODE_ID, "task_id": "TASK-101", "action": "reservar_recurso"})
    enviar_mensaje('failover', {"node_id": NODE_ID, "alert": "Nodo secundario detectado inactivo"})

    # 2. Reenviar el mismo message_id para validar idempotencia en el consumidor
    if mid:
        print("\n[PRUEBA IDEMPOTENCIA] Reenviando mensaje duplicado...")
        enviar_mensaje('metrics', {"node_id": NODE_ID, "cpu_usage": 45.2}, mensaje_id=mid)
