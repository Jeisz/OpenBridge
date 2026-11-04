import {useDetailReveal} from './useDetailReveal';
import {createModalScrollSync} from './modalScrollSync.mjs';
import {useLayoutEffect,useRef} from 'react';
import {X} from 'lucide-react';
import {ToolDetail} from './ToolDetail';

export function ToolModal({id,onClose}){
 const frame=useRef(null),rail=useRef(null);
 useDetailReveal(frame,id);
 useLayoutEffect(()=>{
  const root=document.documentElement;
  const previousOverflow=root.style.overflow;
  const previousPadding=root.style.paddingRight;
  const gutter=Math.max(0,innerWidth-root.clientWidth);
  if(gutter)root.style.paddingRight=`${parseFloat(getComputedStyle(root).paddingRight)+gutter}px`;
  root.style.overflow='hidden';
  root.classList.add('tool-modal-open');
  const scrollport=frame.current.querySelector('.tool-modal-scroll');
  const scrollbar=rail.current;
  const {syncFromContent,syncFromRail}=createModalScrollSync(scrollport,scrollbar);
  const measure=()=>{
   scrollbar.hidden=scrollport.scrollHeight<=scrollport.clientHeight+1;
   scrollbar.firstElementChild.style.height=`${scrollbar.clientHeight*scrollport.scrollHeight/Math.max(1,scrollport.clientHeight)}px`;
   syncFromContent();
  };
  measure();const observer=new ResizeObserver(measure);observer.observe(scrollport);observer.observe(scrollport.firstElementChild);
  scrollport.addEventListener('scroll',syncFromContent,{passive:true});scrollbar.addEventListener('scroll',syncFromRail,{passive:true});
  frame.current?.focus({preventScroll:true});
  const keydown=event=>{
   if(event.key==='Escape'){event.preventDefault();onClose();return;}
   if(event.key!=='Tab')return;
   const controls=[...frame.current.querySelectorAll('a[href],button:not([disabled]),textarea,input,select,[tabindex="0"]')].filter(el=>el.getClientRects().length&&!el.closest('[inert]'));
   const first=controls[0],last=controls.at(-1);
   if(!first){event.preventDefault();frame.current.focus();return;}
   if(event.shiftKey&&(document.activeElement===first||!controls.includes(document.activeElement))){event.preventDefault();last.focus();}
   else if(!event.shiftKey&&(document.activeElement===last||!controls.includes(document.activeElement))){event.preventDefault();first.focus();}
  };
  document.addEventListener('keydown',keydown);
  return()=>{observer.disconnect();scrollport.removeEventListener('scroll',syncFromContent);scrollbar.removeEventListener('scroll',syncFromRail);root.style.overflow=previousOverflow;root.style.paddingRight=previousPadding;root.classList.remove('tool-modal-open');document.removeEventListener('keydown',keydown);};
 },[id]);
 return <div className="tool-modal-overlay" onClick={event=>{if(event.target===event.currentTarget)onClose();}}>
  <div className="tool-modal-shell"><div ref={frame} className="tool-modal-frame" role="dialog" aria-modal="true" aria-labelledby="detail-title" tabIndex={-1}>
   <button className="tool-modal-close ui-wash" type="button" onClick={onClose} aria-label="Cerrar ficha técnica"><X size={20}/></button>
   <div className="tool-modal-scroll"><ToolDetail id={id} onBack={onClose}/></div>
  </div><div ref={rail} className="tool-modal-rail" aria-hidden="true" tabIndex={-1}><div/></div></div>
 </div>;
}
