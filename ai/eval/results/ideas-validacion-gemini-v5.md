# Ideas de integración: validación

Corridas: ideas-validacion-gemini-v5-r1.json, ideas-validacion-gemini-v5-r2.json. Referencia: `ai/eval/ideas_reference.json` (15 repos).

## Criterios

| Criterio | Corrida 1 | Corrida 2 |
|---|---|---|
| Requeridas encontradas (≥ 12) | 14/15 ✅ | 14/15 ✅ |
| Repos que debían quedar sin ideas | 3/3 ✅ | 3/3 ✅ |
| Repos por encima de su tope | 0 ✅ | 0 ✅ |
| Ideas prohibidas | 0 ✅ | 0 ✅ |

**Estabilidad** (mismos tipos en todas las corridas, ≥ 12): 12/15 ✅
Cambian entre corridas: duckdb/duckdb, hashicorp/vault, jaegertracing/jaeger

### Corrida 1

- Ideas: 15 (con snippet: 7)
- Descartadas por el código: ninguna

### Corrida 2

- Ideas: 16 (con snippet: 7)
- Descartadas por el código: {'la cita no está en la entrada': 1}

## Por repo (revisión manual)

Para cada idea: ¿el tipo y el resumen son coherentes con la cita? ¿Los disparadores aportan o son relleno? ¿El enlace lleva a la sección correcta?

### ollama/ollama

Requeridas: rest_api, sdk, docker · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[docker · medium] Desplegar Ollama con Docker**
  - Resumen: Ejecuta la herramienta como un contenedor Docker utilizando la imagen oficial publicada para aislar el servicio en tu infraestructura.
  - Cita: «The official Ollama Docker image `ollama/ollama` is available on Docker Hub.»
  - Stack: Docker · Dependencias: Docker · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#docker
- **[rest_api · high] Gestionar modelos mediante la REST API**
  - Resumen: Envía solicitudes HTTP para ejecutar y gestionar modelos de IA directamente desde la aplicación mediante los endpoints expuestos.
  - Cita: «Ollama has a REST API for running and managing models.»
  - Stack: HTTP · Dependencias: Servidor Ollama en ejecución · Disparadores: Solicitud de chat del usuario
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#rest-api
- **[sdk · high] Integrar el SDK de Python en la aplicación**
  - Resumen: Instala el paquete cliente para interactuar con los modelos de lenguaje directamente desde el código Python de tu aplicación.
  - Cita: «- ollama-python»
  - Stack: Python · Dependencias: ollama · Disparadores: Mensaje del usuario en el chat
  - Snippet (python): `from ollama import chat`
  - Documentación: https://github.com/ollama/ollama#libraries

**Corrida 2**
- **[docker · medium] Desplegar Ollama como contenedor**
  - Resumen: Ejecuta el servicio de modelos de IA de forma aislada usando la imagen oficial para simplificar la infraestructura.
  - Cita: «The official Ollama Docker image `ollama/ollama` is available on Docker Hub.»
  - Stack: Docker · Dependencias: Docker · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#docker
- **[rest_api · medium] Usar la REST API de Ollama**
  - Resumen: Envía peticiones HTTP para gestionar y ejecutar modelos de lenguaje directamente desde tu aplicación.
  - Cita: «Ollama has a REST API for running and managing models.»
  - Stack: HTTP · Dependencias: Ollama corriendo en localhost · Disparadores: Pregunta del usuario en la interfaz
  - Snippet (—): `—`
  - Documentación: https://github.com/ollama/ollama#rest-api
- **[sdk · medium] Instalar el SDK de Ollama para Python**
  - Resumen: Integra llamadas a modelos de IA en tu código Python mediante el paquete oficial.
  - Cita: «- ollama-python»
  - Stack: Python · Dependencias: Paquete ollama, Ollama corriendo · Disparadores: Solicitud de análisis de texto
  - Snippet (python): `from ollama import chat`
  - Documentación: https://github.com/ollama/ollama#libraries

### redis/redis

Requeridas: docker, sdk · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[docker · medium] Desplegar Redis como contenedor Docker**
  - Resumen: Ejecuta una instancia de Redis localmente o en tu infraestructura para almacenar caché o datos en memoria usando contenedores.
  - Cita: «docker run -d -p 6379:6379 redis:latest»
  - Stack: Docker · Dependencias: Docker instalado y corriendo · Disparadores: —
  - Snippet (sh): `  docker run -d -p 6379:6379 redis:latest`
  - Documentación: https://github.com/redis/redis#getting-started
- **[sdk · medium] Conectar la aplicación con Redis usando librerías cliente**
  - Resumen: Integra Redis en el código de tu aplicación para gestionar caché, sesiones y colas de mensajes usando clientes oficiales en Python, Go, Java, JavaScript o C#.
  - Cita: «Using Redis with client libraries»
  - Stack: Python, Go, JavaScript, Java · Dependencias: Servidor Redis en ejecución, Librería cliente del lenguaje correspondiente · Disparadores: Inicio de sesión del usuario, Consulta de datos frecuentes
  - Snippet (—): `—`
  - Documentación: https://github.com/redis/redis#table-of-contents

**Corrida 2**
- **[docker · low] Desplegar Redis con Docker**
  - Resumen: Ejecuta una instancia de Redis como contenedor en tu entorno de desarrollo o producción para almacenar caché y datos en memoria.
  - Cita: «docker run -d -p 6379:6379 redis:latest»
  - Stack: Docker · Dependencias: Docker instalado en el sistema · Disparadores: —
  - Snippet (sh): `  docker run -d -p 6379:6379 redis:latest`
  - Documentación: https://github.com/redis/redis#getting-started
- **[sdk · medium] Conectar la aplicación usando librerías cliente**
  - Resumen: Integra Redis en el código de tu aplicación utilizando clientes oficiales o comunitarios para lenguajes como Python, Go, Java o JavaScript.
  - Cita: «- Python (redis-py)»
  - Stack: Python, Go, JavaScript, Java · Dependencias: Servidor Redis en ejecución, Librería cliente instalada en el proyecto · Disparadores: Lectura o escritura de datos en caché, Almacenamiento de sesiones de usuario
  - Snippet (—): `—`
  - Documentación: https://github.com/redis/redis#redis-starter-projects

### duckdb/duckdb

Requeridas: sdk · Admisibles: — · Prohibidas: —

**Corrida 1**
- **[sdk · medium] Consultar bases de datos analíticas desde tu aplicación**
  - Resumen: Conecta tu aplicación a DuckDB usando sus clientes oficiales para realizar consultas SQL analíticas directamente en el proceso de tu aplicación.
  - Cita: «DuckDB is available as a standalone CLI application and has clients for Python, R, Java, Rust, Go, Wasm, and many more, with deep integrations with packages such as pandas.»
  - Stack: Python, Java, Rust, Go · Dependencias: Paquete cliente de DuckDB · Disparadores: Inicio de la aplicación, Ejecución de una consulta analítica
  - Snippet (—): `—`
  - Documentación: https://github.com/duckdb/duckdb#duckdb

**Corrida 2**
- Sin ideas
- Descartada (la cita no está en la entrada): [sdk] Usar DuckDB en la aplicación

### pgvector/pgvector

Requeridas: ninguna · Admisibles: sdk, docker · Prohibidas: —
Nota: Extensión de PostgreSQL que se usa con SQL ("CREATE EXTENSION vector;"): ningún tipo encaja del todo.

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### hashicorp/vault

Requeridas: sdk · Admisibles: — · Prohibidas: —
Nota: Las pruebas con Docker y el git config son para quien desarrolla Vault.

**Corrida 1**
- Sin ideas

**Corrida 2**
- **[sdk · medium] Importar SDK para la gestión de secretos**
  - Resumen: Usa la librería cliente en tu aplicación para acceder de forma segura a secretos y credenciales dinámicas.
  - Cita: «This repository publishes two libraries that may be imported by other projects: `github.com/hashicorp/vault/api` and `github.com/hashicorp/vault/sdk`.»
  - Stack: Go · Dependencias: Servidor de Vault en ejecución · Disparadores: Inicio de la aplicación, Conexión a base de datos
  - Snippet (—): `—`
  - Documentación: https://github.com/hashicorp/vault#importing-vault

### fastapi/fastapi

Requeridas: sdk · Admisibles: — · Prohibidas: webhook, rest_api
Nota: FastAPI sirve para construir tu propia API; no expone una a la que conectarse.

**Corrida 1**
- **[sdk · medium] Instalar el SDK de FastAPI**
  - Resumen: Importa FastAPI en tu aplicación Python para construir APIs web de alto rendimiento y definir rutas y parámetros fácilmente.
  - Cita: «FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.»
  - Stack: Python, Starlette, Pydantic · Dependencias: Python · Disparadores: Petición HTTP entrante en la API
  - Snippet (python): `from fastapi import FastAPI`
  - Documentación: https://fastapi.tiangolo.com/

**Corrida 2**
- **[sdk · medium] Construir APIs de la aplicación**
  - Resumen: Implementa endpoints HTTP y maneja esquemas de datos en tu aplicación usando la librería FastAPI en Python.
  - Cita: «FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.»
  - Stack: Python, Starlette, Pydantic · Dependencias: Python · Disparadores: Petición HTTP entrante
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
  - Resumen: Despliega una plataforma de streaming de eventos distribuida ejecutando un contenedor Docker para gestionar flujos de datos y procesamiento en tiempo real.
  - Cita: «docker run -p 9092:9092 apache/kafka:latest»
  - Stack: Docker · Dependencias: Docker · Disparadores: —
  - Snippet (bash): `docker run -p 9092:9092 apache/kafka:latest`
  - Documentación: https://github.com/apache/kafka#running-a-kafka-broker

**Corrida 2**
- **[docker · medium] Desplegar un broker de Apache Kafka con Docker**
  - Resumen: Ejecuta Apache Kafka como contenedor en tu entorno de desarrollo o infraestructura para gestionar flujos de eventos y pipelines de datos de alto rendimiento.
  - Cita: «docker run -p 9092:9092 apache/kafka:latest»
  - Stack: Docker · Dependencias: Docker instalado · Disparadores: —
  - Snippet (bash): `docker run -p 9092:9092 apache/kafka:latest`
  - Documentación: https://github.com/apache/kafka#running-a-kafka-broker

### openai/openai-python

Requeridas: sdk · Admisibles: — · Prohibidas: webhook
Nota: La sección de webhooks está fuera del texto que ve el modelo.

**Corrida 1**
- **[sdk · medium] Generar texto y respuestas con inteligencia artificial**
  - Resumen: Conecta tu aplicación a la API de OpenAI usando la librería oficial para generar texto, procesar imágenes y chatear con modelos como GPT.
  - Cita: «The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.10+ application.»
  - Stack: Python · Dependencias: Clave de API de OpenAI · Disparadores: Mensaje del usuario en el chat, Solicitud de procesamiento de imagen
  - Snippet (python): `import os`
  - Documentación: https://github.com/openai/openai-python#openai-python-api-library

**Corrida 2**
- **[sdk · medium] Usar la OpenAI API para generar texto y procesar imágenes**
  - Resumen: Conecta tu aplicación a la API de OpenAI mediante el SDK oficial en Python para generar texto, interactuar con modelos de lenguaje y analizar imágenes enviadas por tus usuarios.
  - Cita: «The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.10+ application.»
  - Stack: Python · Dependencias: Una clave de API de OpenAI o autenticación por identidad de carga de trabajo · Disparadores: Envío de un mensaje de chat por parte del usuario, Subida de una imagen para análisis
  - Snippet (python): `import os`
  - Documentación: https://github.com/openai/openai-python#openai-python-api-library

### prometheus/alertmanager

Requeridas: docker, rest_api · Admisibles: webhook · Prohibidas: —

**Corrida 1**
- **[docker · low] Desplegar Alertmanager con Docker**
  - Resumen: Ejecuta Alertmanager como un contenedor en tu infraestructura para gestionar y enrutar las alertas de tus aplicaciones.
  - Cita: «You can launch an Alertmanager container for trying it out with»
  - Stack: Docker · Dependencias: Docker instalado · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#docker-images
- **[rest_api · medium] Consumir la API REST de Alertmanager**
  - Resumen: Conecta tu aplicación a la API HTTP de Alertmanager para consultar el estado y gestionar las alertas en tiempo real.
  - Cita: «APIv2 is accessed via the `/api/v2` prefix.»
  - Stack: HTTP · Dependencias: Instancia de Alertmanager en ejecución · Disparadores: Consulta periódica del estado de alertas
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#api

**Corrida 2**
- **[docker · low] Desplegar Alertmanager con Docker**
  - Resumen: Despliega Alertmanager como un contenedor Docker en tu infraestructura para gestionar y enrutar las alertas de tus aplicaciones.
  - Cita: «$ docker run --name alertmanager -d -p 127.0.0.1:9093:9093 quay.io/prometheus/alertmanager»
  - Stack: Docker · Dependencias: Docker · Disparadores: —
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#docker-images
- **[rest_api · medium] Conectar la aplicación a la API REST de Alertmanager**
  - Resumen: Consulta el estado y gestiona las alertas de la aplicación llamando a la API REST v2 expuesta por Alertmanager.
  - Cita: «APIv2 is accessed via the `/api/v2` prefix.»
  - Stack: OpenAPI · Dependencias: Alertmanager corriendo · Disparadores: Consulta de estado del sistema
  - Snippet (—): `—`
  - Documentación: https://github.com/prometheus/alertmanager#api

### jaegertracing/jaeger

Requeridas: docker · Admisibles: rest_api, sdk · Prohibidas: —

**Corrida 1**
- **[docker · low] Desplegar Jaeger con Docker**
  - Resumen: Ejecuta Jaeger como contenedor para recopilar y visualizar trazas distribuidas en tu entorno de desarrollo o producción.
  - Cita: «docker run --rm --name jaeger \»
  - Stack: Docker · Dependencias: Docker instalado · Disparadores: —
  - Snippet (bash): `# Run Jaeger all-in-one (includes UI, collector, query, and in-memory storage)`
  - Documentación: https://github.com/jaegertracing/jaeger#quick-start

**Corrida 2**
- **[docker · low] Desplegar Jaeger con Docker**
  - Resumen: Ejecuta Jaeger como contenedor para centralizar trazas distribuidas y monitorizar la aplicación mediante OTLP.
  - Cita: «docker run --rm --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/jaeger:latest»
  - Stack: Docker · Dependencias: Docker instalado en el entorno · Disparadores: —
  - Snippet (bash): `# Run Jaeger all-in-one (includes UI, collector, query, and in-memory storage)`
  - Documentación: https://github.com/jaegertracing/jaeger#quick-start
- **[sdk · medium] Enviar trazas mediante OpenTelemetry SDK**
  - Resumen: Envía trazas de rendimiento y llamadas HTTP o gRPC desde tu aplicación hacia el colector de Jaeger.
  - Cita: «SDK["OpenTelemetry SDK"] --> |HTTP or gRPC| COLLECTOR»
  - Stack: OpenTelemetry SDK · Dependencias: Jaeger Collector corriendo · Disparadores: Petición HTTP entrante en la aplicación
  - Snippet (—): `—`
  - Documentación: https://github.com/jaegertracing/jaeger#architecture

### traefik/traefik

Requeridas: docker · Admisibles: rest_api · Prohibidas: —

**Corrida 1**
- **[docker · medium] Desplegar Traefik con Docker**
  - Resumen: Ejecuta Traefik como un contenedor para actuar como proxy inverso y balanceador de carga para tus microservicios.
  - Cita: «Or use the official tiny Docker image and run it with the sample configuration file:»
  - Stack: Docker · Dependencias: Docker instalado, Archivo de configuración traefik.toml · Disparadores: —
  - Snippet (shell): `docker run -d -p 8080:8080 -p 80:80 -v $PWD/traefik.toml:/etc/traefik/traefik.toml traefik`
  - Documentación: https://github.com/traefik/traefik#download
- **[rest_api · medium] Consumir la API REST de Traefik**
  - Resumen: Consulta el estado y la configuración del proxy de forma programática utilizando su API REST integrada.
  - Cita: «Exposes a Rest API»
  - Stack: Go · Dependencias: Traefik ejecutándose · Disparadores: Consulta de métricas o estado del proxy
  - Snippet (—): `—`
  - Documentación: https://github.com/traefik/traefik#features

**Corrida 2**
- **[docker · medium] Desplegar Traefik con Docker**
  - Resumen: Ejecuta Traefik como contenedor para gestionar el enrutamiento y balanceo de carga de tus microservicios de forma automatizada.
  - Cita: «Or use the official tiny Docker image and run it with the sample configuration file:»
  - Stack: Docker · Dependencias: Docker instalado, Archivo de configuración traefik.toml · Disparadores: Despliegue del contenedor de la aplicación
  - Snippet (shell): `docker run -d -p 8080:8080 -p 80:80 -v $PWD/traefik.toml:/etc/traefik/traefik.toml traefik`
  - Documentación: https://github.com/traefik/traefik#download
- **[rest_api · medium] Consultar la API REST de Traefik**
  - Resumen: Obtén información sobre el estado y las rutas de tus servicios consultando la API HTTP que expone la herramienta.
  - Cita: «- Exposes a Rest API»
  - Stack: HTTP · Dependencias: Instancia de Traefik en ejecución · Disparadores: Petición de estado del proxy
  - Snippet (—): `—`
  - Documentación: https://github.com/traefik/traefik#features

### celery/celery

Requeridas: sdk · Admisibles: webhook · Prohibidas: —
Nota: README en reStructuredText: sin bloques de código, la idea queda sin snippet.

**Corrida 1**
- **[sdk · medium] Procesar tareas en segundo plano usando Celery**
  - Resumen: Distribuye trabajo pesado fuera del ciclo de petición-respuesta instalando esta librería en tu aplicación y conectándola a un broker de mensajes como RabbitMQ o Redis.
  - Cita: «from celery import Celery»
  - Stack: Python · Dependencias: Un broker de mensajes como RabbitMQ o Redis · Disparadores: Envío de un formulario pesado por parte del usuario, Generación de un reporte grande
  - Snippet (—): `—`
  - Documentación: https://github.com/celery/celery#celery-is

**Corrida 2**
- **[sdk · medium] Procesar tareas en segundo plano usando Celery**
  - Resumen: Distribuye cargas de trabajo y ejecuta tareas asíncronas en segundo plano desde el código de tu aplicación instalando Celery y conectándolo a un broker de mensajes.
  - Cita: «from celery import Celery»
  - Stack: Python, Django, Flask, FastAPI · Dependencias: Un broker de mensajes como RabbitMQ o Redis · Disparadores: Envío de un formulario por el usuario, Procesamiento nocturnos de datos
  - Snippet (—): `—`
  - Documentación: https://github.com/celery/celery#celery-is
