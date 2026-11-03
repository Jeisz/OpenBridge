import {ButtonAppearance} from './ButtonAppearance';
import React,{useState} from 'react';
import {useExamplePlaceholder} from './useExamplePlaceholder';
import {ArrowUp,LoaderCircle} from 'lucide-react';
import {ElasticPromptBorder} from '../../ElasticPromptBorder';
import {PromptError} from '../../PromptError';
export function PromptComposer({query,error,canRetry,finished,pending,phase,isDetail,input,submit,setQuery,setError,setCanRetry}){
 return ( <div className={'prompt-form-slot'+(finished?' is-closed':'')} inert={finished?true:undefined} aria-hidden={finished}><div className="prompt-form-clip"><form className={'composer '+(error&&!canRetry?'invalid':'')} data-error={error?'true':undefined} onSubmit={submit}><ElasticPromptBorder/><span className="prompt-surface-glare" aria-hidden="true"/><label htmlFor="prompt" className="sr-only">Describe tu aplicación</label><PromptInput {...{query,error,canRetry,finished,pending,phase,isDetail,input,setQuery,setError,setCanRetry}}/><div className="composer-footer flex items-center justify-end gap-[10px]"><PromptError message={error} canRetry={canRetry&&!pending} onRetry={()=>submit()}/><button className="primary prompt-submit" aria-disabled={pending} type="submit" aria-label={phase==='loading'?'Generando propuesta':'Generar propuesta'} title={phase==='loading'?'Generando propuesta':'Generar propuesta'}><span className={'submit-symbol'+(pending?' is-pending':'')} aria-hidden="true"><ArrowUp className="submit-arrow" size={24} strokeWidth={2}/><LoaderCircle className="submit-spinner spin" size={22}/></span></button></div></form><ButtonAppearance/></div></div>
);
}

// Keep character-by-character updates inside the input, away from the page and shaders.
function PromptInput({query,error,canRetry,finished,pending,phase,isDetail,input,setQuery,setError,setCanRetry}){
 const [promptFocused,setPromptFocused]=useState(false);
 const placeholder=useExamplePlaceholder(finished||isDetail||promptFocused||Boolean(query)||pending||phase==='done',input);
 return (<textarea ref={input} id="prompt" value={query} readOnly={pending} aria-busy={pending} onKeyDown={e=>{if(e.key!=='Enter'||e.shiftKey||e.nativeEvent.isComposing||e.nativeEvent.keyCode===229)return;e.preventDefault();if(!pending&&!e.repeat)e.currentTarget.form?.requestSubmit();}} onChange={e=>{setQuery(e.target.value);setError('');setCanRetry(false);}} placeholder={placeholder} onFocus={()=>setPromptFocused(true)} onBlur={()=>setPromptFocused(false)} aria-describedby={error?"prompt-error":undefined} aria-invalid={!!error&&!canRetry}/>);
}
