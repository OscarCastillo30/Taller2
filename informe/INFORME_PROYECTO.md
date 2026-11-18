# Informe de avance — Taller 2

**Fecha de revisión:** 17 de noviembre de 2026  
**Alcance:** revisión documental y estática de los archivos presentes en el repositorio.

## 1. Resumen ejecutivo

El repositorio contiene un prototipo académico con ejemplos para cuatro áreas de sistemas distribuidos: comunicación síncrona con gRPC, mensajería asíncrona con RabbitMQ, ordenamiento de eventos con relojes de Lamport y coordinación de una Saga con una acción compensatoria.

Los componentes están representados por módulos Python y un contrato Protocol Buffers. Sin embargo, la presencia de estos ejemplos no acredita que el sistema completo se haya ejecutado en varias máquinas ni que sus integraciones estén verificadas. No se encontraron pruebas automatizadas, evidencias de ejecución, manifiestos de dependencias, configuración de Docker Compose ni configuración de base de datos. El estado debe considerarse **prototipo en desarrollo, con integración y validación pendientes**.

## 2. Arquitectura identificada

```text
Agentes / productores
  ├─ gRPC: reportes de métricas y solicitudes de asignación ──> coordinador
  └─ RabbitMQ: publicación de eventos y comandos ─────────────> colas
                                                               ├─ consumidores
                                                               └─ coordinador Lamport

Orquestador Saga ── RabbitMQ ──> comandos de reserva/proceso/compensación
```

El contrato gRPC está definido en [`config/telematica.proto`](../config/telematica.proto). El broker y el coordinador se referencian mediante valores configurados directamente en varios módulos; en el estado revisado no hay un archivo de configuración común para centralizar esos parámetros.

## 3. Avance por componente

### 3.1 Comunicación síncrona — gRPC

**Presente:** el `.proto` define el servicio `CoordinatorService`, con `ReportMetrics` y `RequestAllocation`, y los mensajes asociados. [`coordinador/coordinador.py`](../coordinador/coordinador.py) implementa un servidor de ejemplo; los módulos `agente.py` envían métricas y, en una variante, solicitan asignaciones.

**Alcance actual:** el servidor imprime los datos recibidos y devuelve respuestas predefinidas. La solicitud de asignación no realiza una asignación persistente o coordinada de recursos.

**Pendiente:** probar el flujo cliente-servidor entre procesos, definir instrucciones de ejecución reproducibles y alinear las rutas de importación de los módulos generados con el directorio desde el que se inicia cada programa.

### 3.2 Mensajería asíncrona — RabbitMQ

**Presente:** los módulos de productor declaran colas durables, publican mensajes persistentes y, en algunas variantes, habilitan confirmaciones y reintentos. Los consumidores usan ACK manual. Los ejemplos publican en `metrics`, `allocations` y `failover`.

**Alcance actual:** la deduplicación usa un conjunto en memoria. Por lo tanto, no es durable y no evita el reprocesamiento después de reiniciar un consumidor. Las variantes de consumidor y productor son ejemplos independientes, no una única ejecución integrada.

**Pendiente:** documentar y probar topología, credenciales, política de reintentos, reconexión y comportamiento frente a mensajes no válidos o fallos de procesamiento.

### 3.3 Ordenamiento Lamport

**Presente:** los productores de ejemplo incrementan un contador local y publican eventos con marcas lógicas. [`coordinador/coordinador_lamport.py`](../coordinador/coordinador_lamport.py) acumula mensajes y ordena el búfer por `(lamport_time, node_id)`.

**Alcance actual:** el ordenamiento es una demostración local aplicada a lotes de mensajes recibidos; no se observa persistencia del búfer ni un protocolo distribuido completo para establecer orden causal entre nodos.

**Pendiente:** añadir pruebas con eventos concurrentes, empates, reentregas y reinicios, y definir con precisión la propiedad de orden que debe cumplir el sistema.

### 3.4 Patrón Saga

**Presente:** [`coordinador/saga_orquestador.py`](../coordinador/saga_orquestador.py) envía comandos de reserva, procesamiento y compensación. [`Consumidor/consumidor_saga.py`](../Consumidor/consumidor_saga.py) muestra las acciones recibidas.

**Alcance actual:** el ejemplo activa explícitamente un fallo simulado en el paso de procesamiento para mostrar la compensación. Las acciones de negocio son mensajes de consola; no hay persistencia de estado o efectos transaccionales reales.

**Pendiente:** probar casos exitosos y fallidos, correlacionar comandos y resultados, y definir cómo se recupera una Saga si se reinicia un participante.

## 4. Inventario por carpeta

| Carpeta | Contenido identificado | Estado |
|---|---|---|
| [`agentes/`](../agentes/README.md) | README de orientación; las implementaciones están distribuidas en productor y consumidor. | Sin módulos propios. |
| [`productor/`](../productor/README.md) | `agente.py`, `productor.py`, `productor_broker.py`, `productor_lamport.py`. | Ejemplos de clientes gRPC y productores RabbitMQ. |
| [`Consumidor/`](../Consumidor/README.md) | `agente.py`, `consumidor.py`, `consumidor_broker.py`, `consumidor_saga.py`. | Ejemplos de cliente gRPC y consumidores RabbitMQ. |
| [`coordinador/`](../coordinador/README.md) | `coordinador.py`, `agente.py`, `coordinador_lamport.py`, `productor_lamport.py`, `saga_orquestador.py`. | Servidor y demostraciones; aún requieren integración y pruebas. |
| [`config/`](../config/README.md) | `.proto` y dos módulos gRPC generados. | Contrato y código generado presentes; dependencias no fijadas en un manifiesto. |
| [`pruebas/`](../pruebas/README.md) | README. | No se encontraron pruebas automatizadas. |
| [`evidencias/`](../evidencias/README.md) | README. | No se encontraron evidencias adjuntas. |
| [`logs/`](../logs/README.md) | README. | No se encontraron logs de ejecución. |
| [`scripts/`](../scripts/README.md) | README. | No se encontraron scripts de despliegue o automatización. |
| [`informe/`](./README.md) | README e informe detallado. | Documentación del estado y pendientes. |

## 5. Riesgos y limitaciones observables

1. **Configuración distribuida:** las direcciones del broker/coordinador están definidas en módulos diferentes. Esto dificulta cambiar de entorno sin modificar código.
2. **Credenciales y conexiones:** algunas variantes usan autenticación y otras crean conexiones sin credenciales explícitas. Se debe definir una configuración consistente y externa antes del despliegue.
3. **Importaciones gRPC:** las rutas usadas para importar los módulos generados varían entre scripts. Hay que fijar un punto de ejecución y verificarlo con una prueba de arranque.
4. **Deduplicación volátil:** los IDs procesados se guardan en memoria, no en almacenamiento persistente.
5. **Respuestas de ejemplo:** la asignación gRPC es simulada y la Saga no aplica cambios persistentes de negocio.
6. **Dependencias y operación:** no se encontró manifiesto de paquetes, guía de arranque funcional ni archivo de composición de infraestructura.
7. **Validación no acreditada:** no se encontraron suite automatizada, resultados de ejecución o capturas que demuestren funcionamiento conjunto.

## 6. Próximos pasos recomendados

1. Definir un archivo de dependencias con versiones compatibles de `grpcio`, `grpcio-tools`, `protobuf` y `pika`.
2. Centralizar host, puerto y opciones de conexión en variables de entorno o un mecanismo local de configuración; no guardar credenciales reales en el repositorio.
3. Normalizar los imports de los módulos generados y establecer comandos de inicio desde la raíz del proyecto.
4. Añadir pruebas unitarias para serialización, deduplicación y ordenamiento, además de pruebas de integración para RabbitMQ y gRPC.
5. Convertir la demostración Saga en un flujo verificable con respuestas de cada paso y estado observable; probar tanto éxito como compensación.
6. Documentar el despliegue de los servicios requeridos o aclarar explícitamente si se ejecutarán manualmente.
7. Guardar resultados reproducibles en [`pruebas/`](../pruebas/README.md) y evidencias sanitizadas en [`evidencias/`](../evidencias/README.md).

## 7. Criterio de avance

El avance principal consiste en contar con los contratos y ejemplos iniciales de los cuatro temas funcionales. El proyecto aún no puede considerarse integrado ni validado de extremo a extremo con la evidencia disponible. El siguiente hito recomendado es reproducir una ejecución mínima —coordinador gRPC, broker, productor y consumidor— y acompañarla de pruebas y evidencia.

## 8. Método y límites de esta revisión

Este informe describe archivos encontrados en el repositorio y el comportamiento visible en su código. No afirma que los servicios externos estén disponibles ni que los módulos hayan sido ejecutados durante esta revisión. Las carpetas locales de entorno virtual no forman parte del inventario funcional del proyecto.
