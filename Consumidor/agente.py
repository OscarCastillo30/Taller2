import time
import grpc
import config.telematica_pb2 as telematica_pb2
import config.telematica_pb2_grpc as telematica_pb2_grpc

def report_metrics_with_retry(coordinator_ip, node_id):
    target = f"{coordinator_ip}:50051"
    
    # Parámetros de reintento y timeout
    max_retries = 5
    base_backoff = 2  # segundos iniciales de espera
    timeout_seconds = 3 # tiempo límite por cada intento

    print(f"[AGENTE] Conectando al coordinador en {target}...")

    for attempt in range(1, max_retries + 1):
        try:
            # Establece el canal de comunicación gRPC
            with grpc.insecure_channel(target) as channel:
                stub = telematica_pb2_grpc.CoordinatorServiceStub(channel)
                
                # Construir el mensaje de métricas
                request = telematica_pb2.MetricsReportRequest(
                    node_id=node_id,
                    timestamp=int(time.time()),
                    cpu_usage=45.5,
                    memory_usage=60.2,
                    status="OK"
                )

                print(f"[Intento {attempt}] Enviando métricas al coordinador...")
                
                # Llamada gRPC aplicando el timeout configurado
                response = stub.ReportMetrics(request, timeout=timeout_seconds)
                
                print(f"[ÉXITO] Respuesta del coordinador: {response.message}")
                return response

        except grpc.RpcError as e:
            # Captura errores de conexión, expiración de timeout, etc.
            print(f"[ADVERTENCIA] Fallo en la comunicación (Código {e.code()}: {e.details()})")
            
            if attempt == max_retries:
                print("[ERROR CRÍTICO] Se agotaron todos los reintentos. El coordinador no responde.")
                raise
            
            # Cálculo de espera creciente (backoff exponencial: 2s, 4s, 8s, 16s...)
            sleep_time = base_backoff ** attempt
            print(f"Reintentando en {sleep_time} segundos...\n")
            time.sleep(sleep_time)

if __name__ == '__main__':
    # Reemplaza esta IP con la dirección de Tailscale del computador que actúa como Coordinador
    COORDINATOR_TAILSCALE_IP = "100.74.54.112" 
    NODE_ID = "Agente-Node-02"
    
    # Simular el reporte periódico
    try:
        report_metrics_with_retry(COORDINATOR_TAILSCALE_IP, NODE_ID)
    except Exception as e:
        print("No se pudo completar el reporte de métricas.")
