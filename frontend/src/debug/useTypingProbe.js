import {useEffect} from 'react';
// Local comparison harness. No UI, network requests or prompt contents recorded.
export function useTypingProbe(){
 useEffect(()=>{
  if(!['localhost','127.0.0.1'].includes(location.hostname)||!['borderPerf','typingTest'].some(key=>new URLSearchParams(location.search).has(key)))return;
  const groups={};const frames=new Set();let disposed=false;
  function next(callback){const id=requestAnimationFrame(()=>{frames.delete(id);if(!disposed)callback();});frames.add(id);}
  function onInput(event){
   if(!['prompt','typing-control'].includes(event.target.id))return;
   const id=event.target.id;const samples=groups[id]||(groups[id]=[]);
   const start=performance.now();
   next(()=>next(()=>{
    samples.push(performance.now()-start);
    if(samples.length>500)samples.shift();
    const sorted=[...samples].sort((a,b)=>a-b);
    event.target.dataset.typingProbe=JSON.stringify({count:sorted.length,p50:Math.round(sorted[Math.floor(sorted.length*.5)]),p95:Math.round(sorted[Math.floor(sorted.length*.95)]),max:Math.round(sorted.at(-1))});
   }));
  }
  document.addEventListener('input',onInput,true);
  return()=>{disposed=true;frames.forEach(cancelAnimationFrame);document.removeEventListener('input',onInput,true);document.querySelectorAll('[data-typing-probe]').forEach(el=>delete el.dataset.typingProbe);};
 },[]);
}
