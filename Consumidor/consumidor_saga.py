import pika
import json

def callback_saga(ch, method, properties, body):
    try:
        mensaje = json.loads(body)
        accion = mensaje.get("accion")
        payload = mensaje.get("payload")
        cola_origen = method.routing_key

        print(f"\n[CONSUMIDOR SAGA] Mensaje recibido en cola '{cola_origen}':")
        print(f" -> Acción solicitada: {accion}")
        print(f" -> Datos (Payload): {payload}")

        # Lógica de reacción según la acción de la Saga
        if accion == "RESERVAR_RECURSO":
            print(f"   [ACCIÓN] Reservando recursos para la tarea {payload.get('task_id')}...")
            # Aquí pondrías la lógica real de tu base de datos o estado local

        elif accion == "PROCESAR_TAREA":
            print(f"   [ACCIÓN] Procesando tarea {payload.get('task_id')}...")
            # Aquí simulas el procesamiento que puede salir bien o mal

        elif accion == "COMPENSAR_RESERVA":
            print(f"   [¡ROLLBACK!] Ejecutando compensación. Revirtiendo reserva para {payload.get('task_id')}...")
            print(f"   [¡ROLLBACK!] Motivo: {payload.get('motivo')}")
            # Aquí liberas los recursos que habías reservado en el Paso 1

        # Confirmar el mensaje al broker
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[ÉXITO] Comando de saga procesado y confirmado.\n")

    except Exception as e:
        print(f"[ERROR] Falló el procesamiento del comando Saga: {e}")

def iniciar_consumidor_saga():
    # IP de Tailscale del broker (PC1)
    broker_ip = "100.74.54.112"
    
    connection_params = pika.ConnectionParameters(host=broker_ip)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Declarar las colas que utiliza el Patrón Saga
    colas = ['allocations', 'metrics', 'failover']
    for cola in colas:
        channel.queue_declare(queue=cola, durable=True)

    channel.basic_qos(prefetch_count=1)

    # Nota: Para este ejemplo didáctico, escucharemos la cola 'failover' donde llegan las compensaciones,
    # o puedes replicar la estructura para cada cola. Aquí escucharemos 'failover' como demostración del rollback.
    cola_a_escuchar = 'failover'
    channel.basic_consume(queue=cola_a_escuchar, on_message_callback=callback_saga)

    print(f"[*] Consumidor Saga escuchando la cola de compensaciones/fallos ('{cola_a_escuchar}')... Presiona CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        iniciar_consumidor_saga()
    except KeyboardInterrupt:
        print("\nConsumidor Saga detenido.")
