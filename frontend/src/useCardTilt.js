import {registerCardInteraction} from './cardInteractionEvents.mjs';
import {useEffect, useRef} from 'react';

// Keep hover on an inner surface so filtering and entrance transforms stay independent.
export function useCardTilt() {
 const ref = useRef(null);
 useEffect(() => {
  const card = ref.current;
  const surface = card.querySelector('.card-surface');
  const enabled = matchMedia('(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)');
  const motion = matchMedia('(prefers-reduced-motion: no-preference)');
  let releaseTimer = 0, pressedAt = 0, pointerId = null, pressedKey = null;
  const release = () => {clearTimeout(releaseTimer);surface.removeAttribute('data-pressed');pointerId=null;pressedKey=null;if(!surface.hasAttribute('data-hover'))shared.deactivate();};
  const press = () => {
   if (!motion.matches || card.dataset.exiting === 'true') return;
   shared.activate();
   clearTimeout(releaseTimer);pressedAt=performance.now();surface.dataset.pressed='true';
  };
  const finish = () => {
   pointerId=null;pressedKey=null;
   releaseTimer=window.setTimeout(release,Math.max(0,160-(performance.now()-pressedAt)));
  };
  const down = event => {if(event.isPrimary && event.button===0){pointerId=event.pointerId;press();}};
  const up = event => {if(event.pointerId===pointerId)finish();};
  const keydown = event => {
   if(event.repeat || !event.target.closest('a,button,summary'))return;
   if(event.key==='Enter' || (event.key===' ' && event.target.closest('button,summary'))){pressedKey=event.key;press();}
  };
  const keyup = event => {if(event.key===pressedKey)finish();};
  let frame = 0;
  let x = .5, y = .5, edgeIntensity = 0;
  const reset = () => {
   shared.deactivate();
   release();
   cancelAnimationFrame(frame);
   frame = 0;
   surface.removeAttribute('data-hover');
   surface.style.removeProperty('transform');
  };
  const move = event => {
   if (!enabled.matches || event.pointerType === 'touch' || card.dataset.exiting === 'true') return;
   shared.activate();
   const bounds = card.getBoundingClientRect();
   x = Math.max(0, Math.min(1, (event.clientX - bounds.left) / bounds.width));
   y = Math.max(0, Math.min(1, (event.clientY - bounds.top) / bounds.height));
   const edgeDistance = Math.min(x * bounds.width, (1 - x) * bounds.width, y * bounds.height, (1 - y) * bounds.height);
   edgeIntensity = Math.max(0, 1 - edgeDistance / 100);
   if (frame) return;
   frame = requestAnimationFrame(() => {
    frame = 0;
    surface.dataset.hover = 'true';
    surface.style.transform = `perspective(1100px) rotateX(${( .5-y)*4}deg) rotateY(${(x-.5)*4}deg)`;
    surface.style.setProperty('--glare-x', `${x*100}%`);
    surface.style.setProperty('--glare-y', `${y*100}%`);
    surface.style.setProperty('--edge-intensity', edgeIntensity.toFixed(3));
   });
  };
  const shared=registerCardInteraction({reset,up,keyup});
  card.addEventListener('pointerdown', down, {passive:true});
  card.addEventListener('keydown', keydown);
  card.addEventListener('focusout', release);
  card.addEventListener('cardpressreset', release);
  motion.addEventListener('change', release);
  card.addEventListener('pointermove', move);
  card.addEventListener('pointerleave', reset);
  card.addEventListener('pointercancel', reset);
  enabled.addEventListener('change', reset);
  return () => {
   reset();shared.dispose();
   card.removeEventListener('pointerdown', down);
   card.removeEventListener('keydown', keydown);
   card.removeEventListener('focusout', release);
   card.removeEventListener('cardpressreset', release);
   motion.removeEventListener('change', release);
   card.removeEventListener('pointermove', move);
   card.removeEventListener('pointerleave', reset);
   card.removeEventListener('pointercancel', reset);
   enabled.removeEventListener('change', reset);
  };
 }, []);
 return ref;
}
