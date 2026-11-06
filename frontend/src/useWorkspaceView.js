import {useCallback,useEffect,useLayoutEffect,useRef,useState} from 'react';

// Keep both surfaces mounted: filtering, results and drafts belong to their view.
export function useWorkspaceView(pending){
 const [active,setActive]=useState(false);
 const [view,setView]=useState('assistant');
 const current=useRef('assistant'),positions=useRef({assistant:0,catalog:0}),restore=useRef(false);
 const switchView=useCallback(next=>{
  if(next===current.current)return;
  positions.current[current.current]=window.scrollY;
  current.current=next;restore.current=true;setView(next);
 },[]);
 useLayoutEffect(()=>{if(pending&&!active){positions.current.assistant=0;restore.current=true;setActive(true);}},[pending,active]);
 useEffect(()=>{
  if(!active)return;
  const sync=()=>{if(location.hash==='#catalogo')switchView('catalog');else if(location.hash==='#asistente'||location.hash==='#')switchView('assistant');};
  window.addEventListener('hashchange',sync);
  return()=>window.removeEventListener('hashchange',sync);
 },[active,switchView]);
 useLayoutEffect(()=>{
  if(!restore.current)return;restore.current=false;
  window.scrollTo({top:positions.current[view],behavior:'instant'});
 },[active,view]);
 const navigate=useCallback(event=>{
  if(!active)return;
  event.preventDefault();
  const next=current.current==='assistant'?'catalog':'assistant';
  history.pushState(null,'',next==='catalog'?'#catalogo':'#asistente');switchView(next);
 },[active,switchView]);
 const reset=useCallback(()=>{
  positions.current.assistant=0;current.current='assistant';restore.current=true;
  history.replaceState(history.state,'','#asistente');
  setView('assistant');setActive(false);
 },[]);
 return {active,view,navigate,reset};
}
