import pika
import json

# Buffer para acumular mensajes y ordenarlos causalmente
buffer_mensajes = []
mensajes_procesados = set()

def procesar_buffer_ordenado():
    global buffer_mensajes
    if not buffer_mensajes:
        return

    # ORDENAMIENTO POR TUPLA REQUERIDO: (lamport_time, node_id)
    buffer_mensajes.sort(key=lambda x: (x["lamport_time"], x["node_id"]))

    print("\n--- [COORDINADOR] Procesando buffer ordenado causalmente ---")
    for msg in buffer_mensajes:
        print(f" -> Procesado: Nodo [{msg['node_id']}] | Lamport Time: [{msg['lamport_time']}] | ID: {msg['message_id'][:8]}")
        print(f"    Contenido: {msg['data']}")
    
    # Vaciar el búfer tras el procesamiento
    buffer_mensajes = []
    print("-----------------------------------------------------------\n")

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        msg_id = payload.get("message_id")
        
        # Idempotencia
        if msg_id in mensajes_procesados:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Agregar al búfer de ordenamiento
        buffer_mensajes.append(payload)
        mensajes_procesados.add(msg_id)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

        # Cuando acumulamos 3 o más mensajes, disparamos el ordenamiento y procesamiento
        if len(buffer_mensajes) >= 3:
            procesar_buffer_ordenado()

    except Exception as e:
        print(f"[ERROR] En callback: {e}")

def iniciar_coordinador(cola):
    broker_ip = "100.74.54.112" # IP de Tailscale del broker (PC1)
    
    connection_params = pika.ConnectionParameters(host=broker_ip)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue=cola, durable=True)
    channel.basic_qos(prefetch_count=5)
    channel.basic_consume(queue=cola, on_message_callback=callback)

    print(f"[*] Coordinador escuchando la cola '{cola}' para orden de Lamport. Presiona CTRL+C para salir.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        procesar_buffer_ordenado()
        print("\nCoordinador detenido.")

if __name__ == '__main__':
    iniciar_coordinador('metrics')
