# Rama de integración local

Rama: `codex/integration-backend-frontend`.
Base del equipo: `955edba` de main, consultada el 26 de octubre de 2026.
Frontend: copia de la versión local compilada que sirve el preview, incluidos los cambios de contratos v1.1 y las pestañas de propuesta.

## Estado

- `frontend/`: interfaz y mocks locales. Aún no consume una API real del catálogo.
- `backend/`: vacío en main; pendiente implementar la API del catálogo.
- `ai/`: código del equipo conservado desde main.
- `shared/contracts/`: contratos del equipo conservados sin modificar.
- No hay conexión completa ni Docker Compose preparado en esta rama.

## Próximas pruebas

1. Revisar los endpoints existentes en la rama data-engineer antes de implementar otros.
2. Implementar o incorporar la API del catálogo usando Repo y las categorías acordadas.
3. Añadir un modo HTTP al frontend manteniendo su adapter y el modo mock.
4. Conectar el servicio del asistente del equipo respetando AssistantRequest y AssistantResponse v1.1.
5. Validar errores, herramientas inexistentes y respuestas sin resultados.
6. Documentar variables de entorno y comandos para ejecutar todos los servicios.

El asistente se mantiene como servicio de IA separado según el README del equipo; no se duplica dentro de la API del catálogo.
Las pruebas de integración deben distinguir datos mock de datos reales. No guardar credenciales en Git.
