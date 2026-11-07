import React,{useEffect,useId,useRef,useState} from 'react';
import {Check,ChevronDown} from 'lucide-react';

export function FilterSelect({label,value,onChange,options}){
 const id=useId(),root=useRef(null),trigger=useRef(null),items=useRef([]),search=useRef({text:'',time:0});
 const [open,setOpen]=useState(false),[cursor,setCursor]=useState(0);
 const selected=Math.max(0,options.findIndex(option=>option.value===value));
 useEffect(()=>{
  if(!open)return;
  items.current[cursor]?.focus({preventScroll:true});
  items.current[cursor]?.scrollIntoView({block:'nearest'});
 },[open,cursor]);
 useEffect(()=>{
  if(!open)return;
  const outside=event=>{if(!root.current?.contains(event.target))setOpen(false);};
  document.addEventListener('pointerdown',outside);
  return()=>document.removeEventListener('pointerdown',outside);
 },[open]);
 function close(){setOpen(false);trigger.current?.focus({preventScroll:true});}
 function choose(index){onChange(options[index].value);close();}
 function keyDown(event){
  if(event.key==='Escape'){event.preventDefault();event.stopPropagation();close();return;}
  let next;
  if(event.key==='ArrowDown')next=(cursor+1)%options.length;
  if(event.key==='ArrowUp')next=(cursor-1+options.length)%options.length;
  if(event.key==='Home')next=0;
  if(event.key==='End')next=options.length-1;
  if(next!==undefined){event.preventDefault();setCursor(next);return;}
  if(event.key==='Enter'||event.key===' '){event.preventDefault();choose(cursor);return;}
  if(event.key.length===1&&!event.ctrlKey&&!event.metaKey&&!event.altKey){
   event.preventDefault();
   const now=Date.now();search.current={text:(now-search.current.time<700?search.current.text:'')+event.key.toLocaleLowerCase(),time:now};
   const match=options.findIndex(option=>option.label.toLocaleLowerCase().startsWith(search.current.text));
   if(match>=0)setCursor(match);
  }
 }
 return <div className="catalog-filter" ref={root} onBlur={event=>{if(!event.currentTarget.contains(event.relatedTarget))setOpen(false);}}>
  <span className="catalog-filter-label" id={`${id}-label`}>{label}</span>
  <button ref={trigger} type="button" className="catalog-filter-trigger" aria-labelledby={`${id}-label ${id}-value`} aria-haspopup="listbox" aria-expanded={open} aria-controls={open?`${id}-list`:undefined} onClick={()=>{setCursor(selected);setOpen(!open);}} onKeyDown={event=>{if(['ArrowDown','ArrowUp'].includes(event.key)){event.preventDefault();setCursor(selected);setOpen(true);}}}>
   <span id={`${id}-value`}>{options[selected]?.label}</span><ChevronDown size={16} aria-hidden="true"/>
  </button>
  {open&&<ul className="catalog-filter-menu" id={`${id}-list`} role="listbox" aria-labelledby={`${id}-label`} onKeyDown={keyDown}>
   {options.map((option,index)=><li key={option.value} ref={node=>{items.current[index]=node;}} role="option" aria-selected={value===option.value} tabIndex={cursor===index?0:-1} onFocus={()=>setCursor(index)} onClick={()=>choose(index)}><span>{option.label}</span>{value===option.value&&<Check size={16} aria-hidden="true"/>}</li>)}
  </ul>}
 </div>;
}
