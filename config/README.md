# Configuración y contrato gRPC

Esta carpeta contiene el contrato Protocol Buffers y los módulos Python generados para implementar el cliente y servidor gRPC.

## Archivos

| Archivo | Función |
|---|---|
| [`telematica.proto`](./telematica.proto) | Define `CoordinatorService`, los métodos `ReportMetrics` y `RequestAllocation`, y sus mensajes de solicitud y respuesta. Es la fuente del contrato. |
| [`telematica_pb2.py`](./telematica_pb2.py) | Código generado por Protocol Buffers con las clases de mensajes y descriptores definidos en el `.proto`. No editar manualmente; regenerar desde el contrato. |
| [`telematica_pb2_grpc.py`](./telematica_pb2_grpc.py) | Código gRPC generado con los stubs de cliente y las interfaces de servidor para `CoordinatorService`. No editar manualmente; regenerar desde el contrato. |

## Contrato definido

- `ReportMetrics`: recibe nodo, marca de tiempo, uso de CPU/memoria y estado; devuelve confirmación y mensaje.
- `RequestAllocation`: recibe nodo, tipo y cantidad de recurso, además de una marca Lamport; devuelve el resultado, identificador y nodo asignado.

Los módulos generados dependen de las versiones de `protobuf` y `grpcio` usadas para generarlos. El repositorio no incluye actualmente un manifiesto de dependencias que fije dichas versiones.
