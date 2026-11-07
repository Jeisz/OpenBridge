import React,{useEffect,useState} from 'react';

const words=['Maquinando…','Destilando…','Fusionando…','Fraguando…','Alquimizando…'];

export function WorkingWords(){
 const [step,setStep]=useState(0);
 useEffect(()=>{
  const timer=setInterval(()=>setStep(value=>value+1),5000);
  return()=>clearInterval(timer);
 },[]);
 const renderWord=(word,outgoing)=><span className={'working-word '+(outgoing?'is-leaving':'is-entering')}>
  {[...word].map((letter,index)=><span key={index} style={{'--letter-delay':`${index*16}ms`}}>{letter}</span>)}
 </span>;
 return <>
  <span className="sr-only">Preparando tu propuesta.</span>
  <span className="working-words" aria-hidden="true" key={step}>
   {step>0&&renderWord(words[(step-1)%words.length],true)}
   {renderWord(words[step%words.length],false)}
  </span>
 </>;
}
