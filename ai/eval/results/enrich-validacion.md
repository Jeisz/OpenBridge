# Comparación del enriquecimiento

## Métricas por modelo

| Métrica | claude-haiku-razona | claude-sonnet | gemini | ollama |
|---|---|---|---|---|
| registros | 32 de 32 | 32 de 32 | 32 de 32 | 32 de 32 |
| válidas al primer intento | 32 de 32 | 32 de 32 | 32 de 32 | 32 de 32 |
| casos de uso aceptados | 90 | 112 | 82 | 71 |
| casos de uso descartados | 2 | 0 | 5 | 49 |
| tokens por repo (entrada / salida) | 6239 / 895 | 6239 / 370 | 3401 / 214 | 3433 / 257 |
| segundos por repo (mediana / máx.) | 4.4 / 7.2 | 2.8 / 4.6 | 1.4 / 2.9 | 6.7 / 17.5 |
| misma categoría principal en las 2 corridas | 15 de 16 | 16 de 16 | 15 de 16 | 13 de 16 |
| principal igual a la semilla (referencia) | 15 de 16 | 16 de 16 | 15 de 16 | 14 de 16 |

## Por repo

Revisión: ¿la categoría principal es correcta? ¿los casos de uso son usos principales y no características? ¿el resumen es fiel?

### apache/beam (no nombrado)

- **claude-haiku-razona · corrida 1:** `data-processing` · Modelo de programación unificado para procesar datos en lote y en streaming, con SDKs para Java, Python y Go que ejecutan los pipelines en distintos motores de procesamiento distribuido.
  - Procesar datos en lote y en streaming con un mismo modelo de pipelines
- **claude-haiku-razona · corrida 2:** `data-processing` · Modelo de programación unificado para procesar datos en lote y en streaming, con SDK en Java, Python y Go que ejecutan pipelines en Flink, Spark, Dataflow y otros backends.
  - Procesar datos en lote y en streaming con un mismo modelo de programación
  - Ejecutar pipelines de datos en Apache Flink, Apache Spark o Google Cloud Dataflow
- **claude-sonnet · corrida 1:** `data-processing` · Modelo de programación unificado para definir pipelines de procesamiento de datos por lotes y en streaming, con SDKs en Java, Python y Go y runners para ejecutarlos en backends como Flink, Spark y Dataflow.
  - Definir pipelines de procesamiento de datos por lotes y en streaming con un mismo modelo
  - Ejecutar el mismo pipeline en distintos backends distribuidos mediante runners
  - Escribir pipelines de datos en Java, Python o Go
- **claude-sonnet · corrida 2:** `data-processing` · Modelo de programación unificado para definir pipelines de procesamiento de datos por lotes y en streaming, con SDKs para Java, Python y Go y runners para ejecutarlos en backends como Flink, Spark o Dataflow.
  - Definir pipelines de procesamiento de datos por lotes y en streaming con un único modelo
  - Ejecutar el mismo pipeline en distintos backends distribuidos mediante runners
  - Ejecutar pipelines en una máquina local para desarrollo y pruebas
- **gemini · corrida 1:** `data-processing` · Modelo de programación unificado para procesamiento de datos por lotes y en tiempo real (batch y streaming).
  - Definir pipelines de procesamiento de datos paralelos tanto por lotes como en flujo continuo
  - Ejecutar programas escritos con el modelo Beam en múltiples motores de procesamiento distribuido
- **gemini · corrida 2:** `data-processing` · Modelo de programación unificado para procesamiento de datos por lotes y en tiempo real (batch y streaming).
  - Definir pipelines de procesamiento de datos paralelos tanto por lotes como en streaming
  - Ejecutar programas en múltiples backends de procesamiento distribuido mediante PipelineRunners
- **ollama · corrida 1:** `data-processing, backend` · Modelo unificado para definir pipelines de procesamiento paralelo en lotes y streaming, junto con SDKs y ejecutores para distribuir el trabajo.
  - Procesar datos en tiempo real o streaming
  - Ejecutar pipelines distribuidos en Apache Spark
  - Ejecutar pipelines distribuidos en Google Cloud Dataflow
  - ~~Procesar datos en lotes~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `data-processing, dev-tools` · Framework unificado para definir y ejecutar pipelines de procesamiento paralelo de datos, tanto por lotes como en tiempo real. Soporta múltiples lenguajes (Java, Python, Go) y runners distribuidos como Flink, Spark y Dataflow.
  - Definir pipelines paralelos para el procesamiento por lotes o de streaming
  - ~~Construir pipelines de procesamiento distribuido en clusters externos~~ (la cita no está en la entrada)
  - ~~Escribir código de procesamiento paralelo usando modelos abstractos y transformaciones~~ (la cita no está en la entrada)

Revisión: 

### argoproj/argo-cd (no nombrado)

- **claude-haiku-razona · corrida 1:** `infrastructure` · Herramienta de entrega continua GitOps para Kubernetes: sincroniza las aplicaciones desplegadas con sus definiciones declarativas guardadas en control de versiones.
  - Automatizar el despliegue y el ciclo de vida de aplicaciones en Kubernetes
  - Gestionar definiciones, configuraciones y entornos de forma declarativa y versionada
- **claude-haiku-razona · corrida 2:** `infrastructure` · Herramienta de despliegue continuo declarativo (GitOps) para Kubernetes. Sincroniza las aplicaciones desplegadas con las configuraciones versionadas en Git.
  - Automatizar el despliegue y el ciclo de vida de aplicaciones en Kubernetes
  - Definir aplicaciones y entornos de forma declarativa y bajo control de versiones
- **claude-sonnet · corrida 1:** `infrastructure` · Herramienta declarativa de entrega continua basada en GitOps para Kubernetes, que automatiza el despliegue y la gestión del ciclo de vida de aplicaciones a partir de definiciones versionadas.
  - Desplegar aplicaciones en Kubernetes siguiendo el enfoque GitOps
  - Automatizar y auditar el despliegue y el ciclo de vida de las aplicaciones
  - Mantener configuraciones y entornos declarativos bajo control de versiones
- **claude-sonnet · corrida 2:** `infrastructure` · Herramienta declarativa de entrega continua basada en GitOps para Kubernetes, que automatiza el despliegue y la gestión del ciclo de vida de aplicaciones a partir de definiciones versionadas.
  - Desplegar aplicaciones en Kubernetes siguiendo el modelo GitOps
  - Automatizar y auditar el despliegue y el ciclo de vida de las aplicaciones
  - Mantener configuraciones y entornos declarativos bajo control de versiones
- **gemini · corrida 1:** `infrastructure` · Herramienta de entrega continua GitOps declarativa para Kubernetes.
  - Gestionar el despliegue y ciclo de vida de aplicaciones de forma automatizada
- **gemini · corrida 2:** `infrastructure, automation` · Herramienta de entrega continua GitOps declarativa para Kubernetes.
  - Gestionar el despliegue y ciclo de vida de aplicaciones de forma automatizada
- **ollama · corrida 1:** `infrastructure, messaging` · Herramienta declarativa GitOps para la entrega continua en Kubernetes. Controla la aplicación, configuración y entornos versionados desde el código.
  - Desplegar aplicaciones en entornos Kubernetes automatizando flujos.
  - Aplicar principios GitOps para mantener consistencia en entornos.
  - Implementar entrega progresiva y gestión de versiones de servicios.
  - Orquestar despliegues múltiples combinados con control de planes y OAM.
  - ~~Gestionar y auditar cambios en configuraciones de infraestructura.~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `infrastructure, dev-tools` · Herramienta declarativa de entregas continuas para Kubernetes basada en GitOps, gestionando aplicaciones y configuraciones mediante control de versiones.
  - Implementar entrega continua para aplicaciones ejecutadas en Kubernetes.
  - Gestionar versiones controladas de definiciones, configuraciones y entornos declarativos.
  - Automatizar el ciclo de vida y la gestión del despliegue de aplicaciones.
  - Evitar pipelines complejos mediante la aplicación de principios GitOps en entornos como Kubernetes.

Revisión: 

### BurntSushi/ripgrep (no nombrado · semilla: `dev-tools`)

- **claude-haiku-razona · corrida 1:** `dev-tools` · Herramienta de línea de comandos que busca recursivamente un patrón de expresión regular en directorios y respeta las reglas de .gitignore.
  - Limitar la búsqueda a tipos de archivo concretos, como Python o JavaScript
  - ~~Buscar un patrón de expresión regular en directorios sin revisar los archivos ignorados por gitignore~~ (caso de uso vacío o de más de 100 caracteres)
- **claude-haiku-razona · corrida 2:** `dev-tools` · Herramienta de línea de comandos que busca recursivamente un patrón de expresión regular en directorios, respetando las reglas de .gitignore.
  - Buscar patrones de expresiones regulares en directorios respetando .gitignore
  - Buscar solo en archivos de tipos específicos
  - Buscar con lookaround y backreferences mediante PCRE2
- **claude-sonnet · corrida 1:** `dev-tools` · Herramienta de línea de comandos que busca de forma recursiva un patrón regex en directorios, respetando las reglas de gitignore y omitiendo por defecto archivos ocultos y binarios.
  - Buscar patrones regex en árboles de código fuente respetando .gitignore
  - Limitar la búsqueda a tipos de archivo concretos o excluir otros
  - Buscar en archivos comprimidos o con codificaciones distintas de UTF-8
  - Reemplazar grep con una alternativa más rápida y con soporte Unicode
- **claude-sonnet · corrida 2:** `dev-tools` · Herramienta de línea de comandos que busca de forma recursiva un patrón regex en directorios, orientada a líneas. Respeta las reglas de gitignore y omite archivos ocultos y binarios por defecto.
  - Buscar patrones regex de forma recursiva en el código fuente de un proyecto
  - Reemplazar grep y otras herramientas de búsqueda de código con filtrado automático
  - Limitar la búsqueda a tipos de archivo concretos, como Python o JavaScript
  - Buscar en archivos comprimidos o con codificaciones de texto distintas de UTF-8
- **gemini · corrida 1:** `search, dev-tools` · Herramienta de búsqueda orientada a líneas que busca recursivamente patrones de expresiones regulares en directorios, respetando las reglas de gitignore.
  - Buscar recursivamente patrones de expresiones regulares en directorios
  - Limitar las búsquedas a tipos específicos de archivos
  - Buscar archivos comprimidos en formatos comunes
- **gemini · corrida 2:** `dev-tools, search` · Herramienta de búsqueda orientada a líneas que busca de forma recursiva en directorios un patrón de expresión regular respetando gitignore.
  - Buscar patrones con expresiones regulares de forma recursiva en directorios
  - Filtrar automáticamente archivos ocultos y binarios ignorando reglas de gitignore
  - Limitar las búsquedas a tipos específicos de archivos
- **ollama · corrida 1:** `dev-tools` · Herramienta de búsqueda por línea orientada recursiva para patrones regex que respeta reglas gitignore, ocultando archivos y binarios.
  - Ejecutar búsquedas en archivos comprimidos sin desconstruir los mismos previamente
  - ~~Buscar patrones dentro de carpetas de código fuente o documentación~~ (la cita no está en la entrada)
  - ~~Filtrar resultados ignorando archivos ocultos especificados en .gitignore~~ (la cita no está en la entrada)
  - ~~Reemplazar texto dentro de archivos según el patrón encontrado~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `dev-tools, search` · Herramienta de búsqueda de línea por línea que recurre en directorios buscando patrones regex, respetando gitignore y ocultando archivos.
  - Buscar código dentro de repositorios de control de versiones
  - Realizar búsquedas rápidas en archivos comprimidos
  - Buscar en archivos con codificaciones de texto no UTF-8
  - Extracción de texto de documentos PDF sin preparación previa

Revisión: 

### cilium/cilium (no nombrado)

- **claude-haiku-razona · corrida 1:** `infrastructure, observability` · Plataforma de redes, seguridad y observabilidad para Kubernetes basada en eBPF. Ofrece CNI, balanceo de carga que puede reemplazar a kube-proxy y políticas de red L3-L7 por identidad.
  - Conectar pods de clústeres Kubernetes mediante una red CNI basada en eBPF
  - Reemplazar kube-proxy para balancear la carga del tráfico entre pods
  - Aplicar políticas de red basadas en identidad en lugar de direcciones IP
  - Monitorear la visibilidad de red y seguridad del tráfico entre cargas de trabajo
- **claude-haiku-razona · corrida 2:** `infrastructure, observability` · Plataforma de red, seguridad y observabilidad basada en eBPF, con plugin CNI para Kubernetes, balanceo de carga distribuido y políticas de red L3-L7 basadas en identidad.
  - Aplicar políticas de red L3/L4 por etiquetas, protocolos y puertos
  - Reemplazar kube-proxy y balancear el tráfico entre pods y servicios
  - Conectar y compartir servicios entre varios clusters de Kubernetes
  - Monitorear la visibilidad de red y de seguridad de las cargas de trabajo
- **claude-sonnet · corrida 1:** `infrastructure, observability, auth` · Solución de redes, observabilidad y seguridad para Kubernetes con plano de datos basado en eBPF. Funciona como plugin CNI, balanceador de carga distribuido y aplica políticas de red L3-L7 basadas en identidad.
  - Proveer redes para clústeres de Kubernetes como plugin CNI
  - Reemplazar kube-proxy con balanceo de carga distribuido en eBPF
  - Aplicar políticas de red L3-L7 basadas en identidad
  - Conectar varios clústeres de Kubernetes con Cluster Mesh
- **claude-sonnet · corrida 2:** `infrastructure, observability` · Solución de redes, seguridad y observabilidad para Kubernetes con dataplane basado en eBPF. Funciona como plugin CNI, balanceador de carga distribuido y aplica políticas de red L3-L7 basadas en identidad.
  - Proveer redes para clústeres de Kubernetes como plugin CNI
  - Reemplazar kube-proxy con balanceo de carga distribuido en eBPF
  - Aplicar políticas de red L3-L7 basadas en identidad en lugar de direcciones IP
  - Conectar varios clústeres de Kubernetes con descubrimiento global de servicios
- **gemini · corrida 1:** `infrastructure, observability, backend` · Solución de redes, observabilidad y seguridad basada en eBPF que proporciona conectividad escalable, balanceo de carga y políticas de red en Kubernetes.
  - Conectar clusters de Kubernetes y proporcionar una red de capa 3 plana
  - Implementar balanceo de carga distribuido para reemplazar kube-proxy
  - Conectar de forma segura múltiples clusters de Kubernetes
  - Aplicar políticas de red basadas en identidad en las capas L3 a L7
- **gemini · corrida 2:** `infrastructure, observability, search` · Solución de redes, observabilidad y seguridad basada en eBPF para contenedores y Kubernetes.
  - Gestionar la red y seguridad en clústeres de Kubernetes
  - Implementar balanceo de carga distribuido
  - Conectar de forma segura múltiples clústeres
  - Aplicar políticas de red basadas en identidad
- **ollama · corrida 1:** `infrastructure, observability` · Infraestructura que proporciona una capa de red rápida y segura para Kubernetes mediante eBPF, permitiendo load balancing distribuido, políticas de red identificadas y conectividad segura entre múltiples clusters.
  - ~~Implementar virtualización basada en encapsulamiento para redes unificadas en Kubernetes con soporte VXLAN y_gene.~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Operar un único punto centralizado para realizar balancing de carga entre contenedores internos hacia servicios externos,~~ (la cita no está en la entrada)
  - ~~Gestionar la seguridad entre contenedores aplicando políticas basadas en identidades y no direcciones IP,~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Establecer conectividad segura y transparente entre múltiples clusters de Kubernetes para entornos híbridos o multi-cloud,~~ (caso de uso vacío o de más de 100 caracteres)
- **ollama · corrida 2:** `backend, infrastructure, observability` · Plataforma de servicio que implementa red, seguridad y observabilidad para Kubernetes usando eBPF en el kernel como dataplane dinámico.
  - Reemplazar kube-proxy y gestionar balanceo de carga distribuido para alto rendimiento.
  - Imponer políticas de red y seguridad basadas en identidad a través del modelo L3-L7.
  - ~~Operar redes virtuales segmentadas para clusters de Kubernetes sin dependencias de dispositivos externos.~~ (caso de uso vacío o de más de 100 caracteres)

Revisión: 

### ClickHouse/ClickHouse (no nombrado)

- **claude-haiku-razona · corrida 1:** `database, analytics` · Sistema de gestión de bases de datos columnar de código abierto para análisis de datos en tiempo real y generación de informes analíticos.
  - Generar informes analíticos de datos en tiempo real
- **claude-haiku-razona · corrida 2:** `database, analytics` · Sistema de gestión de bases de datos orientado a columnas para generar informes analíticos en tiempo real.
  - Generar informes analíticos de datos en tiempo real
- **claude-sonnet · corrida 1:** `database` · Sistema de gestión de bases de datos columnar de código abierto, orientado a generar informes analíticos en tiempo real con SQL. Admite despliegue distribuido y autoalojado.
  - Generar informes analíticos de datos en tiempo real
- **claude-sonnet · corrida 2:** `database` · Sistema de gestión de bases de datos columnar de código abierto, orientado a la analítica en tiempo real y a la generación de informes de datos analíticos. Soporta SQL y despliegue distribuido.
  - Generar informes analíticos de datos en tiempo real
- **gemini · corrida 1:** `database, analytics` · Sistema de gestión de bases de datos analíticas orientado a columnas de código abierto que permite generar informes de datos en tiempo real.
  - Generar informes de datos analíticos en tiempo real
- **gemini · corrida 2:** `database, analytics` · Sistema de gestión de bases de datos analíticas orientado a columnas de código abierto que permite generar informes de datos en tiempo real.
  - Generar informes de datos analíticos en tiempo real
- **ollama · corrida 1:** `database, analytics, data-processing` · Sistema de gestión de bases de datos orientado a columnas en tiempo real para generar informes analíticos. Diseñado para procesamiento distribuido, almacenamiento en memoria y consultas SQL masivas.
  - Procesar grandes volúmenes de datos analíticos en tiempo real desde el código.
- **ollama · corrida 2:** `database` · Sistema de gestión de bases de datos orientado a columnas y MPP para generación de informes analíticos en tiempo real. No incluye: cachés, archivos.
  - ~~Generar~~ (la cita no está en la entrada)
  - ~~Almacenar~~ (cita demasiado corta)
  - ~~Consultar datos estructurados a gran escala~~ (cita demasiado corta)
  - ~~Operar en entornos distribuidos~~ (cita demasiado corta)

Revisión: 

### dagster-io/dagster (no nombrado)

- **claude-haiku-razona · corrida 1:** `data-processing` · Orquestador de pipelines de datos para desarrollar, ejecutar y observar activos de datos como tablas, modelos de machine learning y reportes, con linaje y pruebas integradas.
  - Centralizar metadatos, linaje y observabilidad de datos en una sola herramienta
  - Poner pipelines de datos en producción con un motor de orquestación multi-tenant
  - ~~Mantener actualizados activos de datos como tablas, conjuntos de datos, modelos de machine learning y reportes~~ (caso de uso vacío o de más de 100 caracteres)
- **claude-haiku-razona · corrida 2:** `data-processing, observability` · Plataforma de orquestación de pipelines de datos que define activos de datos como funciones de Python, los ejecuta en el momento adecuado y mantiene su linaje y metadatos.
  - Orquestar pipelines de datos declarados como funciones de Python
  - Mantener actualizados tablas, modelos de machine learning y reportes
  - Centralizar metadatos, linaje y observabilidad de los datos
- **claude-sonnet · corrida 1:** `data-processing` · Orquestador de pipelines de datos para todo el ciclo de desarrollo. Permite declarar en Python los data assets (tablas, datasets, modelos, reportes) y ejecutarlos y mantenerlos actualizados, con lineage y observabilidad integrados.
  - Orquestar pipelines de datos en producción con un motor multi-tenant y multi-herramienta
  - Desarrollar y mantener data assets como tablas, datasets, modelos de ML y reportes
  - Centralizar metadata, catálogo y lineage de los datos en una sola herramienta
- **claude-sonnet · corrida 2:** `data-processing` · Orquestador de pipelines de datos que permite declarar assets como funciones de Python y ejecutarlos en el momento adecuado, con linaje, metadatos y observabilidad integrados a lo largo de todo el ciclo de desarrollo.
  - Orquestar pipelines de datos desde el desarrollo local hasta producción
  - Definir y mantener actualizados assets de datos como tablas, datasets y modelos de ML
  - Centralizar metadatos, catálogo y linaje de los datos en una sola herramienta
- **gemini · corrida 1:** `data-processing, observability` · Orquestador de pipelines de datos nativo para la nube para todo el ciclo de vida de desarrollo, con linaje y observabilidad integrados.
  - Declarar funciones de Python para construir activos de datos y mantenerlos actualizados
  - Centralizar metadatos con observabilidad integrada, diagnósticos, catalogación y linaje
  - ~~Desarrollar y mantener activos de datos como tablas, conjuntos de datos y modelos de aprendizaje automático~~ (caso de uso vacío o de más de 100 caracteres)
- **gemini · corrida 2:** `data-processing, observability` · Plataforma de orquestación de datos nativa de la nube para el desarrollo, la producción y la observación de activos de datos.
  - Centralizar metadatos con observabilidad, diagnósticos, catalogación y linaje integrados
  - ~~Desarrollar y mantener activos de datos como tablas, conjuntos de datos, modelos de aprendizaje automático y informes~~ (caso de uso vacío o de más de 100 caracteres)
- **ollama · corrida 1:** `data-processing, backend` · Plataforma de orquestación para el desarrollo y observabilidad de activos de datos mediante funciones declarativas en Python, soporta todo el ciclo de vida del pipeline.
  - ~~Orquestrar pipelines de ETL/ETL automatizados~~ (la cita no está en la entrada)
  - ~~Desarrollar activos de datos y modelos de ML escalables~~ (la cita no está en la entrada)
  - ~~Gestionar la calidad de los datos y el lineage~~ (la cita no está en la entrada)
  - ~~Proteger el ciclo completo de desarrollo local hasta producción~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `data-processing, analytics` · Plataforma de orquestación para el ciclo de desarrollo completo de activos de datos, permitiendo definir modelos declarativos en Python y gestionar automatizaciones desde la localización hasta la producción.
  - Automatizar flujos de trabajo en entornos locales y de prueba sin configurar infraestructura externa
  - ~~Orquestar trabajos ETL distribuidos para procesar conjuntos de datos estructurados~~ (la cita no está en la entrada)
  - ~~Gestionar el entrenamiento, despliegue y evaluación de modelos de aprendizaje automático como activos en una cadena de flujo de trabajo (MLops)~~ (la cita no está en la entrada)
  - ~~Visualizar la línea de datos y los problemas de calidad para monitorear la salud de pipelines complejos~~ (la cita no está en la entrada)

Revisión: 

### duckdb/duckdb (nombrado en los ejemplos · semilla: `database`)

- **claude-haiku-razona · corrida 1:** `database` · Base de datos analítica embebida en el proceso de la aplicación, sin servidor aparte, con SQL avanzado para consultar archivos como CSV, Parquet y JSON, y otras bases de datos.
  - Ejecutar análisis SQL dentro de la aplicación, sin servidor que administrar
  - Consultar archivos CSV, Parquet, JSON o Excel en disco local o en almacenamiento remoto
  - Consultar otras bases de datos en su lugar, sin un paso ETL aparte
- **claude-haiku-razona · corrida 2:** `database, data-processing` · Base de datos analítica embebida que se ejecuta dentro de la aplicación, sin servidor aparte, con un dialecto SQL amplio para consultar archivos como CSV, Parquet o JSON y otras bases de datos.
  - Consultar archivos CSV, Parquet o JSON directamente con SQL
  - Consultar otras bases de datos como PostgreSQL, MySQL o SQLite sin un paso ETL aparte
  - Ejecutar una base de datos analítica embebida sin gestionar un servidor separado
- **claude-sonnet · corrida 1:** `database, analytics` · Sistema de base de datos analítica que se ejecuta dentro de la aplicación, sin servidor aparte. Ofrece un dialecto SQL amplio, lee CSV, Parquet y JSON, y tiene clientes para Python, R, Java y otros.
  - Consultar archivos CSV, Parquet o JSON con SQL sin cargarlos antes
  - Consultar y unir datos de PostgreSQL, MySQL y SQLite sin un paso ETL
  - Embeber una base de datos analítica en una aplicación sin gestionar un servidor
  - Leer datos remotos desde S3, HTTP, Azure o Google Cloud Storage
- **claude-sonnet · corrida 2:** `database, analytics` · Sistema de base de datos analítica que se ejecuta dentro de la aplicación, sin servidor aparte. Ofrece un dialecto SQL amplio, lee CSV, Parquet y JSON, y consulta otras bases de datos como PostgreSQL, MySQL y SQLite.
  - Consultar archivos CSV, Parquet y JSON con SQL directamente desde disco o S3
  - Consultar y combinar datos de PostgreSQL, MySQL y SQLite sin un paso de ETL
  - Incorporar una base de datos analítica embebida en una aplicación sin servidor aparte
- **gemini · corrida 1:** `database, data-processing` · Sistema de base de datos analítica de alto rendimiento que se ejecuta en proceso dentro de tu aplicación.
  - Consultar archivos de diversos formatos directamente desde el disco local o extremos remotos
  - Conectarse a otros sistemas de base de datos para consultarlos in situ sin un paso ETL separado
- **gemini · corrida 2:** `database, data-processing` · Sistema de base de datos analítica de alto rendimiento diseñado para ejecutarse dentro de la aplicación sin un servidor separado.
  - Consultar archivos de diversos formatos directamente desde el disco local o extremos remotos
  - Conectarse a otros sistemas de base de datos para consultarlos in situ sin un paso ETL separado
- **ollama · corrida 1:** `database, analytics` · Sistema de base de datos analítica de alto rendimiento que funciona dentro del proceso de la aplicación con clientes múltiles y lecturas escritas en varios formatos.
  - Ejecutar consultas SQL sobre datos locales o remotos sin un servidor independiente.
  - Conectar a otros sistemas de bases de datos para leer, unificar y mover datos sin pasos ETL.
  - ~~Learna y escribir múltiples formatos de archivo directamente desde el disco local o endpoints remotos.~~ (la cita no está en la entrada)
  - ~~Utilizar un mecanismo de extensiones modulares para agregar formatos de archivo, conectores de base de datos o nuevas funciones y tipos.~~ (cita demasiado corta)
- **ollama · corrida 2:** `database, analytics` · Base de datos SQL in-process diseñada para análisis, que ejecuta consultas dentro de la aplicación con soporte para múltiples formatos de archivo y conectores a otros sistemas.
  - Analizar grandes conjuntos de datos directamente en memoria o desde archivos externos
  - Lectura y escritura directa de formatos como CSV, Parquet y JSON sin conversión previa
  - Consultar y unir datos cruzando motores de bases de datos sin pasos ETL
  - Usar extensibilidad mediante módulos para añadir conectores y tipos nuevos al tiempo de ejecución

Revisión: 

### encode/httpx (no nombrado)

- **claude-haiku-razona · corrida 1:** `backend` · Cliente HTTP para Python con API compatible con requests, soporte para HTTP/1.1 y HTTP/2, y uso síncrono o asíncrono.
  - Hacer peticiones HTTP síncronas o asíncronas desde Python
  - Migrar código que usa requests con cambios mínimos
  - Hacer peticiones directamente a aplicaciones WSGI o ASGI
- **claude-haiku-razona · corrida 2:** `backend` · Cliente HTTP para Python con API compatible con requests, soporte de HTTP/1.1 y HTTP/2, y uso síncrono o asíncrono.
  - Realizar peticiones HTTP síncronas o asíncronas desde Python
  - Hacer peticiones HTTP/2 desde Python
  - Consumir desde la terminal endpoints HTTP con un cliente integrado
- **claude-sonnet · corrida 1:** `backend` · Cliente HTTP para Python 3 con API síncrona y asíncrona, soporte para HTTP/1.1 y HTTP/2, cliente de línea de comandos integrado y API compatible con requests.
  - Realizar peticiones HTTP desde Python con interfaz síncrona o asíncrona
  - Consumir servicios web usando HTTP/2
  - Probar aplicaciones WSGI o ASGI enviándoles peticiones directamente
  - Lanzar peticiones HTTP desde la terminal con el cliente de línea de comandos
- **claude-sonnet · corrida 2:** `backend` · Cliente HTTP para Python con API síncrona y asíncrona, compatible con HTTP/1.1 y HTTP/2, con una API en gran parte compatible con requests y un cliente de línea de comandos integrado.
  - Realizar peticiones HTTP desde Python de forma síncrona o asíncrona
  - Enviar peticiones HTTP/2 desde aplicaciones Python
  - Probar aplicaciones WSGI o ASGI haciendo peticiones directas a ellas
  - Lanzar peticiones HTTP desde la terminal con el cliente integrado
- **gemini · corrida 1:** `backend` · Librería de cliente HTTP para Python 3 con compatibilidad para HTTP/1.1 y HTTP/2, APIs síncronas y asíncronas, y cliente de línea de comandos integrado.
  - Realizar peticiones HTTP síncronas y asíncronas
  - Establecer conexiones utilizando HTTP/1.1 y HTTP/2
  - Ejecutar peticiones directamente a aplicaciones WSGI o ASGI
  - Utilizar la herramienta desde la línea de comandos
- **gemini · corrida 2:** `backend` · Librería cliente HTTP totalmente equipada para Python 3 que incluye un cliente de línea de comandos, soporte HTTP/1.1 y HTTP/2, y APIs síncronas y asíncronas.
  - Soportar tanto HTTP/1.1 como HTTP/2
  - Proveer interfaces síncronas y asíncronas
  - Realizar peticiones directamente a aplicaciones WSGI o ASGI
- **ollama · corrida 1:** `backend, dev-tools` · Biblioteca de cliente HTTP de próxima generación para Python que soporta API síncrona y asíncrona, protocolos HTTP/1.1 y HTTP/2, un cliente en línea de comandos integrado y autenticación básica.
  - Construir clientes HTTP síncronos
  - Elegir clientes de línea de comandos opcionales
  - Implementar múltiples tipos de autenticación en códigos de Python
  - ~~Implementar soporte asíncrono asíncrono~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `dev-tools` · Biblioteca de código abierto que funciona como cliente HTTP asíncrono para Python, ofreciendo soporte nativo para HTTP/1.1 y HTTP/2.
  - Enviar solicitudes HTTP con el cliente integrador desde la terminal.
  - Ejecutar operaciones asíncronas de red utilizando la API estándar de Python.
  - Comunicarse directamente con aplicaciones WSGI o ASGI en el servidor.

Revisión: 

### fastapi/fastapi (nombrado en los ejemplos · semilla: `backend`)

- **claude-haiku-razona · corrida 1:** `backend` · Framework web de Python para construir APIs a partir de type hints estándar, con validación de datos y documentación OpenAPI interactiva generada automáticamente.
  - Construir APIs web en Python a partir de type hints estándar
  - Generar documentación interactiva de la API de forma automática
  - Validar automáticamente los datos de entrada de las peticiones
- **claude-haiku-razona · corrida 2:** `backend` · Framework web de Python para construir APIs a partir de anotaciones de tipos estándar. Se basa en Starlette y Pydantic y genera documentación interactiva de la API automáticamente.
  - Construir APIs web en Python a partir de anotaciones de tipos estándar
  - Generar documentación interactiva de la API automáticamente
  - Validar datos de entrada y devolver errores claros cuando son inválidos
- **claude-sonnet · corrida 1:** `backend` · Framework web para construir APIs con Python basado en type hints estándar. Usa Starlette y Pydantic, valida datos y genera documentación interactiva con OpenAPI y JSON Schema.
  - Construir APIs REST en Python con validación de datos mediante type hints
  - Generar documentación interactiva de la API automáticamente con Swagger UI y ReDoc
  - Exponer modelos de aprendizaje automático como servicio REST para obtener predicciones
- **claude-sonnet · corrida 2:** `backend` · Framework web para construir APIs con Python basado en las anotaciones de tipos estándar. Usa Starlette y Pydantic, y genera documentación interactiva con OpenAPI y JSON Schema.
  - Construir APIs REST con Python usando anotaciones de tipos estándar
  - Validar y convertir datos de entrada y salida de una API de forma automática
  - Generar documentación interactiva de la API con Swagger UI y ReDoc
  - Exponer modelos de aprendizaje automático como servicios REST para obtener predicciones
- **gemini · corrida 1:** `backend` · Framework web moderno y de alto rendimiento para construir APIs con Python basado en tipos estándar.
  - Construir APIs con Python
  - Generar documentación interactiva automáticamente
- **gemini · corrida 2:** `backend` · Framework web moderno y de alto rendimiento para construir APIs con Python basado en tipos estándar.
  - Construir APIs con Python
- **ollama · corrida 1:** `backend` · Framework moderno y de alto rendimiento para desarrollar APIs web con Python utilizando punteros a tipos estándar. Genera documentación interactiva basada en OpenAPI y JSON Schema.
  - Construir APIs REST
  - Reducir errores en el desarrollo de software
  - Generar documentación automática y escalable
  - Desarrollar servicios de Machine Learning integrados con APIs
- **ollama · corrida 2:** `backend, frontend` · Framework web y de APIs moderno para Python. Utiliza punteros de tipo estándar (type hints) para generar validación automática, documentación interactiva y servidores HTTP asincrónicos de alto rendimiento.
  - Servir endpoints RESTful con soporte nativo para operaciones HTTP asíncronas
  - ~~Desarrollar aplicaciones de backend que requieran alta performance en Python~~ (la cita no está en la entrada)
  - ~~Reducir errores humanos y acelerar el desarrollo de características~~ (la cita no está en la entrada)
  - ~~Generar documentación de la API interactiva mediante estándares OpenAPI y JSON Schema~~ (la cita no está en la entrada)

Revisión: 

### grafana/grafana (nombrado en los ejemplos · semilla: `observability`)

- **claude-haiku-razona · corrida 1:** `observability, analytics` · Plataforma de código abierto para visualizar, explorar y alertar sobre métricas, logs y trazas almacenados en múltiples fuentes de datos, como Prometheus, Loki, Elasticsearch, InfluxDB y PostgreSQL.
  - Crear dashboards de monitoreo con métricas de múltiples fuentes de datos
  - Definir reglas de alerta sobre métricas y enviar notificaciones a Slack o PagerDuty
  - Explorar logs y pasar de métricas a logs manteniendo los filtros de etiquetas
- **claude-haiku-razona · corrida 2:** `observability, analytics` · Plataforma de código abierto para visualizar, explorar y crear alertas sobre métricas, logs y trazas almacenados en múltiples fuentes de datos, como Prometheus, Loki, Elasticsearch, InfluxDB y Postgres.
  - Crear dashboards compartidos para visualizar métricas, logs y trazas de sistemas en producción
  - Definir reglas de alerta sobre métricas y enviar notificaciones a Slack, PagerDuty u OpsGenie
  - Combinar datos de distintas fuentes en un mismo gráfico
- **claude-sonnet · corrida 1:** `observability, analytics` · Plataforma de observabilidad y visualización de datos que permite consultar, visualizar y alertar sobre métricas, logs y trazas desde múltiples fuentes como Prometheus, Loki, Elasticsearch, InfluxDB y Postgres.
  - Monitorear métricas y logs de sistemas mediante dashboards compartidos
  - Definir reglas de alerta con notificaciones a Slack, PagerDuty u OpsGenie
  - Explorar logs y métricas con consultas ad hoc y filtros de etiquetas
  - Combinar varias fuentes de datos en un mismo gráfico
- **claude-sonnet · corrida 2:** `observability, analytics` · Plataforma de observabilidad y visualización de datos que consulta, visualiza y genera alertas sobre métricas, logs y trazas de múltiples fuentes como Prometheus, Loki, Elasticsearch, InfluxDB y Postgres.
  - Crear dashboards reutilizables para visualizar métricas y logs de distintas fuentes
  - Definir reglas de alerta y recibir notificaciones en Slack, PagerDuty u OpsGenie
  - Explorar logs y métricas con consultas ad-hoc y comparar rangos de tiempo
  - Combinar varias fuentes de datos en un mismo gráfico
- **gemini · corrida 1:** `observability` · Plataforma de observabilidad y visualización de datos que permite consultar, visualizar y alertar sobre métricas, logs y trazas de múltiples fuentes.
  - Visualizar métricas y logs mediante gráficos rápidos y flexibles
  - Crear paneles dinámicos y reutilizables con variables de plantilla
  - Definir reglas de alerta visualmente y enviar notificaciones
- **gemini · corrida 2:** `observability, analytics` · Plataforma de observabilidad y visualización de datos que permite consultar, visualizar y crear alertas sobre métricas, logs y trazas desde múltiples fuentes.
  - Visualizar métricas y logs con diferentes opciones de paneles
  - Crear dashboards dinámicos y reutilizables con variables de plantilla
  - Explorar datos mediante consultas ad-hoc y desglose dinámico
  - Definir reglas de alerta visualmente para métricas importantes
- **ollama · corrida 1:** `observability` · Plataforma de monitorización y observabilidad que permite consultar, visualizar y alertar en métricas y registros provenientes de diversas fuentes.
  - Visualizar métricas y registros
  - Crear y compartir paneles dinámicos
  - Configurar alertas para métricas críticas
  - Explorar datos con consultas ad-hoc
- **ollama · corrida 2:** `observability, analytics` · Plataforma de monitoreo y visualización de métricas, logs y trazas para múltiples fuentes, permitiendo el creacione de paneles interactivos y alertas.
  - Visualizar dashboards
  - Definir alertas para métricas críticas
  - Explorar datos de métricas y logs simultáneamente
  - Analizar y comparar rangos temporales en distintas fuentes

Revisión: 

### hashicorp/vault (nombrado en los ejemplos · semilla: `auth`)

- **claude-haiku-razona · corrida 1:** `auth` · Herramienta de gestión de secretos que almacena claves, contraseñas y certificados con control de acceso y registro de auditoría. Genera credenciales dinámicas, revoca secretos y ofrece cifrado como servicio.
  - Almacenar claves, contraseñas y certificados con cifrado antes de escribirlos en disco
  - Generar credenciales temporales para AWS o bases de datos SQL bajo demanda
  - Cifrar y descifrar datos sin que Vault los almacene
  - Revocar secretos para rotar claves o bloquear sistemas tras una intrusión
- **claude-haiku-razona · corrida 2:** `auth` · Herramienta de gestión de secretos, como claves de API, contraseñas y certificados, con cifrado como servicio y gestión de accesos privilegiados.
  - Almacenar secretos como pares clave-valor cifrados antes de escribirlos en disco
  - Revocar secretos individuales o grupos de secretos para rotar claves o bloquear sistemas
  - Cifrar y descifrar datos sin almacenarlos, para que los equipos no diseñen su propio cifrado
  - Gestionar el acceso privilegiado a sistemas y recursos sensibles
- **claude-sonnet · corrida 1:** `auth` · Herramienta para gestionar secretos, cifrado como servicio y gestión de acceso privilegiado. Ofrece una interfaz unificada para acceder a secretos con control de acceso estricto y registro de auditoría detallado.
  - Almacenar de forma segura claves de API, contraseñas y certificados
  - Generar credenciales dinámicas bajo demanda para AWS o bases de datos SQL
  - Cifrar y descifrar datos sin almacenarlos en Vault
  - Revocar secretos individuales o grupos de secretos ante una intrusión
- **claude-sonnet · corrida 2:** `auth` · Herramienta para gestionar secretos, cifrado como servicio y gestión de acceso privilegiado. Almacena secretos cifrados, controla el acceso y registra un log de auditoría detallado.
  - Almacenar de forma segura claves de API, contraseñas y certificados
  - Generar credenciales dinámicas bajo demanda para AWS o bases de datos SQL
  - Cifrar y descifrar datos de aplicaciones sin almacenarlos en Vault
  - Revocar secretos individuales o en bloque ante una intrusión o rotación de claves
- **gemini · corrida 1:** `auth` · Herramienta para el acceso seguro a secretos, cifrado como servicio y gestión de accesos privilegiados con control de acceso y registro de auditoría.
  - Generar secretos bajo demanda para sistemas como AWS o bases de datos SQL con revocación automática
  - Cifrar y descifrar datos sin necesidad de almacenarlos
  - Asociar una concesión temporal a cada secreto para su revocación y renovación automática
  - ~~Almacenar de forma segura pares clave/valor con cifrado previo a la escritura en almacenamiento persistente~~ (caso de uso vacío o de más de 100 caracteres)
- **gemini · corrida 2:** `auth, database, storage` · Herramienta para acceder de forma segura a secretos, como claves API, contraseñas y certificados, con control de acceso y registro de auditoría.
  - Almacenar claves y valores arbitrarios cifrados en almacenamiento persistente
  - Generar secretos dinámicos bajo demanda para sistemas como AWS o bases de datos SQL
  - Cifrar y descifrar datos sin necesidad de almacenarlos
  - Revocar automáticamente secretos individuales o árboles de secretos
- **ollama · corrida 1:** `auth, dev-tools, storage` · Sistema de gestión y almacenamiento seguro de secretos (claves, contraseñas, certificados) con control de acceso granular, generación dinámica y cifrado en el servidor. Permite autenticación y almacenización de credenciales.
  - Acceder a claves secretas y contraseñas con un nivel de seguridad y control estrictos.
  - Generar credentials dinámicas para sistemas externos como bases de datos o servicios en la nube.
  - Desarrollar aplicaciones que requieran la integración de gestión de identidad y secretos.
  - ~~Almacenar datos sensibles cifrados antes de guardarlos en bases de datos o almacenamiento persistente.~~ (caso de uso vacío o de más de 100 caracteres)
- **ollama · corrida 2:** `auth, database, storage` · Herramienta para gestión de secretos, cifrado como servicio y acceso privilegiado. Proporciona interfaz unificada, control de acceso estricto y auditoría detallada para credenciales y claves.
  - Gestionar almacenamiento seguro de secretos mediante pares clave/valor encriptados.
  - Generar y revocar dinámicamente secretos temporales bajo demanda (ej. credenciales AWS o SQL).
  - Encriptar y desencriptar datos sin almacenarlos en persistencia local.
  - ~~Gestionar caducidad de acceso mediante sistema de arrendamientos (leasing) con opción de renovación automática.~~ (caso de uso vacío o de más de 100 caracteres)

Revisión: 

### nuxt/nuxt (no nombrado)

- **claude-haiku-razona · corrida 1:** `frontend, backend` · Framework full-stack de Vue para crear aplicaciones y sitios web con renderizado en servidor, generación estática y renderizado híbrido.
  - Construir aplicaciones web full-stack con Vue.js, con renderizado en servidor y generación estática
  - Crear sitios web optimizados para buscadores con metaetiquetas y renderizado en servidor
- **claude-haiku-razona · corrida 2:** `frontend, backend` · Framework full-stack de código abierto para crear aplicaciones y sitios web con Vue.js, con renderizado en servidor, generación estática y rutas automáticas.
  - Construir aplicaciones web full-stack con Vue.js
  - Crear sitios web optimizados para SEO con renderizado en servidor o generación estática
  - Desplegar aplicaciones en diversas plataformas de hosting
- **claude-sonnet · corrida 1:** `frontend, backend` · Framework de código abierto basado en Vue.js para crear aplicaciones web y sitios full-stack con TypeScript, que admite renderizado en servidor, generación de sitios estáticos y renderizado híbrido.
  - Construir aplicaciones web full-stack con Vue.js y un directorio server/
  - Generar sitios estáticos o con renderizado en servidor, híbrido y en el borde
  - Crear sitios web optimizados para SEO con meta tags
  - Ampliar el proyecto con módulos de la comunidad y del equipo de Nuxt
- **claude-sonnet · corrida 2:** `frontend, backend` · Framework de código abierto basado en Vue.js para crear aplicaciones web full-stack con renderizado en servidor, generación de sitios estáticos y renderizado híbrido, con enrutamiento automático y TypeScript.
  - Crear aplicaciones web full-stack con Vue.js usando el directorio server/
  - Generar sitios estáticos y aplicaciones con renderizado en servidor o híbrido
  - Construir sitios web optimizados para buscadores con meta tags
  - Extender proyectos con módulos de la comunidad y del equipo
- **gemini · corrida 1:** `frontend, backend` · Framework web full-stack libre y de código abierto basado en Vue.js para crear aplicaciones y sitios web tipados y de alto rendimiento.
  - Crear aplicaciones web y sitios web full-stack con Vue.js
  - Desarrollar aplicaciones full-stack utilizando el directorio server
  - Desplegar en una variedad de plataformas de alojamiento
  - ~~Implementar renderizado del lado del servidor, generación de sitios estáticos, renderizado híbrido y en el edge~~ (caso de uso vacío o de más de 100 caracteres)
- **gemini · corrida 2:** `frontend` · Framework web full-stack de código abierto basado en Vue.js para crear aplicaciones y sitios web.
  - Configurar enrutamiento automático con división de código y pre-carga
  - Desarrollar la parte de servidor con el directorio server/
  - Desplegar en una variedad de plataformas de alojamiento
  - ~~Implementar renderizado del lado del servidor, generación de sitios estáticos, renderizado híbrido y en el borde~~ (caso de uso vacío o de más de 100 caracteres)
- **ollama · corrida 1:** `backend, frontend, dev-tools` · Framework full-stack de Vue.js para aplicaciones y sitios web seguros, rápidos y escalables. Ofrece renderizado en servidor, generación estática, rutas automáticas y gestión de estado desde el código.
  - Desarrollar aplicaciones web completas con Vue.js que funcionen tanto en servidor como cliente.
  - Crear sitios web optimizados para motores de búsqueda y autocontenidos sin configuración adicional.
  - Construir interfaces frontend extensibles integrando bibliotecas de terceros fácilmente.
  - Programar aplicaciones tipo full-stack directamente del servidor con TypeScript.
- **ollama · corrida 2:** `frontend, ai` · Framework de desarrollo web que combina Vue.js con capacidades de renderizado en el servidor (SSR), generación estática y tipos de datos, orientado al ecosistema JavaScript.
  - ~~Desarrollar aplicaciones web completas y escalables con un enfoque en la seguridad y el rendimiento tipo producción~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Optimizar sitios web para motores de búsqueda mediante renderizado del lado del servidor y generación estática de sitios~~ (la cita no está en la entrada)

Revisión: 

### ollama/ollama (nombrado en los ejemplos · semilla: `ai`)

- **claude-haiku-razona · corrida 1:** `ai` · Herramienta para ejecutar modelos de IA abiertos, como Gemma, Qwen, DeepSeek o GLM, en local o en la nube, con una API REST y librerías para Python y JavaScript.
  - Ejecutar modelos de lenguaje abiertos en local
  - Integrar modelos en aplicaciones mediante una API REST
  - Conectar agentes de programación como Claude Code o Codex
  - Crear un asistente de IA personal en WhatsApp o Telegram
- **claude-haiku-razona · corrida 2:** `ai` · Herramienta para ejecutar modelos de lenguaje abiertos como Gemma, Qwen, DeepSeek o Llama en local o en la nube, con CLI, API REST y librerías para Python y JavaScript.
  - Ejecutar modelos de lenguaje abiertos en local con total privacidad
  - Integrar modelos en aplicaciones mediante su API REST o sus librerías de Python y JavaScript
  - Conectar agentes de programación como Claude Code u OpenCode a modelos propios
- **claude-sonnet · corrida 1:** `ai` · Herramienta para descargar y ejecutar modelos de lenguaje abiertos (Gemma, Qwen, DeepSeek, gpt-oss y otros) de forma local o en la nube, con CLI, API REST y librerías para Python y JavaScript.
  - Ejecutar modelos de lenguaje abiertos de forma local con CLI
  - Integrar modelos locales en aplicaciones mediante la API REST
  - Conectar modelos a agentes de programación como Claude Code u OpenCode
  - Crear un asistente personal de IA en WhatsApp, Telegram o Slack
- **claude-sonnet · corrida 2:** `ai` · Herramienta para descargar y ejecutar modelos de lenguaje abiertos (Gemma, Qwen, DeepSeek, gpt-oss y otros) de forma local o en la nube, con CLI, API REST y librerías para Python y JavaScript.
  - Ejecutar modelos de lenguaje abiertos de forma local o en la nube
  - Conversar con un modelo desde la línea de comandos
  - Integrar modelos en aplicaciones mediante la API REST
  - Conectar modelos locales con agentes de programación como Claude Code u OpenCode
- **gemini · corrida 1:** `ai` · Servidor e interfaz para ejecutar, gestionar y chatear con modelos de lenguaje de código abierto de forma local o en la nube.
  - Ejecutar y chatear con modelos de lenguaje localmente
  - Gestionar y ejecutar modelos mediante una API REST
- **gemini · corrida 2:** `ai` · Servidor de inferencia y ejecución local de modelos de lenguaje de gran tamaño (LLM) con soporte para múltiples arquitecturas.
  - Ejecutar y chatear con modelos de lenguaje de forma local
  - Gestionar y ejecutar modelos mediante una API REST
- **ollama · corrida 1:** `ai, backend` · Servidor de inferencia para ejecutar modelos de lenguaje grandes (LLMs) y generar texto localmente o en la nube con privacidad completa, integrado con múltiples frameworks y aplicaciones.
  - Conectar Ollama con agentes existentes o aplicaciones como Claude Code, OpenClaw y Copilot.
  - ~~Proceder de un modelo de IA preexistente para generar respuestas a consultas.~~ (la cita no está en la entrada)
  - ~~Integrar con frameworks de orquestación de IA como LangChain, crewAI y AutoGPT para construir agentes autónomos.~~ (la cita no está en la entrada)
  - ~~Implementar aplicaciones RAG para consultas sobre documentos con motores como RAGFlow y MaxKB.~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `ai, backend` · Herramienta para ejecutar modelos de lenguaje localmente en la nube o on-premise con privacidad completa, soportando múltiples frameworks y agentes.
  - ~~Procesar consultas de chat con modelos generativos como Gemma o Claude mediante interacción por línea de comandos o APIs REST.~~ (la cita no está en la entrada)
  - ~~Servir inferencias para frameworks de integración y agentes que requieren acceso a LLMs localmente configurables.~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Gestionar modelos distribuidos y servidores de inferencia a través de librerías y SDKs compatibles con Python, Go y múltiples lenguajes.~~ (la cita no está en la entrada)

Revisión: 

### pgvector/pgvector (nombrado en los ejemplos · semilla: `search`)

- **claude-haiku-razona · corrida 1:** `search, database` · Extensión de código abierto para PostgreSQL que almacena vectores y permite buscar los más similares, de forma exacta o aproximada, con índices HNSW e IVFFlat.
  - Guardar vectores junto con el resto de los datos de una base PostgreSQL
  - Buscar vecinos más cercanos entre vectores con búsqueda aproximada
  - Escalar la búsqueda de vectores numerosos con cuantización
- **claude-haiku-razona · corrida 2:** `search, database` · Extensión de código abierto para Postgres que almacena vectores y busca sus vecinos más cercanos por similitud, de forma exacta o aproximada con índices HNSW e IVFFlat.
  - Buscar vectores similares dentro de Postgres
  - Almacenar vectores junto con el resto de los datos
  - Buscar vecinos más cercanos exactos o aproximados
- **claude-sonnet · corrida 1:** `search, database` · Extensión de Postgres para búsqueda por similitud de vectores. Permite almacenar vectores junto al resto de los datos y hacer búsqueda exacta o aproximada de vecinos más cercanos con índices HNSW e IVFFlat.
  - Buscar vecinos más cercanos de vectores directamente en Postgres
  - Almacenar vectores junto con el resto de los datos de la aplicación
  - Acelerar consultas de similitud con índices aproximados HNSW o IVFFlat
- **claude-sonnet · corrida 2:** `search, database` · Extensión de Postgres para búsqueda por similitud de vectores. Permite almacenar vectores junto a los demás datos y hacer búsqueda exacta o aproximada de vecinos más cercanos con índices HNSW e IVFFlat.
  - Almacenar vectores junto al resto de los datos en Postgres
  - Buscar vecinos más cercanos exactos o aproximados mediante distintas métricas de distancia
  - Acelerar consultas de similitud con índices aproximados HNSW o IVFFlat
- **gemini · corrida 1:** `search, database` · Extensión open source para búsqueda de similitud de vectores en Postgres, que permite almacenar y buscar vectores junto al resto de los datos.
  - Realizar búsquedas de vecinos más cercanos exactas y aproximadas
  - Escalar grandes volúmenes de vectores mediante cuantización
- **gemini · corrida 2:** `search, database` · Extensión open-source para PostgreSQL que permite realizar búsqueda de similitud de vectores y almacenar embeddings junto con los demás datos.
  - Realizar búsquedas de vecinos más cercanos exactas y aproximadas
  - Escalar grandes volúmenes de vectores mediante cuantización
- **ollama · corrida 1:** `database, search` · Extensión de base de datos PostgreSQL para almacenar vectores y realizar búsqueda por vecindad más cercana (exacta o aproximada) usando distintos tipos de distancia y tipos numéricos, integrándose en los registros ordinarios.
  - Buscar documentos similares en una base de datos principal
  - Implementar búsqueda semántica dentro de PostgreSQL
  - Realizar consultas de vecindad más cercana con diferentes métricas (L2, producto interno, coseno)
  - Escalar el uso para grandes volúmenes mediante cuantización
- **ollama · corrida 2:** `database, search` · Extensión de Postgres para almacenar vectores y realizar búsqueda por similaridad. Permite búsquedas exactas y aproximadas con múltiples medidas de distancia.
  - ~~Realizar búsqueda de vecinos más cercanos (exacta o aproximada) en conjuntos grandes de datos estructurados~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Integrar capacidades vectoriales directamente en entornos de base de datos relacionales mediante consultas SQL nativas~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Optimizar el rendimiento de búsqueda de similaridad escalando el uso de cuantización para grandes volúmenes de vectores~~ (caso de uso vacío o de más de 100 caracteres)
  - ~~Implementar índices HNSW e IVFFlat para acelerar consultas en tiempo real sin abandonar la consistencia ACID de Postgres~~ (caso de uso vacío o de más de 100 caracteres)

Revisión: 

### redis/redis (nombrado en los ejemplos · semilla: `cache`)

- **claude-haiku-razona · corrida 1:** `cache, database, search` · Base de datos en memoria y servidor de estructuras de datos, usado como caché, con motor de consultas sobre documentos JSON y búsqueda vectorial.
  - Cachear datos de acceso frecuente para responder más rápido
  - Guardar sesiones de usuario distribuidas
  - Indexar documentos para buscar por texto completo y vectores
  - Implementar colas y comunicación entre servicios
- **claude-haiku-razona · corrida 2:** `database, cache, search` · Almacén de estructuras de datos en memoria que sirve como caché, base de datos clave-valor y motor de consulta de documentos y vectores.
  - Acelerar respuestas guardando en caché datos de uso frecuente
  - Almacenar sesiones de usuario distribuidas entre servidores
  - Indexar documentos para búsqueda vectorial y de texto completo
  - Comunicar servicios mediante colas, pub/sub y streams
- **claude-sonnet · corrida 1:** `cache, database, messaging` · Servidor de estructuras de datos en memoria que funciona como caché, base de datos NoSQL clave-valor y de documentos, motor de búsqueda vectorial y de texto, y message broker con streams y pub/sub.
  - Cachear datos de uso frecuente para aliviar la base de datos principal
  - Gestionar sesiones de usuario distribuidas
  - Implementar colas de trabajo, pub/sub y streams entre servicios
  - Almacenar vectores y memoria para aplicaciones de IA generativa con RAG
- **claude-sonnet · corrida 2:** `cache, database, messaging` · Servidor de estructuras de datos en memoria que funciona como caché, base de datos clave-valor y documental, con motor de consulta y búsqueda vectorial, streams y pub/sub.
  - Cachear datos de uso frecuente para evitar consultar la base de datos principal
  - Gestionar sesiones de usuario distribuidas
  - Implementar colas de trabajos, mensajería entre servicios y pub/sub
  - Almacenar vectores y memoria para aplicaciones de IA generativa, RAG y caché semántica
- **gemini · corrida 1:** `cache, database, search` · Sistema de caché en memoria, servidor de estructuras de datos y motor de consultas de documentos y vectores en tiempo real.
  - Implementar almacenamiento en caché con políticas de desalojo y expiración de claves
  - Gestionar sesiones distribuidas con modelado flexible de datos
  - Almacenar datos NoSQL de tipo clave-valor, documentos y series temporales
  - Realizar búsquedas vectoriales y de texto completo para aplicaciones de IA generativa
- **gemini · corrida 2:** `cache, database, search` · Sistema de caché en memoria, servidor de estructuras de datos y motor de consultas de documentos y vectores en tiempo real.
  - Implementar almacenamiento en caché con múltiples políticas de desalojo y expiración de claves
  - Gestionar sesiones de usuario distribuidas con opciones flexibles de modelado de datos
  - Almacenar y buscar datos vectoriales para aplicaciones de inteligencia artificial generativa
  - Procesar colas de mensajes y eventos en tiempo real con agentes de mensajería
- **ollama · corrida 1:** `cache, database` · Servidor de caché y almacén de datos en memoria para aplicaciones en tiempo real. Ofrece alto rendimiento con latencia baja, soporte flexible para múltiples estructuras de datos y capacidades avanzadas como búsqueda semántica.
  - Almacenar caché de datos
  - Gestionar sesiones de usuario
  - Procesar mensajes entre servicios
  - Realizar búsqueda semántica y consultas vectoriales
- **ollama · corrida 2:** `cache, search, database` · Servidor en memoria para caché de alto rendimiento y almacenamiento documentales. Soporta operaciones vectoriales y búsquedas semánticas además de bases de datos clave-valor, series temporales y estructuras distribuidas.
  - Cachear datos frecuentemente accesibles para reducir la latencia en aplicaciones críticas.
  - Almacenar sesiones de usuario persistentes y distribuidas entre múltiples instancias.
  - Realizar búsquedas semánticas y recuperación de documentos vectoriales para aplicaciones IA.
  - Actuar como mensajería y cola de eventos entre servicios mediante streams y pub/sub.

Revisión: 

### storybookjs/storybook (no nombrado)

- **claude-haiku-razona · corrida 1:** `dev-tools, frontend` · Workshop de frontend para construir, documentar y probar componentes de interfaz de forma aislada, con soporte para React, Vue, Angular, Svelte y web components.
  - Construir componentes de interfaz de forma aislada
  - Documentar componentes de interfaz
  - Probar componentes de interfaz
- **claude-haiku-razona · corrida 2:** `dev-tools, frontend` · Workshop de frontend para construir, documentar y probar componentes de interfaz de forma aislada, con soporte para React, Vue, Angular, Svelte y web components.
  - Construir componentes de interfaz de forma aislada
  - Documentar componentes de interfaz
  - Probar componentes de interfaz
- **claude-sonnet · corrida 1:** `frontend, dev-tools` · Entorno de trabajo para construir, documentar y probar componentes de interfaz de usuario de forma aislada. Admite React, Angular, Vue, Svelte, Web Components y otros, y se amplía con addons.
  - Construir componentes y páginas de interfaz de forma aislada
  - Documentar componentes de interfaz con documentación de alta calidad
  - Probar la accesibilidad de los componentes de interfaz
  - Revisar el diseño responsivo de componentes en distintos tamaños de pantalla
- **claude-sonnet · corrida 2:** `frontend, dev-tools` · Entorno de trabajo (workshop) para construir, documentar y probar componentes de interfaz de usuario de forma aislada, con soporte para React, Vue, Angular, Svelte, web components y otros frameworks, y extensible mediante addons.
  - Construir componentes y páginas de UI de forma aislada
  - Documentar componentes de interfaz con documentación de alta calidad
  - Probar la accesibilidad de los componentes
  - Revisar componentes responsivos en distintos tamaños de pantalla
- **gemini · corrida 1:** `frontend, dev-tools` · Taller frontend para construir, documentar y probar componentes de interfaz de usuario de forma aislada.
  - Construir componentes de interfaz de usuario y páginas en aislamiento
  - Probar componentes para la accesibilidad de los usuarios en Storybook
  - Registrar acciones a medida que los usuarios interactúan con los componentes en la interfaz
  - Agregar documentación de alta calidad a los componentes
- **gemini · corrida 2:** `frontend, dev-tools` · Taller frontend para construir, documentar y probar componentes y páginas de interfaz de usuario de forma aislada.
  - Construir componentes de interfaz de usuario y páginas en aislamiento
  - Documentar componentes de interfaz de usuario
  - Probar componentes de interfaz de usuario
- **ollama · corrida 1:** `frontend, cms` · Entorno de desarrollo para construir, documentar y probar componentes UI de forma aislada en frameworks web y móviles de diversos tipos.
  - ~~Desarrollar componentes UI y páginas en entornos aislados.~~ (la cita no está en la entrada)
  - ~~Documentar alta calidad los componentes de la aplicación.~~ (la cita no está en la entrada)
  - ~~Probar accesibilidad y funcionalidad en componentes interactivos.~~ (la cita no está en la entrada)
  - ~~Crear guías de estilo y sistemas de diseño visualmente consistentes.~~ (la cita no está en la entrada)
- **ollama · corrida 2:** `frontend, dev-tools` · Entorno de trabajo para construir componentes UI en reposo. Permite desarrollar, documentar y probar librerías de frontend como React o Vue sin conectividad al servidor.
  - Desarrollar
  - Aislar lógica de UI
  - ~~Documentar~~ (la cita no está en la entrada)
  - ~~Probar accesibilidad~~ (la cita no está en la entrada)

Revisión: 
