const easing='cubic-bezier(.22,1,.36,1)';
export const bounds=el=>{const r=el.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height};};
const geometry=r=>({left:`${r.left}px`,top:`${r.top}px`,width:`${r.width}px`,height:`${r.height}px`});
function textStyle(el){const s=getComputedStyle(el);return {fontFamily:s.fontFamily,fontSize:s.fontSize,fontWeight:s.fontWeight,fontStyle:s.fontStyle,lineHeight:s.lineHeight,letterSpacing:s.letterSpacing,color:s.color};}
export function captureCover(el){
 if(!el)return null;
 const card=el.closest('.tool-card');
 if(card){
  card.dispatchEvent(new Event('cardpressreset'));
  const surface=card.querySelector('.card-surface');
  surface.style.setProperty('transition','none');
  surface.style.setProperty('scale','1');
  surface.getBoundingClientRect();
  surface.style.removeProperty('scale');
  surface.style.removeProperty('transition');
 }

 const style=getComputedStyle(el),items=[];
 function add(key,node){if(!node)return;const s=getComputedStyle(node),r=bounds(node);if(r.width<2||r.height<2)return;items.push({key,node:node.cloneNode(true),rect:r,style:{...textStyle(node),filter:s.filter,opacity:s.opacity,background:s.background,borderRadius:s.borderRadius,padding:s.padding,objectFit:s.objectFit,textAlign:s.textAlign}});}
 add('title',el.querySelector('h1,h3'));
 add('logo',el.querySelector('.tool-logo img,.brand-logo,.brand-initials,.detail-identity>img'));
 add('watermark',el.querySelector('.card-watermark img,.brand-watermark,.detail-watermark'));
 el.querySelectorAll('.tool-tags>span').forEach(tag=>add(`tag-${tag.textContent.trim()}`,tag));
 // Paragraphs keep their own wrapping and hand off without crossing words.
 add('description',el.querySelector('p'));
 const isCard=el.matches('.tool-card-intro');
 const backgroundHost=isCard?el.closest('.card-surface'):el;
 const panel=isCard?card?.querySelector('.tool-card-details'):el.closest('.tool-detail')?.querySelector('.detail-body');
 const rect=bounds(el);
 let join=null;
 if(panel){
  const panelStyle=getComputedStyle(panel),panelRect=bounds(panel);
  const radius=Math.max(parseFloat(panelStyle.borderTopLeftRadius)||0,parseFloat(panelStyle.borderTopRightRadius)||0);
  if(isCard)rect.height=Math.max(rect.height,panelRect.top-rect.top+radius);
  join={height:Math.max(0,rect.top+rect.height-panelRect.top),left:panelStyle.borderTopLeftRadius,right:panelStyle.borderTopRightRadius,background:panelStyle.backgroundColor};
 }
 return {rect,background:getComputedStyle(backgroundHost).background,backgroundSize:`${bounds(backgroundHost).width}px ${bounds(backgroundHost).height}px`,items,join};
}
export function animateCover(start,end,target,{opening,onFinish,outerStart,outerEnd}){
 const duration=opening?400:460,animations=[],nodes=[];
 document.documentElement.classList.add('cover-in-flight');
 const envelope=document.createElement('div');
 Object.assign(envelope.style,{position:'fixed',inset:'0',zIndex:'110',pointerEvents:'none'});
 envelope.setAttribute('aria-hidden','true');envelope.inert=true;document.body.append(envelope);nodes.push(envelope);
 if(outerStart&&outerEnd){
  const clip=({rect,radius})=>`inset(${rect.top}px ${innerWidth-rect.left-rect.width}px ${innerHeight-rect.top-rect.height}px ${rect.left}px round ${radius})`;
  const a=envelope.animate([{clipPath:clip(outerStart)},{clipPath:clip(outerEnd)}],{duration,easing,fill:'both'});animations.push(a);
 }
 const surface=document.createElement('div');surface.className='cover-transition';
 Object.assign(surface.style,{position:'fixed',zIndex:'110',pointerEvents:'none',background:start.background,backgroundSize:start.backgroundSize,backgroundRepeat:'no-repeat',overflow:'hidden',borderRadius:'0'});
 surface.setAttribute('aria-hidden','true');surface.inert=true;envelope.append(surface);nodes.push(surface);
 const animate=(node,frames,options={})=>{const a=node.animate(frames,{duration,easing,fill:'both',...options});animations.push(a);return a;};
 const cover=animate(surface,[{...geometry(start.rect),backgroundSize:start.backgroundSize},{...geometry(end.rect),backgroundSize:end.backgroundSize}]);
 // Crossfade the two authentic backgrounds without replacing the cover at the end.
 const finishBackground=document.createElement('div');Object.assign(finishBackground.style,{position:'absolute',inset:'0',background:end.background,backgroundSize:end.backgroundSize});surface.append(finishBackground);animate(finishBackground,[{opacity:0},{opacity:1}]);
 // Only the outer envelope rounds the sheet. The cover has one neutral join,
 // sampled from the real information panel, never its own rounded rectangle.
 if(start.join&&end.join){
  const join=document.createElement('div');join.className='cover-transition-join';
  Object.assign(join.style,{position:'absolute',left:'0',right:'0',zIndex:'2',background:start.join.background});surface.append(join);
  const shape=entry=>({height:`${entry.height+64}px`,bottom:'-64px',borderRadius:`${entry.left} ${entry.right} 0 0`,background:entry.background});
  animate(join,[shape(start.join),shape(end.join)]);
 }
 for(const item of start.items){
  const dest=end.items.find(i=>i.key===item.key);if(!dest)continue;
  if(item.key==='description'){
   const addParagraph=(entry)=>{
    const node=entry.node;node.removeAttribute('id');node.removeAttribute('class');node.setAttribute('aria-hidden','true');node.inert=true;
    Object.assign(node.style,{...entry.style,...geometry(entry.rect),position:'fixed',zIndex:'111',margin:'0',boxSizing:'border-box',pointerEvents:'none',whiteSpace:'normal',maxWidth:'none',minHeight:'0'});
    envelope.append(node);nodes.push(node);return node;
   };
   animate(addParagraph(item),[{opacity:1},{opacity:0}],{duration:120});
   animate(addParagraph(dest),[{opacity:0,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}],{delay:opening?140:180,duration:220,fill:'both'});
   continue;
  }
  const piece=item.node;piece.removeAttribute('id');piece.removeAttribute('class');piece.setAttribute('aria-hidden','true');piece.inert=true;
  Object.assign(piece.style,{...item.style,position:'fixed',zIndex:item.key==='watermark'?'110':'111',margin:'0',boxSizing:'border-box',pointerEvents:'none',whiteSpace:'nowrap',transform:'none',minHeight:'0',maxWidth:'none',display:'block'});
  if(item.key==='watermark'){
   // Keep the artwork inside the changing cover, including its rounded corners.
   piece.style.position='absolute';piece.style.zIndex='0';surface.append(piece);
   const local=(r,parent)=>({...r,left:r.left-parent.left,top:r.top-parent.top});
   animate(piece,[{...geometry(local(item.rect,start.rect)),opacity:item.style.opacity},{...geometry(local(dest.rect,end.rect)),opacity:dest.style.opacity}]);
  }else{
   envelope.append(piece);nodes.push(piece);
   animate(piece,[{...geometry(item.rect),...item.style},{...geometry(dest.rect),...dest.style}]);
  }
 }
 target.style.visibility='hidden';
 let done=false;
 const dispose=()=>{if(done)return;done=true;document.documentElement.classList.remove('cover-in-flight');target.style.visibility='';animations.forEach(a=>a.cancel());nodes.forEach(n=>n.remove());};
 cover.finished.then(()=>{dispose();onFinish();}).catch(()=>{});
 return dispose;
}
