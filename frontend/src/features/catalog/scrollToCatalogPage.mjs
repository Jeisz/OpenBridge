// Bound page navigation independently of the browser's distance-based duration.
export function scrollToCatalogPage(top){
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 if(motion.matches){window.scrollTo({top,behavior:'instant'});return ()=>{};}
 const from=window.scrollY,start=performance.now(),duration=440;
 let frame=0;
 const events=['wheel','touchstart','pointerdown','keydown','resize'];
 const stop=()=>{
  cancelAnimationFrame(frame);
  events.forEach(event=>window.removeEventListener(event,stop,true));
  motion.removeEventListener('change',stop);
 };
 const tick=now=>{
  const progress=Math.min(1,(now-start)/duration);
  const eased=1-Math.pow(1-progress,3);
  window.scrollTo({top:from+(top-from)*eased,behavior:'instant'});
  if(progress<1)frame=requestAnimationFrame(tick);else stop();
 };
 events.forEach(event=>window.addEventListener(event,stop,{capture:true,passive:true}));
 motion.addEventListener('change',stop);
 frame=requestAnimationFrame(tick);
 return stop;
}
