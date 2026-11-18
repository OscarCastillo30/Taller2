import pika
import json

# Memoria local para control de idempotencia (evitar procesar duplicados)
mensajes_procesados = set()

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        msg_id = payload.get("message_id")
        
        # 1. Control de Idempotencia
        if msg_id in mensajes_procesados:
            print(f"[DUPLICADO] El mensaje {msg_id} ya fue procesado. Descartando...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"[CONSUMIDOR] Procesando mensaje ID: {msg_id}...")
        
        # --- LÓGICA DE PROCESAMIENTO ---
        print(f"   -> Datos recibidos: {payload.get('data')}")
        
        # Registrar como procesado
        mensajes_procesados.add(msg_id)
        
        # 2. Confirmación de recepción (ACK) SOLO después de procesar
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[ÉXITO] Mensaje {msg_id} procesado y confirmado al broker.\n")

    except Exception as e:
        print(f"[ERROR] Falló el procesamiento del mensaje: {e}")

def iniciar_consumidor(cola):
    broker_ip = "100.74.54.112" # IP de Tailscale del broker (PC1)
    
    connection_params = pika.ConnectionParameters(host=broker_ip)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue=cola, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=cola, on_message_callback=callback)

    print(f"[*] Escuchando la cola '{cola}' en el broker {broker_ip}. Presiona CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    # Puedes cambiar aquí la cola que deseas escuchar ('metrics', 'allocations' o 'failover')
    COLA_A_ESCUCHAR = 'metrics'
    
    try:
        iniciar_consumidor(COLA_A_ESCUCHAR)
    except KeyboardInterrupt:
        print("\nConsumidor detenido.")
