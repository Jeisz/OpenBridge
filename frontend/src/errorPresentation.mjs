const entry=(title,description,retry=true)=>Object.freeze({title,description,retry});
export const assistantErrors=Object.freeze({
 empty_query:entry('Describe tu idea','Escribe qué quieres construir.',false),
 short_query:entry('Necesitamos más detalles','Escribe al menos 20 caracteres.',false),
 long_query:entry('Acorta tu descripción','Usa un máximo de 2000 caracteres.',false),
 invalid_query:entry('Revisa tu descripción','La descripción debe tener entre 20 y 2000 caracteres.',false),
 provider_unavailable:entry('El asistente no está disponible','Inténtalo de nuevo más tarde.'),
 timeout:entry('La respuesta tardó demasiado','Vuelve a intentarlo.'),
 invalid_response:entry('No pudimos completar la propuesta','Recibimos una respuesta que no podemos mostrar.'),
 connection_error:entry('No pudimos conectar con el asistente','Comprueba tu conexión y vuelve a intentarlo.'),
 unavailable_tool:entry('No pudimos validar la propuesta','Una herramienta recomendada no está disponible en el catálogo.'),
 unverified_license:entry('No pudimos validar la propuesta','Una herramienta recomendada tiene su licencia sin verificar.'),
 technical_error:entry('No pudimos generar la propuesta','Ocurrió un problema inesperado. Vuelve a intentarlo.')
});
export const errorActions=Object.freeze({retry:'Reintentar',close:'Cerrar ficha'});
export const interfaceErrors=Object.freeze({catalog:'No pudimos cargar las herramientas.',detail:'No pudimos cargar la ficha de esta herramienta.',missing:'Esta herramienta no está disponible en el catálogo.',copy:'No pudimos copiar el código. Puedes seleccionarlo y copiarlo manualmente.'});
export const getAssistantError=code=>Object.hasOwn(assistantErrors,code)?assistantErrors[code]:assistantErrors.technical_error;
export function queryErrorCode(query){
 if(typeof query!=='string'||!query.trim())return 'empty_query';
 const length=Array.from(query).length;
 return length<20?'short_query':length>2000?'long_query':null;
}
