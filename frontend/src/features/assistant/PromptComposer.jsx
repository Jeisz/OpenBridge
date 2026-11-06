import {ButtonAppearance} from './ButtonAppearance';
import React,{useState,useEffect,useLayoutEffect,useRef} from 'react';
import {useExamplePlaceholder} from './useExamplePlaceholder';
import {ArrowUp,Square} from 'lucide-react';
import {ElasticPromptBorder} from '../../ElasticPromptBorder';
import {PromptError} from '../../PromptError';
export function PromptComposer({query,error,canRetry,finished,pending,phase,isDetail,input,exampleReveal,submit,stop,workspace=false,setQuery,setError,setCanRetry}){
 return ( <div className="prompt-form-slot"><div className="prompt-form-clip"><form className={'composer '+(error&&!canRetry?'invalid':'')} data-error={error?'true':undefined} onSubmit={submit}><ElasticPromptBorder/><span className="prompt-surface-glare" aria-hidden="true"/><label htmlFor="prompt" className="sr-only">Describe tu aplicación</label><PromptInput {...{query,error,canRetry,finished,pending,phase,isDetail,input,exampleReveal,workspace,setQuery,setError,setCanRetry}}/><div className="composer-footer flex items-center justify-end gap-[10px]"><PromptError message={error} canRetry={canRetry&&!pending} onRetry={()=>submit()}/><button className="primary prompt-submit" type={pending?'button':'submit'} onClick={pending?event=>{event.preventDefault();stop();}:undefined} aria-label={pending?'Detener consulta':'Generar propuesta'} title={pending?'Detener consulta':'Generar propuesta'}><span className="submit-symbol" aria-hidden="true">{pending?<Square size={16} fill="currentColor" strokeWidth={0}/>:<ArrowUp className="submit-arrow" size={24} strokeWidth={2}/>}</span></button></div></form><ButtonAppearance/></div></div>
);
}

// Keep character-by-character updates inside the input, away from the page and shaders.
function PromptInput({query,error,canRetry,finished,pending,phase,isDetail,input,exampleReveal,workspace,setQuery,setError,setCanRetry}){
 const [promptFocused,setPromptFocused]=useState(false);
 const [dismissed,setDismissed]=useState(null);
 const overlay=useRef(null);
 const words=exampleReveal?.text.split(' ')||[];
 const active=Boolean(exampleReveal&&dismissed!==exampleReveal.id&&query===exampleReveal.text&&!pending&&!finished);
 useLayoutEffect(()=>{
  if(!active)return;
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){setDismissed(exampleReveal.id);return;}
  input.current.scrollTop=0;
  const style=getComputedStyle(input.current);
  for(const key of ['fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','paddingTop','paddingRight','paddingBottom','paddingLeft'])overlay.current.style[key]=style[key];
 },[active,exampleReveal,input]);
 useEffect(()=>{
  if(!active)return;
  const timer=setTimeout(()=>setDismissed(exampleReveal.id),360+Math.min(300,(words.length-1)*24));
  return()=>clearTimeout(timer);
 },[active,exampleReveal,words.length]);
 const stopReveal=()=>{if(exampleReveal)setDismissed(exampleReveal.id);};
 useLayoutEffect(()=>{
  const field=input.current;if(!field)return;
  field.style.height='0px';
  field.style.height=`${Math.max(workspace?24:108,Math.min(workspace?144:240,field.scrollHeight))}px`;
 },[query,input,workspace]);
 const placeholder=useExamplePlaceholder(finished||isDetail||promptFocused||Boolean(query)||pending||phase==='done',input);
 return (<div className="prompt-input-wrap"><textarea className={active?"is-example-revealing":undefined} onPointerDown={stopReveal} onScroll={stopReveal} ref={input} id="prompt" value={query} readOnly={pending} aria-busy={pending} onKeyDown={e=>{stopReveal();if(e.key!=='Enter'||e.shiftKey||e.nativeEvent.isComposing||e.nativeEvent.keyCode===229)return;e.preventDefault();if(!pending&&!e.repeat)e.currentTarget.form?.requestSubmit();}} onChange={e=>{stopReveal();setQuery(e.target.value);setError('');setCanRetry(false);}} placeholder={placeholder} onFocus={()=>setPromptFocused(true)} onBlur={()=>setPromptFocused(false)} aria-describedby={error?"prompt-error":undefined} aria-invalid={!!error&&!canRetry}/>{active&&<div ref={overlay} className="prompt-example-reveal" aria-hidden="true" key={exampleReveal.id}>{words.map((word,index)=><React.Fragment key={index}><span className="prompt-example-mask"><span style={{animationDelay:`${Math.min(300,index*24)}ms`}}>{word}</span></span>{index<words.length-1?' ':null}</React.Fragment>)}</div>}</div>);
}
