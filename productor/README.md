# Productor

Esta carpeta contiene ejemplos de nodos que originan solicitudes o eventos del sistema. Algunas variantes usan gRPC para comunicarse con el coordinador y otras publican mensajes en RabbitMQ.

## Archivos

| Archivo | Función |
|---|---|
| [`agente.py`](./agente.py) | Cliente gRPC de agente: reporta métricas y solicita asignaciones al coordinador. Incluye reintentos para el reporte de métricas. |
| [`productor.py`](./productor.py) | Publica ejemplos en las colas `metrics`, `allocations` y `failover`. Incluye ID de mensaje, confirmación de publicación, mensajes persistentes y un reenvío para probar duplicados. |
| [`productor_broker.py`](./productor_broker.py) | Variante de productor RabbitMQ con cola durable, confirmación del broker, mensajes persistentes y reintentos. |
| [`productor_lamport.py`](./productor_lamport.py) | Publica eventos con una marca lógica de Lamport que incrementa localmente. |

## Consideraciones

Los scripts son ejemplos independientes y contienen parámetros de conexión definidos en el código. Antes de ejecutarlos, verifica la dirección del broker/coordinador, las credenciales aplicables y las rutas de importación gRPC. No se incluye aquí una configuración de despliegue ni una prueba automatizada.
