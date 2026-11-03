import {memo,useEffect,useRef} from 'react';
import {borderLightFrame} from './promptBorderGeometry.mjs';

export const ElasticPromptBorder=memo(function ElasticPromptBorder(){
 const root=useRef(null);
 useEffect(()=>{
  const svg=root.current,form=svg.parentElement;
  const paths=svg.querySelectorAll(':scope > path'),light=svg.querySelector('radialGradient');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)'),fine=matchMedia('(hover: hover) and (pointer: fine)');
  let rect,buttonBox,points=[],raf=0,last=0,disposed=false;
  let burstStart=null,releasing=false,side=0,sideX=0;
  let glowFrame=null,glowSettling=false;
  let x=0,y=0,tx=0,ty=0,strength=0,target=0,cx=0,cy=0;
  function paint(now=performance.now()){
   form.style.setProperty('--prompt-glare-x',`${cx}px`);
   form.style.setProperty('--prompt-glare-y',`${cy}px`);
   form.style.setProperty('--prompt-glare-opacity',form.contains(document.activeElement)?0:strength);
   form.style.removeProperty('translate');
   if(buttonBox){
    const bx=cx-buttonBox.x,by=cy-buttonBox.y;
    const distance=Math.hypot(bx-buttonBox.width/2,by-buttonBox.height/2);
    const reflection=form.contains(document.activeElement)?0:strength*Math.exp(-(distance*distance)/(2*150*150));
    form.style.setProperty('--submit-reflection',String(reflection*.18));
    form.style.setProperty('--submit-reflection-x',`${bx}px`);
    form.style.setProperty('--submit-reflection-y',`${by}px`);
   }
   const d=points.map(([px,py,nx,ny],i)=>{
    const pull=0;
    return `${i?'L':'M'}${(px+nx*pull).toFixed(2)},${(py+ny*pull).toFixed(2)}`;
   }).join(' ')+' Z';
   paths.forEach(path=>path.setAttribute('d',d));
   light.setAttribute('cx',cx);light.setAttribute('cy',cy);
   const hoverRadius=Math.min(85,rect.height*.4,rect.width*.22);
   if(burstStart!==null){
    light.removeAttribute('gradientTransform');
    const progress=Math.min(1,(now-burstStart)/(releasing?950:720));
    const spread=releasing?1:1-(1-progress)**3;
    light.setAttribute('r',hoverRadius+(Math.hypot(rect.width,rect.height)*1.3-hoverRadius)*spread);
    paths[1].style.opacity=String(releasing?1-progress*progress*(3-2*progress):1-Math.max(0,(progress-.5)/.5)**2);
    if(progress===1){burstStart=null;releasing=false;}
   }else{
    light.setAttribute('r',hoverRadius);
    const {x:gx,y:gy,angle}=glowFrame||borderLightFrame(cx,cy,rect.width,rect.height);
    const stretch=280/hoverRadius;
    light.setAttribute('cx',gx);light.setAttribute('cy',gy);
    light.setAttribute('gradientTransform',`translate(${gx} ${gy}) rotate(${angle}) scale(${stretch} 1) translate(${-gx} ${-gy})`);
    paths[1].style.opacity=String(strength);
   }
   const fade=svg.querySelector('#prompt-reflection-fade');
   const magnitude=Math.min(1,Math.hypot(sideX,side));
   const norm=Math.hypot(sideX,side)||1;
   const dx=sideX/norm,dy=side/norm;
   const extent=Math.abs(dx)*rect.width/2+Math.abs(dy)*rect.height/2;
   fade.setAttribute('x1',rect.width/2);fade.setAttribute('y1',rect.height/2);
   fade.setAttribute('x2',rect.width/2+dx*extent);fade.setAttribute('y2',rect.height/2+dy*extent);
   const bright=Math.round(magnitude*255);
   fade.lastElementChild.setAttribute('stop-color',`rgb(${bright} ${bright} ${bright})`);
   paths[2].style.opacity=String(Number(paths[1].style.opacity)*.28);
   paths[3].style.opacity=String(Number(paths[1].style.opacity)*.16);
  }
  function tick(now){
   raf=0;if(disposed)return;
   const dt=Math.min(now-(last||now-16),40);last=now;
   const k=1-Math.exp(-dt/95);
   const goal=borderLightFrame(cx,cy,rect.width,rect.height);
   if(!glowFrame||strength<.005)glowFrame={...goal};
   const turn=((goal.angle-glowFrame.angle+540)%360)-180;
   const follow=1-Math.exp(-dt/140);
   glowFrame.x+=(goal.x-glowFrame.x)*follow;
   glowFrame.y+=(goal.y-glowFrame.y)*follow;
   glowFrame.angle=(glowFrame.angle+turn*follow+360)%360;
   glowSettling=Math.hypot(goal.x-glowFrame.x,goal.y-glowFrame.y)>.1||Math.abs(turn)>.1;

   const targetSide=rect?Math.max(-1,Math.min(1,(cy/rect.height-.5)*4)):0;
   const targetX=rect?Math.max(-1,Math.min(1,(cx/rect.width-.5)*4)):0;
   side+=(targetSide-side)*k;sideX+=(targetX-sideX)*k;
   x+=(tx-x)*k;y+=(ty-y)*k;strength+=(target-strength)*k;
   paint(now);
   if(glowSettling||burstStart!==null||Math.abs(targetX-sideX)+Math.abs(targetSide-side)+Math.abs(tx-x)+Math.abs(ty-y)+Math.abs(target-strength)>.003)raf=requestAnimationFrame(tick);else last=0;
  }
  function start(){if(!raf)raf=requestAnimationFrame(tick);}
  function reset(){tx=ty=target=0;start();}
  function measure(){
   const box=form.getBoundingClientRect();rect={left:box.left-x,top:box.top-y,width:box.width,height:box.height};
   const button=form.querySelector('.prompt-submit')?.getBoundingClientRect();
   buttonBox=button?{x:button.left-box.left,y:button.top-box.top,width:button.width,height:button.height}:null;
   const w=box.width,h=box.height,r=12;points=[];
   // Clockwise rounded contour; outward normals deform only the nearby edge.
   const corners=[[w-r,r,-90],[w-r,h-r,0],[r,h-r,90],[r,r,180]];
   corners.forEach(([ox,oy,angle],index)=>{
    for(let a=0;a<=90;a+=9){const t=(angle+a)*Math.PI/180;points.push([ox+r*Math.cos(t),oy+r*Math.sin(t),Math.cos(t),Math.sin(t)]);}
    const next=corners[(index+1)%4],t=(angle+90)*Math.PI/180;
    const ax=ox+r*Math.cos(t),ay=oy+r*Math.sin(t),bx=next[0]+r*Math.cos(t),by=next[1]+r*Math.sin(t);
    const steps=Math.ceil(Math.hypot(bx-ax,by-ay)/10);
    for(let i=1;i<steps;i++)points.push([ax+(bx-ax)*i/steps,ay+(by-ay)*i/steps,Math.cos(t),Math.sin(t)]);
   });
   svg.querySelector('#prompt-reflection-fade').setAttribute('y1',0);
   svg.querySelector('#prompt-reflection-fade').setAttribute('y2',h);
   svg.querySelector('#prompt-reflection-mask').setAttribute('width',w+256);
   svg.querySelector('#prompt-reflection-mask').setAttribute('height',h+256);
   svg.querySelector('#prompt-reflection-mask rect').setAttribute('width',w+256);
   svg.querySelector('#prompt-reflection-mask rect').setAttribute('height',h+256);
   svg.querySelector('clipPath path').setAttribute('d',`M-128 -128H${w+128}V${h+128}H-128Z M12 0H${w-12}Q${w} 0 ${w} 12V${h-12}Q${w} ${h} ${w-12} ${h}H12Q0 ${h} 0 ${h-12}V12Q0 0 12 0Z`);
   svg.setAttribute('viewBox',`-128 -128 ${w+256} ${h+256}`);paint();
  }
  function move(e){
   if(releasing||form.contains(document.activeElement)||e.pointerType==='touch'||reduced.matches||!fine.matches||document.hidden)return;
   if(!rect)return;
   cx=e.clientX-rect.left;cy=e.clientY-rect.top;
   const outside=Math.hypot(Math.max(0,-cx,cx-rect.width),Math.max(0,-cy,cy-rect.height));
   target=Math.max(0,1-outside/90);
   tx=0;
   ty=0;
   start();
  }
  const observer=new ResizeObserver(measure);observer.observe(form);measure();
  document.addEventListener('pointermove',move,{passive:true});document.addEventListener('pointerleave',reset);
  window.addEventListener('scroll',measure,{passive:true});window.addEventListener('blur',reset);
  function stop(){releasing=false;glowFrame=null;glowSettling=false;burstStart=null;cancelAnimationFrame(raf);raf=0;last=0;x=y=tx=ty=strength=target=0;paint();}
  function activate(){
   if(reduced.matches||document.hidden){stop();return;}
   releasing=false;tx=ty=target=0;burstStart=performance.now();start();
  }
  function press(e){
   if(e.target.tagName!=='TEXTAREA')return;
   if(rect){cx=e.clientX-rect.left;cy=e.clientY-rect.top;}
   if(!form.contains(document.activeElement))return;
  }
  function focus(e){if(!form.contains(e.relatedTarget))activate();}
  function blur(e){if(!form.contains(e.relatedTarget))stop();}
  form.addEventListener('pointerdown',press);form.addEventListener('focusin',focus);form.addEventListener('focusout',blur);
  document.addEventListener('visibilitychange',stop);reduced.addEventListener('change',stop);
  return()=>{disposed=true;cancelAnimationFrame(raf);observer.disconnect();form.removeEventListener('pointerdown',press);form.removeEventListener('focusin',focus);form.removeEventListener('focusout',blur);form.style.removeProperty('translate');['--prompt-glare-x','--prompt-glare-y','--prompt-glare-opacity','--submit-reflection','--submit-reflection-x','--submit-reflection-y'].forEach(key=>form.style.removeProperty(key));document.removeEventListener('pointermove',move);document.removeEventListener('pointerleave',reset);window.removeEventListener('scroll',measure);window.removeEventListener('blur',reset);document.removeEventListener('visibilitychange',stop);reduced.removeEventListener('change',stop);};
 },[]);
 return <svg ref={root} className="elastic-prompt-border" aria-hidden="true"><defs><linearGradient id="prompt-background-light" x1="50%" y1="0%" x2="50%" y2="100%"><stop stopColor="var(--prompt-light-color, #ffffff)" stopOpacity=".6"/><stop offset="1" stopColor="var(--prompt-light-color, #ffffff)" stopOpacity=".15"/></linearGradient><radialGradient id="prompt-edge-light" gradientUnits="userSpaceOnUse" r="85"><stop stopColor="#ffffff"/><stop offset=".14" stopColor="var(--prompt-light-core, #ffffff)"/><stop offset=".30" stopColor="var(--prompt-light-fringe-cool, #edfaff)" stopOpacity=".85"/><stop offset=".62" stopColor="var(--prompt-light-fringe-soft, #f0edff)" stopOpacity=".45"/><stop offset=".84" stopColor="var(--prompt-light-color, #ffffff)" stopOpacity=".15"/><stop offset="1" stopColor="var(--prompt-light-color, #ffffff)" stopOpacity="0"/></radialGradient><radialGradient id="prompt-edge-spill" href="#prompt-edge-light"><stop stopColor="var(--prompt-spill-cool, #8cdff5)" stopOpacity=".85"/><stop offset=".48" stopColor="var(--prompt-spill-cool, #8cdff5)" stopOpacity=".7"/><stop offset=".76" stopColor="var(--prompt-spill-rose, #e8a9d5)" stopOpacity=".6"/><stop offset="1" stopColor="var(--prompt-spill-rose, #e8a9d5)" stopOpacity="0"/></radialGradient><clipPath id="prompt-foil-exterior" clipPathUnits="userSpaceOnUse"><path clipRule="evenodd"/></clipPath><linearGradient id="prompt-reflection-fade" gradientUnits="userSpaceOnUse" x1="0" x2="0"><stop stopColor="black"/><stop offset=".35" stopColor="black"/><stop offset="1" stopColor="black"/></linearGradient><mask id="prompt-reflection-mask" maskUnits="userSpaceOnUse" x="-128" y="-128" width="100%" height="100%"><rect x="-128" y="-128" fill="url(#prompt-reflection-fade)"/></mask></defs><path className="elastic-edge-base"/><path className="elastic-edge-light" stroke="url(#prompt-edge-light)"/><path className="elastic-edge-reflection" mask="url(#prompt-reflection-mask)" stroke="url(#prompt-edge-spill)" clipPath="url(#prompt-foil-exterior)"/><path className="elastic-edge-reflection elastic-edge-ambient" mask="url(#prompt-reflection-mask)" stroke="url(#prompt-edge-spill)" clipPath="url(#prompt-foil-exterior)"/><path className="elastic-edge-focus"/></svg>;
});
