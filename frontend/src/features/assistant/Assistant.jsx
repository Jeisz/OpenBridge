import React from 'react';
import {PromptSuggestions} from './PromptSuggestions';
import {getAssistantError} from '../../errorPresentation.mjs';
import {ArrowUpRight} from 'lucide-react';
import {RevealHeading} from '../../PageReveal';
import {HeroLights} from '../../HeroLights';
import {promptMotion} from '../../promptPresentation.mjs';
import {StackProposal} from './StackProposal';
import {PromptComposer} from './PromptComposer';
export function Assistant({flow}){
 const {assistantResponse,originalPrompt,slow,resultHeading,finished,pending,expanded,hasResult,input,newArchitecture,error,canRetry}=flow;
 const errorCopy=error?getAssistantError(error):null;
 const headerActive=expanded||Boolean(error);
 const heading=pending?'Preparando tu stack':errorCopy?errorCopy.title:assistantResponse?.title||({needs_clarification:'Precisemos tu idea',no_evidence:'Sin evidencia suficiente'}[assistantResponse?.status]||'Tu arquitectura');
 const description=pending?(slow?'La solicitud está tardando más de lo habitual.':'Estamos generando tu propuesta.'):errorCopy?errorCopy.description:assistantResponse?.summary||'';
 return (<div className="hero"><HeroLights inputRef={input}/><section id="asistente"><div className={'hero-inner'+(expanded?' has-architecture':'')+(error?' has-request-error':'')} style={Object.fromEntries([...Object.entries(promptMotion).filter(([key])=>key!=='ease').map(([key,value])=>[`--prompt-${key}-duration`,`${value}ms`]),['--prompt-ease',promptMotion.ease]])}>
 <div className="prompt-heading"><div className="prompt-heading-initial" aria-hidden={headerActive}><RevealHeading as="h1" text="De tu idea a tu stack" gradientWord="stack" mobileBreak/></div><h1 ref={resultHeading} tabIndex={-1} className="prompt-heading-result" aria-hidden={!headerActive}><span className={'assistant-heading-content'+(pending?' is-pending':'')}><span className="assistant-light-loader" aria-hidden="true"/><span key={heading} className="assistant-heading-copy">{pending?<>Preparando tu <span className="gradient-word"><span className="reveal-letter" data-glow="stack" style={{'--word-play-state':'running'}}>stack</span></span></>:heading}</span></span></h1></div>
 <div className="prompt-intro" role="status" aria-live="polite" aria-atomic="true"><p className="intro intro-initial" aria-hidden={headerActive}>Describe lo que quieres construir y descubre las herramientas open source para hacerlo realidad.</p><p id="prompt-error" className="intro intro-result" aria-hidden={!headerActive}><span key={description} className="assistant-heading-copy">{description}</span></p></div>
 {finished&&<div className="stack-new-action"><button type="button" className="new-architecture" onClick={newArchitecture}>Crear nueva arquitectura <ArrowUpRight size={16}/></button></div>}
 <StackProposal expanded={expanded} pending={pending} hasResult={hasResult} slow={slow} response={assistantResponse}/>

 <PromptComposer {...flow}/>
 {finished&&<div className="architecture-result-tools"><details className="original-prompt"><summary>Tu idea original</summary><p>{originalPrompt}</p></details></div>}

 </div><PromptSuggestions flow={flow}/></section>
 </div>
);
}
