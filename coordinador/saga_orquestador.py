import pika
import json
import time

class SagaOrquestador:
    def __init__(self):
        self.broker_ip = "100.74.54.112"  # IP de Tailscale del broker (PC1)

    def enviar_comando(self, cola, accion, payload):
        """Envía un paso de la saga o una compensación a RabbitMQ."""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.broker_ip))
            channel = connection.channel()
            channel.queue_declare(queue=cola, durable=True)

            mensaje = {
                "accion": accion,
                "payload": payload
            }
            
            channel.basic_publish(
                exchange='',
                routing_key=cola,
                body=json.dumps(mensaje),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"[SAGA ORQUESTADOR] Enviado a '{cola}' -> Acción: {accion}")
            connection.close()
            return True
        except Exception as e:
            print(f"[ERROR SAGA] Falló la comunicación con el broker: {e}")
            return False

    def ejecutar_saga(self, task_id):
        print(f"\n=== INICIANDO TRANSACCIÓN DISTRIBUIDA (SAGA) para: {task_id} ===")
        
        # --- PASO 1: Reservar Recursos ---
        print("Paso 1: Intentando reservar recursos...")
        exito_paso1 = self.enviar_comando('allocations', 'RESERVAR_RECURSO', {"task_id": task_id})
        
        if not exito_paso1:
            print("[FALLO] El Paso 1 no pudo comunicarse. Abortando Saga.")
            return

        # Simulamos un tiempo de procesamiento local
        time.sleep(1)

        # --- PASO 2: Procesar Tarea / Validar ---
        print("Paso 2: Procesando la tarea en el nodo de procesamiento...")
        exito_paso2 = self.enviar_comando('metrics', 'PROCESAR_TAREA', {"task_id": task_id})
        
        # Simulamos un fallo intencional en el Paso 2 para demostrar la compensación
        simular_fallo = True  # Cambia a False si quieres que la saga sea exitosa

        if simular_fallo:
            print("\n[¡ALERTA!] Falló el Paso 2. Iniciando compensaciones (Rollback lógico)...")
            
            # --- COMPENSACIÓN: Revertir Paso 1 ---
            print("Compensación: Liberando el recurso previamente reservado...")
            self.enviar_comando('failover', 'COMPENSAR_RESERVA', {"task_id": task_id, "motivo": "Fallo en Paso 2"})
            print("=== SAGA FALLIDA Y COMPENSADA EXITOSAMENTE ===")
        else:
            print("Paso 2 exitoso. Transacción completada con éxito (Commit).")
            print("=== SAGA COMPLETADA ===")

if __name__ == '__main__':
    orquestador = SagaOrquestador()
    # Ejecutamos la saga de prueba
    orquestador.ejecutar_saga("TASK-999")
