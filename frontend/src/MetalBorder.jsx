import {memo,useEffect,useRef} from 'react';
import {metalEase,metalGeometry,metalIntensity,metalEntryEnergy,metalShaderTime} from './metalGeometry.mjs';

import {ShaderMount,liquidMetalFragmentShader,getShaderColorFromString} from '@paper-design/shaders';
import {liquidMetalMaterial} from './liquidMetalMaterial';

export const MetalBorder=memo(function MetalBorder(){
 const root=useRef(null),canvas=useRef(null),source=useRef(null),reflection=useRef(null);
 useEffect(()=>{
  const host=root.current,form=host.parentElement,materialHost=source.current,output=canvas.current;
  const ctx=output.getContext('2d'),mask=document.createElement('canvas'),mc=mask.getContext('2d'),reveal=document.createElement('canvas'),rc=reveal.getContext('2d'),glow=document.createElement('canvas'),gc=glow.getContext('2d');
  const reflected=reflection.current,light=reflected.getContext('2d');
  const red=document.createElement('canvas'),redCtx=red.getContext('2d');red.width=red.height=256;
  if(!ctx||!mc||!rc||!gc||!light||!redCtx)return;
  const testMode=['localhost','127.0.0.1'].includes(location.hostname)?new URLSearchParams(location.search).get('borderPerf'):null;
  const noReflection=testMode==='no-reflection'||testMode==='no-shader';
  const noShader=testMode==='no-shader';
  host.dataset.perfMode=testMode||'full';
  if(noReflection)reflected.style.display='none';
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  let focused=false,visible=true,failed=false,active=false,running=false,hasError=false,errorMix=0;
  let raf=0,last=0,elapsed=0,progress=0,entry=0,w=1,h=1,dpr=1,geometry,paths=[],maskProgress=-1,disposed=false;
  const pad=64;
  let shader;
  try{
   if(!noShader){
   const uniforms={u_isImage:false,u_shape:1,u_fit:1,u_scale:1.2,u_rotation:52,u_offsetX:0,u_offsetY:-.04,u_originX:.5,u_originY:.5,u_worldWidth:0,u_worldHeight:0};
   for(const key of ['repetition','softness','shiftRed','shiftBlue','distortion','contour','angle'])uniforms['u_'+key]=liquidMetalMaterial[key];
   // Original liquid-metal palette, with the shared soft chromatic reflections.
   uniforms.u_colorBack=getShaderColorFromString(liquidMetalMaterial.colorBack);
   uniforms.u_colorTint=getShaderColorFromString(liquidMetalMaterial.colorTint);
   shader=new ShaderMount(materialHost,liquidMetalFragmentShader,uniforms,{preserveDrawingBuffer:true,alpha:true},0,12000,1,220000);
   }
  }catch{failed=true;}

  function buildMask(){
   if(progress===maskProgress)return;
   maskProgress=progress;
   rc.clearRect(0,0,mask.width,mask.height);rc.save();rc.scale(dpr,dpr);rc.translate(pad,pad);
   rc.lineWidth=2;rc.strokeStyle='#fff';rc.lineCap='butt';
   // Average overlapping prefixes to feather the last 24 CSS pixels.
   // Additive coverage keeps the two routes seamless at their shared endpoints.
   rc.globalCompositeOperation='lighter';rc.globalAlpha=1/12;
   for(let i=0;i<12;i++){
    const length=Math.max(0,Math.min(geometry.length,progress*(geometry.length+24)-(i+.5)*2));
    if(!length)continue;
    rc.setLineDash([geometry.length,geometry.length]);rc.lineDashOffset=geometry.length-length;
    paths.forEach(path=>rc.stroke(path));
   }
   rc.restore();
   mc.clearRect(0,0,mask.width,mask.height);mc.drawImage(reveal,0,0);
   // Expand the light source before blurring; a 2px source alone vanishes
   // against the hero. Remove the whole interior, not just the thin stroke.
   gc.clearRect(0,0,glow.width,glow.height);gc.save();
   gc.shadowColor='rgba(255,255,255,.7)';gc.shadowBlur=10*dpr;gc.globalAlpha=.65;
   for(const [dx,dy] of [[-2,0],[2,0],[0,-2],[0,2]])gc.drawImage(reveal,dx*dpr,dy*dpr);
   gc.shadowBlur=0;gc.globalAlpha=1;gc.globalCompositeOperation='destination-out';
   gc.scale(dpr,dpr);gc.beginPath();gc.roundRect(pad,pad,w,h,12);gc.fill();gc.restore();

  }
  function draw(){
   if(!geometry||disposed)return;
   ctx.clearRect(0,0,output.width,output.height);
   buildMask();
   const energy=(failed||motion.matches)?0:metalEntryEnergy(elapsed);
   const intensity=metalIntensity(elapsed)*.65*(1+.2*energy);
   ctx.globalCompositeOperation='source-over';
   if(!failed&&!motion.matches){ctx.globalAlpha=Math.min(1,intensity*(.88+.12*(1-Math.min(elapsed/4000,1))**3+.18*energy));ctx.drawImage(glow,0,0);}
   ctx.globalAlpha=(failed||motion.matches)?.45:intensity;ctx.drawImage(mask,0,0);ctx.globalAlpha=1;
   ctx.globalCompositeOperation='source-in';
   if(shader&&!failed&&!motion.matches&&shader.canvasElement.width>0&&shader.canvasElement.height>0){
    ctx.filter='blur(.65px)';
    const material=shader.canvasElement;
    // Sample the interior material so its own rectangular silhouette never becomes a second rim.
    ctx.drawImage(material,material.width*.25,material.height*.25,material.width*.5,material.height*.5,0,0,output.width,output.height);
    ctx.filter='none';
    if(errorMix>0){
     // Preserve shader luminance while fixing hue to red (no amber/chromatic fringe).
     redCtx.clearRect(0,0,256,256);redCtx.filter='grayscale(1) brightness(1.5)';
     redCtx.drawImage(material,0,0,256,256);redCtx.filter='none';
     redCtx.globalCompositeOperation='multiply';redCtx.fillStyle='#ff5149';redCtx.fillRect(0,0,256,256);
     redCtx.globalCompositeOperation='destination-in';redCtx.drawImage(material,0,0,256,256);redCtx.globalCompositeOperation='source-over';
     ctx.globalCompositeOperation='source-atop';ctx.globalAlpha=errorMix;ctx.filter='blur(.65px)';
     ctx.drawImage(red,64,64,128,128,0,0,output.width,output.height);
     ctx.globalAlpha=1;ctx.filter='none';
    }
   }else{ctx.fillStyle=hasError?'#ff625a':'#78caff';ctx.fillRect(0,0,output.width,output.height);}
   ctx.globalCompositeOperation='source-over';
   // Reuse the exact colored border frame, so nearby texture catches its passing reflections.
   if(!noReflection)light.clearRect(0,0,reflected.width,reflected.height);
   if(!noReflection&&!motion.matches&&!failed){
    light.globalCompositeOperation='lighter';
    for(const [dx,dy] of [[0,0],[-5,0],[5,0],[0,-5],[0,5]])light.drawImage(output,dx*dpr,dy*dpr);
    light.globalCompositeOperation='source-over';
   }

  }
  function stop(){cancelAnimationFrame(raf);raf=0;last=0;}
  function tick(now){
   if(!running||disposed)return;
   const delta=last?now-last:0;elapsed+=delta;last=now;
   errorMix+=(Number(hasError)-errorMix)*(1-Math.exp(-delta/100));
   if(Math.abs(Number(hasError)-errorMix)<.001)errorMix=Number(hasError);
   // One animation clock draws the shader before copying it through the cached border mask.
   shader?.setFrame(12000+metalShaderTime(elapsed));
   progress=metalEase(Math.min(elapsed/1800,1));host.dataset.progress=progress.toFixed(4);
   host.dataset.phase=elapsed<1800?'entering':elapsed<4000?'settling':'reflecting';draw();
   raf=requestAnimationFrame(tick);
  }
  function sync(){
   stop();hasError=form.dataset.error==='true'||form.classList.contains('invalid');
   const nextActive=focused||hasError;
   if(nextActive&&!active){elapsed=0;progress=0;maskProgress=-1;errorMix=Number(hasError);host.dataset.entry=String(++entry);}
   active=nextActive;host.dataset.active=String(active);host.dataset.tone=hasError?'error':'default';
   running=active&&visible&&!document.hidden&&!motion.matches&&!failed;host.dataset.running=String(running);
   if((motion.matches||failed)&&active){errorMix=Number(hasError);progress=1;host.dataset.phase='static';draw();}
   else if(running)tick(performance.now());
  }
  function enter(){focused=true;sync();}
  function leave(e){if(!form.contains(e.relatedTarget)){focused=false;sync();}}
  const resize=new ResizeObserver(()=>{
   const rect=form.getBoundingClientRect();
   if(rect.width<=0||rect.height<=0)return;
   w=rect.width;h=rect.height;dpr=Math.min(devicePixelRatio||1,1.5);
   reflected.width=output.width=mask.width=reveal.width=glow.width=Math.ceil((w+pad*2)*dpr);reflected.height=output.height=mask.height=reveal.height=glow.height=Math.ceil((h+pad*2)*dpr);
   output.style.left=output.style.top=-pad+'px';output.style.width=(w+pad*2)+'px';output.style.height=(h+pad*2)+'px';
   reflected.style.left=reflected.style.top=-pad+'px';reflected.style.width=(w+pad*2)+'px';reflected.style.height=(h+pad*2)+'px';
   const x=pad,y=pad,r=12;
   reflected.style.clipPath=`path(evenodd, "M0 0 H${w+2*pad} V${h+2*pad} H0 Z M${x+r} ${y} H${x+w-r} Q${x+w} ${y} ${x+w} ${y+r} V${y+h-r} Q${x+w} ${y+h} ${x+w-r} ${y+h} H${x+r} Q${x} ${y+h} ${x} ${y+h-r} V${y+r} Q${x} ${y} ${x+r} ${y} Z")`;
   geometry=metalGeometry(w,h);paths=[new Path2D(geometry.upper),new Path2D(geometry.lower)];maskProgress=-1;draw();
  });
  const intersection=new IntersectionObserver(([e])=>{visible=e.isIntersecting;sync();});
  const invalid=new MutationObserver(sync);
  resize.observe(form);intersection.observe(form);invalid.observe(form,{attributes:true,attributeFilter:['class','data-error']});
  form.addEventListener('focusin',enter);form.addEventListener('focusout',leave);
  document.addEventListener('visibilitychange',sync);motion.addEventListener('change',sync);
  if(form.contains(document.activeElement))enter();else sync();
  return()=>{disposed=true;running=false;stop();resize.disconnect();intersection.disconnect();invalid.disconnect();form.removeEventListener('focusin',enter);form.removeEventListener('focusout',leave);document.removeEventListener('visibilitychange',sync);motion.removeEventListener('change',sync);shader?.dispose();};
 },[]);
 return <div ref={root} className="metal-border" aria-hidden="true"><canvas ref={reflection} className="metal-border-reflection"/><canvas ref={canvas} className="metal-border-core"/><div ref={source} className="metal-border-source"/></div>;
});
