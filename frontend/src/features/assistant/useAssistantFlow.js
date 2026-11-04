import {createHttpAssistantProvider} from '../../data/assistantHttp.mjs';
import {useMemo,useState,useRef,useEffect,useReducer} from 'react';
import {useCatalogData} from '../../data/CatalogProvider';
import {promptPresentation,initialPresentation} from '../../promptPresentation.mjs';
import {usePromptLayout} from '../../usePromptLayout';
import {queryErrorCode,getAssistantError} from '../../errorPresentation.mjs';
import {requestAssistant} from '../../data/assistantRequest.mjs';
import {assistantScenarioOptions} from '../../mocks/assistant-scenarios.mjs';
export function useAssistantFlow(isDetail){
 const {tools}=useCatalogData();
 const baseUrl=process.env.NEXT_PUBLIC_ASSISTANT_API_BASE_URL||'';
 const provider=useMemo(()=>baseUrl?createHttpAssistantProvider({baseUrl}):null,[baseUrl]);
 const [query,setQuery]=useState(''),[error,setError]=useState('');
 const [assistantResponse,setAssistantResponse]=useState(null);
 const [originalPrompt,setOriginalPrompt]=useState('');
 const [slow,setSlow]=useState(false),[canRetry,setCanRetry]=useState(false);
 const attempts=useRef(0);
 const resultHeading=useRef(null);
 const finished=Boolean(assistantResponse&&assistantResponse.status!=='needs_clarification');
 const [presentation,dispatchPresentation]=useReducer(promptPresentation,initialPresentation);
 const {pending,expanded,hasResult}=presentation;
 const phase=pending?'loading':hasResult?'done':'idle';
 const input=useRef(null), request=useRef(null);useEffect(()=>()=>request.current?.abort(),[]);
 const preparePromptLayout=usePromptLayout(expanded,input,isDetail);
 useEffect(()=>{if(isDetail){request.current?.abort();setSlow(false);dispatchPresentation({type:'cancel'});}},[isDetail]);
 useEffect(()=>{if(finished&&!isDetail)resultHeading.current?.focus({preventScroll:true});},[finished,isDetail]);
 function newArchitecture(){
  request.current?.abort();request.current=null;attempts.current=0;setSlow(false);setCanRetry(false);setAssistantResponse(null);setOriginalPrompt('');setQuery('');setError('');
  dispatchPresentation({type:'reset'});
  requestAnimationFrame(()=>input.current?.focus({preventScroll:true}));
 }
 async function submit(e){
  e?.preventDefault();if(pending||request.current)return;
  const validation=queryErrorCode(query);if(validation){setCanRetry(false);setError(validation);input.current.focus();return;}
  setError('');setCanRetry(false);setSlow(false);preparePromptLayout();dispatchPresentation({type:'submit'});
  request.current?.abort();const controller=new AbortController();request.current=controller;
  const submitted=query;
  try{
   const scenario=new URLSearchParams(window.location.search).get('assistantMock')||'ok';
   const localScenario=process.env.NEXT_PUBLIC_ERROR_PREVIEW==='true'&&['localhost','127.0.0.1'].includes(window.location.hostname)&&new URLSearchParams(window.location.search).has('assistantMock');
   const response=await requestAssistant({query:submitted},{...(provider&&!localScenario?{provider,catalog:tools}:assistantScenarioOptions(scenario,tools)),signal:controller.signal,attempt:++attempts.current,onSlow:()=>{if(request.current===controller&&!controller.signal.aborted)setSlow(true);}});
   if(controller.signal.aborted)return;
   setOriginalPrompt(submitted);setAssistantResponse(response);dispatchPresentation({type:'success'});
   setQuery(response.status==='needs_clarification'?submitted:'');
  }catch(error){if(controller.signal.aborted||error.name==='AbortError')return;dispatchPresentation({type:'failure'});setError(error.code||'technical_error');setCanRetry(getAssistantError(error.code).retry);}
  finally{if(request.current===controller){request.current=null;if(!controller.signal.aborted)setSlow(false);}}
 }

 return {query,setQuery,error,setError,assistantResponse,originalPrompt,slow,canRetry,setCanRetry,resultHeading,finished,pending,expanded,hasResult,phase,isDetail,input,newArchitecture,submit};
}
