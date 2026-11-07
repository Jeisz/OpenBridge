# Ideas de integración: validación

Corridas: ideas-validacion-gemini-v4-r1.json, ideas-validacion-gemini-v4-r2.json. Referencia: `ai/eval/ideas_reference.json` (15 repos).

## Criterios

| Criterio | Corrida 1 | Corrida 2 |
|---|---|---|
| Requeridas encontradas (≥ 13) | 13/16 ✅ | 13/16 ✅ |
| Repos que debían quedar sin ideas | 3/3 ✅ | 3/3 ✅ |
| Repos por encima de su tope | 0 ✅ | 0 ✅ |
| Ideas prohibidas | 1 ❌ | 1 ❌ |

**Estabilidad** (mismos tipos en todas las corridas, ≥ 12): 12/15 ✅
Cambian entre corridas: duckdb/duckdb, prometheus/alertmanager, jaegertracing/jaeger

### Corrida 1

- Ideas: 16 (con snippet: 7)
- Descartadas por el código: ninguna
- Prohibidas: fastapi/fastapi · Desplegar una API web REST con FastAPI: tipo prohibido (rest_api)
- Fuera de la referencia (revisar): traefik/traefik · rest_api · Consultar la API REST de Traefik

### Corrida 2

- Ideas: 15 (con snippet: 7)
- Descartadas por el código: {'la cita no está en la entrada': 1}
- Prohibidas: fastapi/fastapi · Desplegar una API web de alto rendimiento: tipo prohibido (rest_api)
- Fuera de la referencia (revisar): traefik/traefik · rest_api · Consultar la API REST de Traefik

## Por repo (revisión manual)

Para cada idea: ¿el tipo y el resumen son coherentes con la cita? ¿Los disparadores aportan o son relleno? ¿El enlace lleva a la sección correcta?

### ollama/ollama

Requeridas: rest_api, sdk, docker · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[docker · medium] Desplegar Ollama con Docker**
  - Resumen: Ejecuta Ollama como un contenedor aislado en tu infraestructura usando la imagen oficial para servir modelos locales a tu aplicación.
  - Cita: «The official Ollama Docker image `ollama/ollama` is available on Docker Hub.»
  - Stack: Docker · Dependencias: Docker instalado y corriendo · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#docker
- **[sdk · medium] Usar el SDK de Ollama en Python**
  - Resumen: Instala el paquete cliente en Python para enviar mensajes a los modelos locales e integrar respuestas de inteligencia artificial en tu código.
  - Cita: «pip install ollama»
  - Stack: Python · Dependencias: Paquete ollama de Python, Servicio Ollama corriendo · Disparadores: Solicitud de procesamiento de lenguaje
  - Snippet (python): `from ollama import chat`
  - Documentación: https://github.com/ollama/ollama#python
- **[rest_api · high] Integrar la REST API de Ollama**
  - Resumen: Conecta tu aplicación con Ollama llamando directamente a sus endpoints HTTP para ejecutar y gestionar modelos de lenguaje.
  - Cita: «Ollama has a REST API for running and managing models.»
  - Stack: HTTP · Dependencias: Servicio Ollama corriendo · Disparadores: Mensaje del usuario en el chat
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#rest-api

**Corrida 2**
- **[docker · medium] Desplegar Ollama con Docker**
  - Resumen: Ejecuta Ollama como un contenedor en la infraestructura de la aplicación para gestionar modelos locales de IA.
  - Cita: «The official Ollama Docker image `ollama/ollama` is available on Docker Hub.»
  - Stack: Docker · Dependencias: Docker corriendo · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#docker
- **[rest_api · high] Integrar la REST API para gestionar y ejecutar modelos**
  - Resumen: Conecta la aplicación con la API HTTP de Ollama para enviar peticiones de chat y generar respuestas con modelos de IA.
  - Cita: «Ollama has a REST API for running and managing models.»
  - Stack: HTTP · Dependencias: Ollama corriendo localmente · Disparadores: Mensaje del usuario en el chat
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#rest-api
- **[sdk · high] Usar el SDK para chatear con modelos**
  - Resumen: Instala el paquete oficial en la aplicación para interactuar programáticamente con los modelos de IA mediante código.
  - Cita: «- ollama-python»
  - Stack: Python, JavaScript · Dependencias: Paquete ollama, Ollama corriendo localmente · Disparadores: Mensaje del usuario en el chat
  - Snippet (python): `from ollama import chat`
  - Documentación: https://github.com/ollama/ollama#libraries

### redis/redis

Requeridas: docker, sdk · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[docker · low] Desplegar Redis con Docker**
  - Resumen: Ejecuta una instancia de Redis como contenedor en tu entorno de desarrollo o producción usando la imagen oficial.
  - Cita: «docker run -d -p 6379:6379 redis:latest»
  - Stack: Docker, Alpine, Debian · Dependencias: Docker corriendo · Disparadores: —
  - Snippet (sh): `  docker run -d -p 6379:6379 redis:latest`
  - Documentación: https://github.com/redis/redis#getting-started
- **[sdk · medium] Conectar la aplicación con Redis usando librerías cliente**
  - Resumen: Integra Redis en tu aplicación utilizando librerías oficiales o recomendadas para lenguajes como Python, Go, C#, JavaScript o Java.
  - Cita: «Using Redis with client libraries»
  - Stack: Python, Go, JavaScript, Java · Dependencias: Servidor Redis accesible, Librería cliente instalada · Disparadores: Guardar datos en caché, Consultar sesiones de usuario
  - Snippet (—): `—`
  - Documentación: https://github.com/redis/redis#table-of-contents

**Corrida 2**
- **[docker · low] Desplegar Redis con Docker**
  - Resumen: Ejecuta una instancia de Redis como contenedor en tu entorno de desarrollo o producción usando la imagen oficial de Docker.
  - Cita: «docker run -d -p 6379:6379 redis:latest»
  - Stack: Docker · Dependencias: Docker instalado en el sistema · Disparadores: —
  - Snippet (sh): `  docker run -d -p 6379:6379 redis:latest`
  - Documentación: https://github.com/redis/redis#getting-started
- **[sdk · medium] Conectar la aplicación usando SDK**
  - Resumen: Integra Redis en tu aplicación instalando una librería cliente oficial para lenguajes como Python, C#/.NET, Go, JavaScript o Java.
  - Cita: «- Python (redis-py)»
  - Stack: Python, C#, Go, JavaScript, Java · Dependencias: Servidor Redis en ejecución · Disparadores: Inicio de sesión del usuario, Lectura de caché en la aplicación
  - Snippet (—): `—`
  - Documentación: https://github.com/redis/redis#redis-starter-projects

### duckdb/duckdb

Requeridas: sdk · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[sdk · medium] Usar DuckDB en la aplicación**
  - Resumen: Conecta la aplicación a DuckDB instalando los clientes oficiales para consultar datos analíticos directamente en proceso mediante SQL.
  - Cita: «DuckDB is available as a standalone CLI application and has clients for Python, R, Java, Rust, Go, Wasm, and many more, with deep integrations with packages such as pandas.»
  - Stack: Python, R, Java, Rust, Go, Wasm · Dependencias: — · Disparadores: Consulta analítica de datos en la aplicación
  - Snippet (—): `—`
  - Documentación: https://github.com/duckdb/duckdb#duckdb

**Corrida 2**
- Sin ideas
- Descartada (la cita no está en la entrada): [sdk] Consultar datos con DuckDB en tu aplicación

### pgvector/pgvector

Requeridas: sdk · Admisibles: docker · Prohibidas: —

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### hashicorp/vault

Requeridas: sdk · Admisibles: — · Prohibidas: —
Nota: Las pruebas con Docker y el git config son para quien desarrolla Vault.

**Corrida 1**
- **[sdk · medium] Usar las librerías API y SDK en la aplicación**
  - Resumen: Conecta tu aplicación con Vault usando sus librerías cliente en Go para acceder de forma segura a secretos, gestionar cifrado y renovar leases dinámicos.
  - Cita: «This repository publishes two libraries that may be imported by other projects: `github.com/hashicorp/vault/api` and `github.com/hashicorp/vault/sdk`.»
  - Stack: Go · Dependencias: Vault servidor en ejecución, Claves de acceso o token · Disparadores: Arranque de la aplicación, Petición de un secreto o credencial
  - Snippet (—): `—`
  - Documentación: https://github.com/hashicorp/vault#importing-vault

**Corrida 2**
- **[sdk · medium] Usar la API de Vault para acceder a secretos**
  - Resumen: Importa la librería para acceder a secretos de forma segura, generar secretos dinámicos, cifrar datos y renovar leases desde tu código.
  - Cita: «This repository publishes two libraries that may be imported by other projects: `github.com/hashicorp/vault/api` and `github.com/hashicorp/vault/sdk`.»
  - Stack: Go · Dependencias: Instancia de Vault corriendo, Credenciales o token de acceso · Disparadores: Inicio de la aplicación, Conexión a una base de datos externa
  - Snippet (—): `—`
  - Documentación: https://github.com/hashicorp/vault#importing-vault

### fastapi/fastapi

Requeridas: sdk · Admisibles: — · Prohibidas: webhook, rest_api
Nota: FastAPI sirve para construir tu propia API; no expone una a la que conectarse.

**Corrida 1**
- **[rest_api · medium] Desplegar una API web REST con FastAPI**
  - Resumen: Implementa un servidor web rápido basado en Python y tipos estándar para exponer endpoints REST y documentación interactiva automática.
  - Cita: «FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.»
  - Stack: Python, Uvicorn, Pydantic · Dependencias: Python, FastAPI · Disparadores: Petición HTTP entrante, Consulta de parámetros de ruta o consulta
  - Snippet (python): `from fastapi import FastAPI`
  - Documentación: https://fastapi.tiangolo.com/

**Corrida 2**
- **[rest_api · medium] Desplegar una API web de alto rendimiento**
  - Resumen: Expón endpoints HTTP y documentación interactiva automática en tu aplicación usando FastAPI para procesar peticiones y devolver respuestas en formato JSON.
  - Cita: «FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.»
  - Stack: Python, Starlette, Pydantic · Dependencias: Python instalado · Disparadores: Petición HTTP entrante en la API
  - Snippet (python): `from fastapi import FastAPI`
  - Documentación: https://fastapi.tiangolo.com/

### grafana/grafana

Requeridas: ninguna · Admisibles: — · Prohibidas: webhook · Tope: 0
Nota: Nombra notificaciones a otros sistemas sin decir el mecanismo.

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### BurntSushi/ripgrep

Requeridas: ninguna · Admisibles: — · Prohibidas: sdk · Tope: 0
Nota: Herramienta de línea de comandos; la instalación es solo un enlace.

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### opensearch-project/OpenSearch

Requeridas: ninguna · Admisibles: — · Prohibidas: — · Tope: 0
Nota: Sin código ni instrucciones de uso.

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### apache/kafka

Requeridas: docker · Admisibles: — · Prohibidas: sdk, rest_api · Tope: 1
Nota: El resto del README es para compilar y probar Kafka.

**Corrida 1**
- **[docker · low] Desplegar Apache Kafka con Docker**
  - Resumen: Despliega una plataforma de streaming de eventos para gestionar pipelines de datos y analíticas en tiempo real en tu infraestructura ejecutando un contenedor.
  - Cita: «docker run -p 9092:9092 apache/kafka:latest»
  - Stack: Docker · Dependencias: Docker instalado en el sistema · Disparadores: —
  - Snippet (bash): `docker run -p 9092:9092 apache/kafka:latest`
  - Documentación: https://github.com/apache/kafka#running-a-kafka-broker

**Corrida 2**
- **[docker · medium] Desplegar un clúster de Apache Kafka con Docker**
  - Resumen: Ejecuta Apache Kafka como contenedor en tu infraestructura para gestionar pipelines de eventos y streaming de datos en tiempo real.
  - Cita: «docker run -p 9092:9092 apache/kafka:latest»
  - Stack: Docker, Java · Dependencias: Docker instalado, Java · Disparadores: —
  - Snippet (bash): `docker run -p 9092:9092 apache/kafka:latest`
  - Documentación: https://github.com/apache/kafka#running-a-kafka-broker

### openai/openai-python

Requeridas: sdk · Admisibles: — · Prohibidas: webhook
Nota: La sección de webhooks está fuera del texto que ve el modelo.

**Corrida 1**
- **[sdk · medium] Generar texto y respuestas con IA**
  - Resumen: Usa la librería oficial para conectar tu aplicación con los modelos de OpenAI y generar texto o completar chats mediante peticiones síncronas o asíncronas.
  - Cita: «The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.10+ application.»
  - Stack: Python · Dependencias: Clave de API de OpenAI o configuración de identidad · Disparadores: Mensaje del usuario en el chat, Solicitud de generación de contenido
  - Snippet (—): `—`
  - Documentación: https://github.com/openai/openai-python#openai-python-api-library

**Corrida 2**
- **[sdk · medium] Generar texto y respuestas con IA en tu aplicación**
  - Resumen: Conecta la librería de OpenAI para procesar texto, chatear con modelos y analizar imágenes dentro de la lógica de tu aplicación.
  - Cita: «The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.10+ application.»
  - Stack: Python · Dependencias: Clave de API de OpenAI o autenticación por identidad de carga de trabajo · Disparadores: Envío de un mensaje de chat por parte del usuario, Solicitud de análisis de imagen
  - Snippet (python): `import os`
  - Documentación: https://github.com/openai/openai-python#openai-python-api-library

### prometheus/alertmanager

Requeridas: docker, rest_api · Admisibles: webhook · Prohibidas: —

**Corrida 1**
- **[docker · low] Desplegar Prometheus Alertmanager con Docker**
  - Resumen: Despliega Prometheus Alertmanager en un contenedor para gestionar, agrupar y enrutar las alertas de tu aplicación de forma centralizada.
  - Cita: «You can launch an Alertmanager container for trying it out with»
  - Stack: Docker · Dependencias: Docker · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#docker-images

**Corrida 2**
- **[docker · low] Desplegar Alertmanager con Docker**
  - Resumen: Ejecuta Alertmanager como un contenedor Docker en tu infraestructura para gestionar y enrutar las alertas de tus aplicaciones.
  - Cita: «You can launch an Alertmanager container for trying it out with»
  - Stack: Docker · Dependencias: Docker instalado en el sistema · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#docker-images
- **[rest_api · medium] Consultar la API de Alertmanager**
  - Resumen: Llama a la API HTTP de Alertmanager desde tu aplicación para consultar el estado de las alertas y gestionarlas mediante solicitudes HTTP.
  - Cita: «APIv2 is accessed via the `/api/v2` prefix.»
  - Stack: HTTP · Dependencias: Alertmanager corriendo en un servidor accesible · Disparadores: Consulta de estado del sistema
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#api

### jaegertracing/jaeger

Requeridas: docker · Admisibles: rest_api, sdk · Prohibidas: —

**Corrida 1**
- **[docker · low] Desplegar Jaeger con Docker**
  - Resumen: Ejecuta la plataforma de trazado distribuido Jaeger como un contenedor para recopilar trazas y visualizar métricas de la aplicación.
  - Cita: «docker run --rm --name jaeger \»
  - Stack: Docker · Dependencias: Docker instalado · Disparadores: —
  - Snippet (bash): `# Run Jaeger all-in-one (includes UI, collector, query, and in-memory storage)`
  - Documentación: https://github.com/jaegertracing/jaeger#quick-start
- **[rest_api · medium] Enviar trazas mediante OTLP**
  - Resumen: Envía trazas desde la aplicación hacia Jaeger utilizando el protocolo OTLP a través de HTTP o gRPC.
  - Cita: «Send traces via OTLP: gRPC on port 4317, HTTP on port 4318»
  - Stack: OpenTelemetry SDK · Dependencias: Jaeger Collector ejecutándose, OpenTelemetry SDK en la aplicación · Disparadores: Inicio de una petición HTTP en la aplicación, Ejecución de una operación rastreada
  - Snippet (bash): `# Run Jaeger all-in-one (includes UI, collector, query, and in-memory storage)`
  - Documentación: https://github.com/jaegertracing/jaeger#quick-start

**Corrida 2**
- **[docker · low] Desplegar Jaeger con Docker**
  - Resumen: Ejecuta Jaeger como un contenedor para recopilar y visualizar trazas distribuidas en tu entorno de desarrollo o producción.
  - Cita: «docker run --rm --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/jaeger:latest»
  - Stack: Docker · Dependencias: Docker instalado y funcionando · Disparadores: —
  - Snippet (bash): `# Run Jaeger all-in-one (includes UI, collector, query, and in-memory storage)`
  - Documentación: https://github.com/jaegertracing/jaeger#quick-start

### traefik/traefik

Requeridas: docker · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[docker · medium] Desplegar Traefik como contenedor Docker**
  - Resumen: Despliega Traefik utilizando su imagen oficial para gestionar el tráfico y balanceo de carga de tus microservicios.
  - Cita: «Or use the official tiny Docker image and run it with the sample configuration file:»
  - Stack: Docker · Dependencias: Docker corriendo, Archivo de configuración traefik.toml · Disparadores: Despliegue del contenedor
  - Snippet (shell): `docker run -d -p 8080:8080 -p 80:80 -v $PWD/traefik.toml:/etc/traefik/traefik.toml traefik`
  - Documentación: https://github.com/traefik/traefik#download
- **[rest_api · medium] Consultar la API REST de Traefik**
  - Resumen: Consulta la API REST expuesta por Traefik para monitorizar rutas y estado de los microservicios.
  - Cita: «Exposes a Rest API»
  - Stack: HTTP · Dependencias: Traefik en ejecución · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/traefik/traefik#features

**Corrida 2**
- **[docker · medium] Desplegar Traefik con Docker**
  - Resumen: Ejecuta Traefik como un contenedor en tu infraestructura para gestionar el enrutamiento y balanceo de carga de tus servicios mediante su imagen oficial.
  - Cita: «Or use the official tiny Docker image and run it with the sample configuration file:»
  - Stack: Docker · Dependencias: Docker instalado en el sistema · Disparadores: Despliegue de la infraestructura
  - Snippet (shell): `docker run -d -p 8080:8080 -p 80:80 -v $PWD/traefik.toml:/etc/traefik/traefik.toml traefik`
  - Documentación: https://github.com/traefik/traefik#download
- **[rest_api · medium] Consultar la API REST de Traefik**
  - Resumen: Consume la API REST expuesta por Traefik desde tu aplicación para supervisar el estado de las rutas y la configuración de los microservicios.
  - Cita: «Exposes a Rest API»
  - Stack: HTTP · Dependencias: Traefik ejecutándose y accesible por red · Disparadores: Consulta de monitorización de servicios
  - Snippet (—): `—`
  - Documentación: https://github.com/traefik/traefik#features

### celery/celery

Requeridas: sdk · Admisibles: webhook · Prohibidas: —
Nota: README en reStructuredText: sin bloques de código, la idea queda sin snippet.

**Corrida 1**
- **[sdk · medium] Procesar tareas asíncronas con Celery**
  - Resumen: Distribuye tareas pesadas o en segundo plano fuera del flujo principal de tu aplicación utilizando la librería de Celery conectada a un broker de mensajes.
  - Cita: «Celery is written in Python, but the protocol can be implemented in any language. In addition to Python there's node-celery_ for Node.js, a PHP client_, gocelery_, gopher-celery_ for Go, and rusty-cel»
  - Stack: Python, Node.js, Go, Rust · Dependencias: Un broker de mensajes como RabbitMQ o Redis, El paquete celery instalado · Disparadores: Envío de un formulario pesado, Generación de reportes programados
  - Snippet (—): `—`
  - Documentación: https://github.com/celery/celery#whats-a-task-queue

**Corrida 2**
- **[sdk · medium] Usar Celery como librería en tu aplicación**
  - Resumen: Distribuye trabajo pesado en segundo plano instalando Celery en tu aplicación para enviar tareas a una cola mediante un broker.
  - Cita: «Celery is written in Python, but the protocol can be implemented in any language. In addition to Python there's node-celery_ for Node.js, a `PHP client`_, `gocelery`_, gopher-celery_ for Go, and rusty»
  - Stack: Python, Node.js, PHP, Go · Dependencias: Un broker de mensajes como RabbitMQ o Redis, El paquete celery instalado · Disparadores: Envío de un formulario por el usuario, Generación de un reporte pesado
  - Snippet (—): `—`
  - Documentación: https://github.com/celery/celery#whats-a-task-queue
