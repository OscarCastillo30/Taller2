import pika
import json

# Control de idempotencia en memoria
mensajes_procesados = set()

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        msg_id = payload.get("message_id")
        
        # Verificar duplicados (Idempotencia)
        if msg_id in mensajes_procesados:
            print(f"[DUPLICADO] El mensaje {msg_id} ya fue procesado. Ignorando...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"[CONSUMIDOR] Procesando mensaje ID: {msg_id}...")
        print(f"Datos recibidos: {payload.get('data')}")
        
        # Registrar como procesado
        mensajes_procesados.add(msg_id)
        
        # Confirmar recepción (ACK) solo después de procesar
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[ÉXITO] Mensaje {msg_id} procesado y confirmado.\n")

    except Exception as e:
        print(f"[ERROR] Falló el procesamiento: {e}")

def iniciar_consumidor(cola):
    broker_ip = "100.74.54.112"
    
    connection_params = pika.ConnectionParameters(host=broker_ip)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue=cola, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=cola, on_message_callback=callback)

    print(f"[*] Escuchando la cola '{cola}'. Presiona CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        iniciar_consumidor('metrics')
    except KeyboardInterrupt:
        print("\nConsumidor detenido.")
