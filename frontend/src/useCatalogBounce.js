import {useEffect} from 'react';

// Pull the catalog as one surface; never scale its text or intercept scrolling.
export function useCatalogBounce(isDetail){
 useEffect(()=>{
  if(isDetail)return;
  const shell=document.querySelector('#landing-view .catalog-shell');
  if(!shell)return;
  const motion=matchMedia('(prefers-reduced-motion: no-preference)');
  let frame=0,last=0,offset=0,velocity=0,pull=0,previous=Math.max(0,window.scrollY),lastWheel=-Infinity;
  const eligible=()=>{if(document.documentElement.classList.contains('tool-modal-open')||shell.closest('[data-layout-moving="true"]'))return false;const top=shell.getBoundingClientRect().top-offset;return top>=-56&&top<window.innerHeight;};
  const reset=()=>{cancelAnimationFrame(frame);frame=0;last=0;offset=velocity=pull=0;previous=Math.max(0,window.scrollY);shell.style.removeProperty('--catalog-pull-y');shell.removeAttribute('data-bouncing');};
  const tick=now=>{
   frame=0;
   if(!motion.matches||document.hidden||!eligible()){reset();return;}
   // Integrate elapsed time in small steps, so dropped frames do not slow time.
   let remaining=Math.min(.25,(now-(last||now-16))/1000);last=now;
   while(remaining>0){
    const dt=Math.min(1/120,remaining);remaining-=dt;
    pull*=Math.exp(-dt/.06);
    velocity+=(480*(pull-offset)-28*velocity)*dt;
    offset+=velocity*dt;
    if(offset>22){offset=22;velocity=Math.min(0,velocity);}
    if(offset< -2){offset=-2;velocity=Math.max(0,velocity);}
   }
   shell.style.setProperty('--catalog-pull-y',`${offset.toFixed(2)}px`);
   if(pull<.15&&Math.abs(offset)<.15&&Math.abs(velocity)<2){reset();return;}
   frame=requestAnimationFrame(tick);
  };
  const excite=distance=>{
   if(!motion.matches||document.hidden||!eligible()||distance<=0)return;
   pull=Math.min(22,pull+Math.min(12,distance*.18));
   shell.dataset.bouncing='true';if(!frame)frame=requestAnimationFrame(tick);
  };
  const scroll=()=>{const y=Math.max(0,window.scrollY),delta=previous-y;previous=y;if(delta>0)excite(delta);else if(delta<0)pull=0;};
  const wheel=event=>{
   // Only a fresh wheel gesture may pull at the top; ignore its inertia tail.
   const now=performance.now(),fresh=now-lastWheel>180;lastWheel=now;
   if(window.scrollY>0||event.deltaY>=0||event.ctrlKey||!fresh)return;
   if(event.target.closest?.('textarea,pre,input,[role="scrollbar"]'))return;
   const distance=-event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?window.innerHeight:1);excite(distance);
  };
  const visibility=()=>{if(document.hidden)reset();};
  window.addEventListener('scroll',scroll,{passive:true});window.addEventListener('wheel',wheel,{passive:true});window.addEventListener('blur',reset);window.addEventListener('hashchange',reset);window.addEventListener('resize',reset);motion.addEventListener('change',reset);document.addEventListener('visibilitychange',visibility);
  return()=>{reset();window.removeEventListener('scroll',scroll);window.removeEventListener('wheel',wheel);window.removeEventListener('blur',reset);window.removeEventListener('hashchange',reset);window.removeEventListener('resize',reset);motion.removeEventListener('change',reset);document.removeEventListener('visibilitychange',visibility);};
 },[isDetail]);
}
