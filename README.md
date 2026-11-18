# 🚀 Taller 2 — Integración, Mensajería y Transacciones
**Asignatura:** Sistemas Distribuidos Modernos  
**Docente:** Msc. Ing. Óscar Gabriel Espejo Mojica  
**Institución:** Ingeniería en Telemática  
**Versión:** 1.0 — Octubre 2026  

---

## 📋 Descripción General del Proyecto
Este repositorio contiene la solución completa para el **Taller 2** de Sistemas Distribuidos Modernos. El propósito principal es integrar los diferentes componentes del sistema distribuido:
1. **Comunicación síncrona** entre agentes y el coordinador.
2. **Mensajería asíncrona** mediante un broker (RabbitMQ).
3. **Orden causal** de eventos utilizando Relojes de Lamport.
4. **Asignación transaccional robusta** implementando el **Patrón Saga** con compensaciones automáticas.

El sistema está diseñado para ejecutarse de manera distribuida utilizando **máquinas virtuales / WSL (Debian/Ubuntu)** interconectadas mediante **Tailscale**, y se empaqueta completamente utilizando **Docker** y **Docker Compose**.

---

## 🛠️ Arquitectura del Sistema

```text
[ Agente 1 (Portátil 2) ] --(gRPC / REST)--> [ Coordinador (Portátil 1) ]
[ Agente 2 (Portátil 3) ] --(Asíncrono)-----> [ Broker RabbitMQ ] 
                                                   │
                                                   ▼
                                            [ Base de Datos PostgreSQL ]
```

### Componentes Principales:
* **Coordinador:** Gestiona el estado global, procesa métricas, coordina el orden causal de eventos y maneja las transacciones distribuidas.
* **Agentes:** Nodos de borde encargados de monitorear recursos y reportar métricas periódicamente de forma síncrona y asíncrona.
* **Broker (RabbitMQ):** Sistema de colas de mensajes desacoplado para tópicos clave (`metrics`, `allocations`, `failover`).
* **Base de Datos (PostgreSQL):** Almacenamiento persistente para el inventario replicado y el registro de estados de las Sagas.

---

## ⚙️ Requisitos del Entorno

* **Sistema Operativo:** Debian 13 o Ubuntu Server 26.04.1 LTS (o entorno WSL en desarrollo).
* **Virtualización de Red:** Tailscale configurado para la comunicación mallada entre los portátiles del equipo.
* **Contenedorización:** Docker y Docker Compose instalados en cada nodo.
* **Recursos:** Mínimo 2 GB de RAM para agentes/coordinador y 3 GB para el broker y base de datos.

---

## 🚀 Guía de Despliegue Rápido

Sigue estos pasos para clonar y levantar el sistema completo en tu entorno de desarrollo o máquina virtual:

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/taller2-telematica.git
cd taller2-telematica
```

### 2. Configurar variables de entorno (Opcional / Valores por defecto)
Verifica los archivos de configuración en cada subcarpeta si requieres cambiar IPs de Tailscale o credenciales.

### 3. Levantar la infraestructura base y servicios con Docker Compose
```bash
docker compose up --build -d
```

### 4. Verificar el estado de los contenedores
```bash
docker compose ps
```

---

## 🔍 Requisitos Funcionales Implementados

- **3.1 Comunicación Síncrona:** Definición de contratos y llamadas con control de tiempo límite (*timeouts*) y reintentos con espera creciente (*exponential backoff*).
- **3.2 Mensajería Asíncrona:** Publicación y consumo con confirmaciones de entrega y mecanismos de idempotencia basados en identificadores únicos de mensajes.
- **3.3 Orden Causal (Relojes de Lamport):** Inclusión de marcas lógicas en los eventos procesados y ordenamiento estricto por el par $(\text{marca de Lamport}, \text{ID de nodo})$.
- **3.4 Patrón Saga (Transacciones Distribuidas):** Flujo de 3 pasos (Reserva $\rightarrow$ Replicación $\rightarrow$ Confirmación) dotado de lógica de compensación automática ante fallos en la persistencia.

---

## 👥 Bitácora de Autoevaluación del Equipo

| Integrante | Rol / Componente Principal | Autoevaluación y Comentarios |
| :--- | :--- | :--- |
| **Integrante 1** | Coordinador & Base de Datos | *Diseño del orquestador y configuración de la persistencia replicada.* |
| **Integrante 2** | Agentes & Comunicación Síncrona | *Implementación de clientes gRPC/REST y reintentos ante fallos.* |
| **Integrante 3** | Broker & Patrón Saga | *Configuración de colas en RabbitMQ y transacciones con compensación.* |

---

## 📚 Referencias
* Garcia-Molina, H., & Salem, K. (1987). *Sagas*. ACM SIGMOD.
* Lamport, L. (1978). *Time, Clocks, and the Ordering of Events in a Distributed System*. Communications of the ACM.
* Documentación Oficial de RabbitMQ, Docker y gRPC.