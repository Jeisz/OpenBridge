import {AssistantError,mockAssistant,validateAssistantQuery,validateAssistantResponse,validateAssistantCatalog} from './assistant.mjs';
import {catalogRecords} from './catalog.mjs';
export const assistantRequestTiming=Object.freeze({slowMs:60000,timeoutMs:90000});

// Local request boundary; future HTTP providers plug in without changing the view.
// Race cancellation/deadline even when a provider ignores AbortSignal.
export async function requestAssistant(request,{signal,provider=mockAssistant,catalog=catalogRecords,onSlow,slowMs=assistantRequestTiming.slowMs,timeoutMs=assistantRequestTiming.timeoutMs,...providerOptions}={}){
 const validation=validateAssistantQuery(request.query);
 if(validation)throw new AssistantError('invalid_query',validation);
 if(signal?.aborted)throw new DOMException('Cancelado','AbortError');
 const controller=new AbortController();
 let slowTimer,timeoutTimer,rejectCancellation;
 const cancelled=new Promise((_,reject)=>{rejectCancellation=reject;});
 const cancel=()=>{controller.abort();rejectCancellation(new DOMException('Cancelado','AbortError'));};
 signal?.addEventListener('abort',cancel,{once:true});
 const deadline=new Promise((_,reject)=>{
  timeoutTimer=setTimeout(()=>{
   // Reject with the meaningful timeout before aborting an abort-aware provider.
   reject(new AssistantError('timeout','La consulta tardó demasiado. Tu descripción se conserva; puedes reintentar.'));
   controller.abort();
  },timeoutMs);
 });
 if(onSlow)slowTimer=setTimeout(()=>{if(!controller.signal.aborted)onSlow();},slowMs);
 try{
  const pending=Promise.resolve().then(()=>{if(controller.signal.aborted)throw new DOMException('Cancelado','AbortError');return provider.ask({query:request.query},{...providerOptions,signal:controller.signal});});
  const raw=await Promise.race([pending,deadline,cancelled]);
  if(signal?.aborted)throw new DOMException('Cancelado','AbortError');
  return validateAssistantCatalog(validateAssistantResponse(raw),catalog);
 }catch(error){
  if(signal?.aborted)throw new DOMException('Cancelado','AbortError');
  if(error instanceof AssistantError)throw error;
  throw new AssistantError('technical_error','No pudimos generar la propuesta. Tu descripción se conserva; vuelve a intentarlo.');
 }finally{
  clearTimeout(slowTimer);clearTimeout(timeoutTimer);signal?.removeEventListener('abort',cancel);
 }
}
