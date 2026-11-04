import {AssistantError} from './assistant.mjs';
import {getAssistantError} from '../errorPresentation.mjs';
const codes=new Set(['invalid_query','invalid_response','provider_unavailable','timeout']);
// The assistant has its own service origin. Server diagnostics are never displayed.
export function createHttpAssistantProvider({baseUrl,fetchImpl=globalThis.fetch}){
 const url=new URL('assistant',baseUrl.endsWith('/')?baseUrl:baseUrl+'/');
 return {async ask({query},{signal}={}){
  let response;
  try{response=await fetchImpl(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query}),signal});}
  catch(error){if(signal?.aborted||error.name==='AbortError')throw error;throw new AssistantError('connection_error',getAssistantError('connection_error').description);}
  const payload=await response.json().catch(()=>null);
  if(!response.ok){
   const code=payload?.error?.code;
   if(typeof code==='string'&&codes.has(code))throw new AssistantError(code,getAssistantError(code).description);
   throw new AssistantError('technical_error','No pudimos generar la propuesta. Tu descripción se conserva; vuelve a intentarlo.');
  }
  if(payload===null)throw new AssistantError('invalid_response',getAssistantError('invalid_response').description);
  return payload; // requestAssistant validates the full response and catalog references.
 }};
}
