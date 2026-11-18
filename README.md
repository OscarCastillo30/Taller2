# Taller 2 — Sistemas Distribuidos

> **Guía principal del repositorio**
> Arquitectura, inventario de archivos y estado actual del proyecto, con enlaces directos a cada componente.

## Resumen ejecutivo

Este repositorio reúne un prototipo académico de un sistema distribuido con agentes, un coordinador y comunicación mediante gRPC y RabbitMQ. El código aborda cuatro temas: comunicación síncrona, mensajería asíncrona, ordenamiento de eventos con relojes de Lamport y una demostración del patrón Saga.

**Estado observado:** hay implementaciones de ejemplo para esos componentes, pero el repositorio todavía no contiene una configuración de despliegue integral ni pruebas automatizadas. Por ello, la documentación distingue entre lo que el código hace hoy y lo que sigue pendiente; no se presenta el proyecto como una solución ya validada de extremo a extremo.

## Navegación

| Área | Función | Documentación |
|---|---|---|
| [agentes/](./agentes/README.md) | Índice conceptual de los nodos agente; sus implementaciones están organizadas en productor y consumidor. | [README de agentes](./agentes/README.md) |
| [productor/](./productor/README.md) | Clientes que envían métricas, solicitudes y eventos al coordinador o al broker. | [README de productor](./productor/README.md) |
| [Consumidor/](./Consumidor/README.md) | Consumidores RabbitMQ y cliente gRPC de agente. | [README de consumidor](./Consumidor/README.md) |
| [coordinador/](./coordinador/README.md) | Servidor gRPC, procesamiento de mensajes y orquestación Saga de ejemplo. | [README de coordinador](./coordinador/README.md) |
| [config/](./config/README.md) | Contrato Protocol Buffers y módulos Python gRPC generados. | [README de configuración](./config/README.md) |
| [pruebas/](./pruebas/README.md) | Espacio previsto para pruebas y sus resultados. | [README de pruebas](./pruebas/README.md) |
| [evidencias/](./evidencias/README.md) | Espacio previsto para capturas y evidencias de ejecución. | [README de evidencias](./evidencias/README.md) |
| [logs/](./logs/README.md) | Espacio previsto para registros de ejecución. | [README de logs](./logs/README.md) |
| [scripts/](./scripts/README.md) | Espacio previsto para automatizaciones auxiliares. | [README de scripts](./scripts/README.md) |
| [informe/](./informe/README.md) | Documentación de avance. | [Informe detallado del proyecto](./informe/INFORME_PROYECTO.md) |

## Arquitectura y flujo actual

```text
Agente / productor ── gRPC ──> Coordinador
Agente / productor ── RabbitMQ ──> consumidor o coordinador
                                  ├─ métricas y eventos Lamport
                                  └─ comandos de la demostración Saga
```

- **gRPC:** el contrato define `ReportMetrics` y `RequestAllocation`. El servidor de ejemplo responde a ambos métodos.
- **RabbitMQ:** los productores publican mensajes persistentes en colas como `metrics`, `allocations` y `failover`; los consumidores confirman mensajes con ACK.
- **Lamport:** los ejemplos adjuntan marcas lógicas y el coordinador de eventos ordena un búfer por `(lamport_time, node_id)`.
- **Saga:** un orquestador de demostración envía comandos de reserva, procesamiento y compensación. El fallo del segundo paso está activado intencionalmente en el código de ejemplo.

## Inventario de archivos fuente

### Productor

- [productor/agente.py](./productor/agente.py): cliente gRPC que informa métricas y solicita asignaciones al coordinador.
- [productor/productor.py](./productor/productor.py): ejemplo de publicación RabbitMQ con ID de mensaje, confirmación de publicación, reintentos y reenvío de un ID para mostrar la detección de duplicados.
- [productor/productor_broker.py](./productor/productor_broker.py): variante de productor RabbitMQ con confirmación y publicación persistente.
- [productor/productor_lamport.py](./productor/productor_lamport.py): emite eventos con una marca lógica de Lamport.

### Consumidor

- [Consumidor/agente.py](./Consumidor/agente.py): cliente gRPC que reporta métricas con timeout y reintentos.
- [Consumidor/consumidor.py](./Consumidor/consumidor.py): consume una cola RabbitMQ, descarta duplicados en memoria y confirma mensajes procesados.
- [Consumidor/consumidor_broker.py](./Consumidor/consumidor_broker.py): variante de consumidor con ACK manual y control de duplicados en memoria.
- [Consumidor/consumidor_saga.py](./Consumidor/consumidor_saga.py): recibe comandos de ejemplo de Saga, incluidos los de compensación, desde `failover`.

### Coordinador

- [coordinador/coordinador.py](./coordinador/coordinador.py): servidor gRPC de ejemplo que atiende reportes de métricas y solicitudes de asignación.
- [coordinador/agente.py](./coordinador/agente.py): cliente gRPC de agente con reintentos; es una implementación auxiliar duplicada en esta carpeta.
- [coordinador/coordinador_lamport.py](./coordinador/coordinador_lamport.py): consume eventos, evita duplicados durante la ejecución y procesa el búfer ordenado por marca Lamport y nodo.
- [coordinador/productor_lamport.py](./coordinador/productor_lamport.py): publica eventos de ejemplo con marca de Lamport en RabbitMQ.
- [coordinador/saga_orquestador.py](./coordinador/saga_orquestador.py): orquesta los pasos de la demostración Saga y envía la compensación configurada.

### Contratos gRPC

- [config/telematica.proto](./config/telematica.proto): contrato de servicios y mensajes para métricas y asignaciones.
- [config/telematica_pb2.py](./config/telematica_pb2.py): clases Protocol Buffers generadas a partir del contrato.
- [config/telematica_pb2_grpc.py](./config/telematica_pb2_grpc.py): cliente y servidor gRPC generados a partir del contrato.

Los detalles de función y alcance de cada archivo están también en el README de su carpeta. La carpeta [agentes/](./agentes/README.md) documenta la organización conceptual y enlaza las implementaciones reales.

## Estado por tema

| Tema | Implementación presente | Alcance / pendiente |
|---|---|---|
| Comunicación síncrona | Cliente y servidor gRPC de ejemplo y contrato `.proto`. | Respuestas simuladas; falta validar el flujo entre procesos con una configuración reproducible. |
| Mensajería asíncrona | Publicación persistente, confirmación del productor, consumo y ACK manual. | La deduplicación del consumidor vive en memoria y no sobrevive al reinicio. |
| Orden causal | Ejemplos con reloj lógico y ordenamiento de eventos por `(marca, nodo)`. | Es una demostración basada en un búfer local; no es una implementación distribuida completa de orden causal. |
| Patrón Saga | Orquestador, comandos y consumidor demostrativos con acción compensatoria. | El fallo se fuerza en el ejemplo; no hay persistencia transaccional ni almacenamiento de estado. |

## Pendientes de integración y validación

1. Añadir instrucciones y configuración reproducible para instalar dependencias y ejecutar cada proceso.
2. Unificar la configuración de direcciones del broker/coordinador y evitar valores de entorno incrustados en el código; usar variables de entorno o configuración local excluida del repositorio.
3. Revisar la consistencia de las rutas de importación de los módulos gRPC generados y definir desde qué directorio se ejecuta cada módulo.
4. Añadir pruebas automatizadas para el contrato gRPC, publicación/consumo, deduplicación, ordenamiento y compensación Saga.
5. Incorporar evidencias de ejecución y, si el alcance lo exige, persistencia real para deduplicación y estado de Saga.
6. Definir el despliegue de infraestructura. En el inventario actual no se encontraron archivos Docker Compose, manifiestos de servicios ni configuración de base de datos.

Las carpetas [pruebas/](./pruebas/README.md), [evidencias/](./evidencias/README.md), [logs/](./logs/README.md) y [scripts/](./scripts/README.md) contienen por ahora su documentación, no implementaciones adicionales. Para el análisis ampliado y sus observaciones, consulta el [informe detallado](./informe/INFORME_PROYECTO.md).

## Alcance de esta documentación

La descripción se basa en los archivos presentes en el repositorio. La existencia de un ejemplo no implica que haya sido ejecutado ni validado en una red distribuida. Las direcciones y opciones de conexión deben revisarse antes de ejecutar el código en otro entorno.
