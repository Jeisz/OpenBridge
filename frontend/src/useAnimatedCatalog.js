import {useLayoutEffect,useRef,useState} from 'react';

export function useAnimatedCatalog(tools){
 const [displayed,setDisplayed]=useState(tools);
 const latest=useRef(tools),positions=useRef(new Map());latest.current=tools;
 const key=JSON.stringify(tools.map(tool=>String(tool.id)));
 useLayoutEffect(()=>{
  const grid=document.querySelector('#catalogo .grid:not(.catalog-skeleton .grid)');
  if(!grid)return;
  const cards=[...grid.children],wanted=new Set(latest.current.map(tool=>String(tool.id)));
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  const columns=getComputedStyle(grid).gridTemplateColumns.split(' ').length;
  let delay=0,removed=false,timer;
  cards.forEach((card,index)=>{
   delete card.dataset.exiting;card.inert=false;
   if(wanted.has(card.dataset.toolId))return;
   removed=true;
   const rect=card.getBoundingClientRect();
   const onScreen=rect.bottom>0&&rect.top<innerHeight;
   const row=Math.floor(index/columns),rowSize=Math.min(columns,cards.length-row*columns);
   const stagger=onScreen?Math.min(row*60,120)+(rowSize-1-index%columns)*40:0;
   card.style.setProperty('--exit-delay',`${stagger}ms`);
   card.getAnimations().filter(animation=>animation.effect?.getKeyframes().some(frame=>frame.opacity!==undefined)).forEach(animation=>animation.cancel());
   card.dataset.exiting='true';card.inert=true;
   if(onScreen)delay=Math.max(delay,240+stagger);
  });
  const commit=()=>{
   const mounted=new Set(cards.map(card=>card.dataset.toolId));
   grid.dataset.restoring=String(cards.length>0&&latest.current.some(tool=>!mounted.has(String(tool.id))));
   positions.current=new Map(cards.filter(card=>wanted.has(card.dataset.toolId)).map(card=>[card.dataset.toolId,card.getBoundingClientRect()]));
   setDisplayed(latest.current);
  };
  if(removed&&!motion.matches&&delay)timer=setTimeout(commit,delay);else commit();
  const reduce=()=>{if(motion.matches){clearTimeout(timer);commit();}};
  motion.addEventListener('change',reduce);
  return()=>{clearTimeout(timer);motion.removeEventListener('change',reduce);cards.forEach(card=>{delete card.dataset.exiting;card.inert=false;});};
 },[key]);
 useLayoutEffect(()=>{
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const animations=[];
  document.querySelectorAll('#catalogo .grid > .tool-card').forEach(card=>{
   const before=positions.current.get(card.dataset.toolId);
   if(!before)return;
   const after=card.getBoundingClientRect(),x=before.left-after.left,y=before.top-after.top;
   if(x||y)animations.push(card.animate([{transform:`translate(${x}px,${y}px)`},{transform:'translate(0,0)'}],{duration:420,easing:'cubic-bezier(.22,1,.36,1)'}));
  });
  positions.current.clear();
  return()=>animations.forEach(animation=>animation.cancel());
 },[displayed]);
 // Publish the first results in the same render that removes the skeleton.
 // An empty intermediate grid can clamp the document scroll position.
 return displayed.length===0?tools:displayed;
}
