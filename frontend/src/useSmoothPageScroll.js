import {useEffect} from 'react';

// Smooth wheel input only. Touch, keyboard and nested scroll areas stay native.
export function useSmoothPageScroll(paused){
 useEffect(()=>{
  if(paused)return;
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  let frame=0,target=scrollY,last=0,painted=scrollY;
  const stop=()=>{cancelAnimationFrame(frame);frame=0;target=painted=scrollY;last=0;};
  const max=()=>Math.max(0,document.documentElement.scrollHeight-innerHeight);
  const tick=now=>{
   const dt=Math.min(40,last?now-last:16);last=now;
   target=Math.max(0,Math.min(max(),target));
   const next=scrollY+(target-scrollY)*(1-Math.exp(-dt/85));
   painted=Math.abs(target-next)<.5?target:next;
   window.scrollTo({top:painted,behavior:'instant'});
   if(Math.abs(target-scrollY)>.5)frame=requestAnimationFrame(tick);else stop();
  };
  const wheel=event=>{
   if(motion.matches||event.defaultPrevented||!event.cancelable||event.ctrlKey||event.metaKey||Math.abs(event.deltaX)>Math.abs(event.deltaY))return;
   if(event.target.closest?.('textarea,input,select,pre,[contenteditable="true"],[role="dialog"],[role="menu"],[role="listbox"],[role="scrollbar"]')){stop();return;}
   for(let node=event.target;node instanceof Element&&node!==document.body;node=node.parentElement){
    if(/auto|scroll/.test(getComputedStyle(node).overflowY)&&node.scrollHeight>node.clientHeight+1){stop();return;}
   }
   const delta=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?innerHeight:1);
   if(!delta)return;
   // Keep ownership at the page edges: handing the first wheel event back
   // to the browser can switch the rest of a trackpad gesture to native scroll.
   event.preventDefault();
   if((scrollY<=0&&delta<0)||(scrollY>=max()-1&&delta>0)){stop();return;}
   if(!frame||Math.sign(delta)!==Math.sign(target-scrollY)){target=scrollY;}
   target=Math.max(0,Math.min(max(),target+delta));
   if(!frame){last=0;frame=requestAnimationFrame(tick);}
  };
  const scroll=()=>{if(frame&&Math.abs(scrollY-painted)>2)stop();};
  window.addEventListener('wheel',wheel,{passive:false});
  window.addEventListener('scroll',scroll,{passive:true});
  window.addEventListener('pointerdown',stop,{capture:true});
  window.addEventListener('keydown',stop);window.addEventListener('resize',stop);window.addEventListener('hashchange',stop);window.addEventListener('popstate',stop);motion.addEventListener('change',stop);
  return()=>{stop();window.removeEventListener('wheel',wheel);window.removeEventListener('scroll',scroll);window.removeEventListener('pointerdown',stop,{capture:true});window.removeEventListener('keydown',stop);window.removeEventListener('resize',stop);window.removeEventListener('hashchange',stop);window.removeEventListener('popstate',stop);motion.removeEventListener('change',stop);};
 },[paused]);
}
