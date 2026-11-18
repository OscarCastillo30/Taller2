# Coordinador

Esta carpeta contiene el servidor gRPC de ejemplo, utilidades de agente y las demostraciones de ordenamiento Lamport y orquestación Saga.

## Archivos

| Archivo | Función |
|---|---|
| [`coordinador.py`](./coordinador.py) | Inicia el servidor gRPC en el puerto `50051`. Atiende reportes de métricas y solicitudes de asignación con respuestas de ejemplo. |
| [`agente.py`](./agente.py) | Cliente gRPC auxiliar que reporta métricas con reintentos. Cumple un rol de agente, aunque está guardado junto al coordinador. |
| [`coordinador_lamport.py`](./coordinador_lamport.py) | Consume eventos RabbitMQ, evita procesar IDs repetidos durante la ejecución y ordena el búfer por `(lamport_time, node_id)`. |
| [`productor_lamport.py`](./productor_lamport.py) | Productor de eventos de ejemplo con reloj lógico de Lamport. |
| [`saga_orquestador.py`](./saga_orquestador.py) | Orquesta los comandos de reserva, procesamiento y compensación de la demostración Saga. El ejemplo configura intencionalmente un fallo en el segundo paso. |

## Consideraciones

El ordenamiento de Lamport opera sobre un búfer local de mensajes recibidos; no constituye por sí solo un protocolo distribuido completo. La Saga es demostrativa: los efectos de negocio y el estado transaccional persistente no están implementados. Verifica las rutas de importación y la configuración del broker antes de ejecutar los módulos.
