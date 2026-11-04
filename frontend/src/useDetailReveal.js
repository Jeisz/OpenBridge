import {useLayoutEffect} from 'react';

// Each group has its own short stagger; below-the-fold content starts on entry.
export function useDetailReveal(frame,id){
 useLayoutEffect(()=>{
  const root=frame.current?.querySelector('.tool-modal-scroll');
  if(!root)return;
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  if(motion.matches)return;
  const started=performance.now(), animations=new Map(), delays=new Map();
  const groups=[
   [...root.querySelectorAll('.detail-overview>section>h2,.detail-summary,.detail-overview>section>h3,.detail-features>li')],
   [...root.querySelectorAll('.detail-health,.detail-metrics dl>div,.detail-metrics>.catalog-snapshot-note')],
   [...root.querySelectorAll('.detail-integrations>h2,.detail-integrations>p')],
   ...[...root.querySelectorAll('.integration')].map(group=>[...group.querySelectorAll('.integration-heading,.integration>p,.integration-facts>div,.snippet,.integration-docs')])
  ];
  groups.forEach(group=>group.forEach((element,index)=>{
   delays.set(element,Math.min(index*28,168));
   const animation=element.animate([{opacity:0,translate:'0 7px'},{opacity:1,translate:'0 0'}],{duration:220,easing:'cubic-bezier(.22,1,.36,1)',fill:'both'});
   animation.pause();animations.set(element,animation);
  }));
  const reveal=element=>{
   const animation=animations.get(element);if(!animation)return;
   animation.effect.updateTiming({delay:Math.max(0,140-(performance.now()-started))+delays.get(element)});
   animation.onfinish=()=>{animation.cancel();animations.delete(element);};
   animation.play();observer.unobserve(element);
  };
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting)reveal(entry.target);}),{root,threshold:0.05});
  animations.forEach((_,element)=>observer.observe(element));
  const showFocused=event=>animations.forEach((animation,element)=>{if(element.contains(event.target)){animation.cancel();animations.delete(element);observer.unobserve(element);}});
  const stop=()=>{observer.disconnect();animations.forEach(animation=>animation.cancel());animations.clear();};
  const reduce=()=>{if(motion.matches)stop();};
  root.addEventListener('focusin',showFocused);motion.addEventListener('change',reduce);
  return()=>{stop();root.removeEventListener('focusin',showFocused);motion.removeEventListener('change',reduce);};
 },[frame,id]);
}
