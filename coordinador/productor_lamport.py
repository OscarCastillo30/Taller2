import pika
import uuid
import json

# Reloj lógico de Lamport local del nodo
lamport_clock = 0
NODE_ID = "Agente-Node-02"  # Cambia este ID según el computador (ej: Agente-Node-01, Agente-Node-02)

def enviar_evento_lamport(cola, datos):
    global lamport_clock
    # 1. Incrementar el reloj lógico local antes de un evento propio
    lamport_clock += 1
    
    broker_ip = "100.74.54.112"  # IP de Tailscale del broker (PC1)
    
    try:
        connection_params = pika.ConnectionParameters(host=broker_ip)
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=cola, durable=True)

        mensaje_id = str(uuid.uuid4())
        payload = {
            "message_id": mensaje_id,
            "node_id": NODE_ID,
            "lamport_time": lamport_clock,  # Valor actual del reloj de Lamport
            "data": datos
        }

        body = json.dumps(payload)

        channel.basic_publish(
            exchange='',
            routing_key=cola,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistente
            )
        )
        print(f"[PRODUCTOR {NODE_ID}] Enviado -> Lamport Time: {lamport_clock} (ID: {mensaje_id[:8]})")
        connection.close()

    except Exception as e:
        print(f"[ERROR] No se pudo enviar el mensaje: {e}")

if __name__ == '__main__':
    # Simular el envío de un evento hacia la cola 'metrics'
    enviar_evento_lamport('metrics', {"cpu_load": 65.4})
