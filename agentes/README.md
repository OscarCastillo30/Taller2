# Agentes

Esta carpeta funciona como punto de entrada documental para los nodos que participan en el sistema. Las implementaciones de ejemplo están separadas por función: el envío de solicitudes y eventos se encuentra principalmente en [`productor/`](../productor/README.md), mientras que la recepción de mensajes y otro cliente gRPC están en [`Consumidor/`](../Consumidor/README.md).

## Organización de las implementaciones

- **Comunicación gRPC:** clientes de agente en [`productor/agente.py`](../productor/agente.py) y [`Consumidor/agente.py`](../Consumidor/agente.py).
- **Publicación RabbitMQ:** ejemplos de productor en [`productor/`](../productor/README.md).
- **Recepción RabbitMQ:** consumidores en [`Consumidor/`](../Consumidor/README.md).

No hay módulos Python directamente en esta carpeta por ahora. Este README mantiene visible el área de agentes y explica dónde consultar sus implementaciones actuales.
