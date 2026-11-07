import {useLayoutEffect,useRef,useCallback} from 'react';
import {promptMotion} from './promptPresentation.mjs';

// Measure the real composer before the first reflow. Animate dimensions, never glyph scale.
export function usePromptLayout(expanded,inputRef,isDetail){
 const formRef=useRef(null),timer=useRef(0),frame=useRef(0),previous=useRef(false);
 const prepare=useCallback(()=>{
  const form=inputRef.current?.closest('form');if(!form||previous.current)return;
  formRef.current=form;
  const slot=form.closest('.prompt-form-slot');
  if(slot){const rect=form.getBoundingClientRect();slot.dataset.dockOrigin=JSON.stringify({left:rect.left,top:rect.top,height:rect.height});}
  form.style.setProperty('--composer-height',`${form.getBoundingClientRect().height}px`);
  document.querySelector('#landing-view')?.setAttribute('data-layout-moving','true');
 },[inputRef]);
 useLayoutEffect(()=>{
  if(isDetail)return;
  if(!expanded){previous.current=false;return;}
  if(previous.current)return;previous.current=true;
  const form=formRef.current??inputRef.current?.closest('form');if(!form)return;
  const host=form.closest('#landing-view');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const finish=()=>{host?.removeAttribute('data-layout-moving');};
  const observer=new ResizeObserver(()=>{if(reduced.matches)finish();});observer.observe(form);
  const onMotion=()=>{if(reduced.matches){form.style.setProperty('--composer-height','80px');finish();}};
  reduced.addEventListener('change',onMotion);
  if(reduced.matches){form.style.setProperty('--composer-height','80px');finish();}
  else frame.current=requestAnimationFrame(()=>{form.style.setProperty('--composer-height','80px');timer.current=window.setTimeout(finish,promptMotion.layout);});
  return()=>{cancelAnimationFrame(frame.current);clearTimeout(timer.current);observer.disconnect();reduced.removeEventListener('change',onMotion);finish();};
 },[expanded,inputRef,isDetail]);
 return prepare;
}
