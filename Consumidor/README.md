# Consumidor

Esta carpeta agrupa ejemplos de recepción de mensajes de RabbitMQ y un cliente gRPC de agente. Los consumidores usan ACK manual para confirmar la recepción después de procesar el mensaje.

## Archivos

| Archivo | Función |
|---|---|
| [`agente.py`](./agente.py) | Cliente gRPC que informa métricas al coordinador, con timeout y hasta cinco intentos de conexión. |
| [`consumidor.py`](./consumidor.py) | Escucha una cola RabbitMQ elegida por el punto de entrada; procesa el contenido y descarta IDs ya vistos durante la ejecución. |
| [`consumidor_broker.py`](./consumidor_broker.py) | Variante del consumidor RabbitMQ que permite seleccionar la cola y aplica ACK manual y deduplicación en memoria. |
| [`consumidor_saga.py`](./consumidor_saga.py) | Escucha la cola `failover` y muestra las acciones de Saga recibidas, incluida la compensación de una reserva. |

## Consideraciones

El conjunto de IDs procesados se mantiene únicamente en memoria y se pierde al reiniciar el proceso. Los consumidores de ejemplo conectan con una dirección definida en el código. Configura el broker y valida el comportamiento de reentrega antes de usar estos ejemplos en un entorno real.
