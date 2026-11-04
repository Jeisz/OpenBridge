const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
// Blend nearby edge projections along the perimeter, then sample its rounded curve.
// Unlike switching nearest edges, position and tangent stay continuous at corners.
export function borderLightFrame(x,y,width,height){
 const r=Math.min(12,width/2,height/2),a=width-2*r,b=height-2*r,c=Math.PI*r/2;
 const perimeter=2*a+2*b+4*c;
 const candidates=[
  [Math.abs(y),clamp(x-r,0,a)],
  [Math.abs(width-x),a+c+clamp(y-r,0,b)],
  [Math.abs(height-y),a+b+2*c+clamp(width-r-x,0,a)],
  [Math.abs(x),2*a+b+3*c+clamp(height-r-y,0,b)],
 ];
 const nearest=candidates.reduce((best,p)=>p[0]<best[0]?p:best);
 let sum=0,weight=0;
 for(const [distance,position] of candidates){
  const w=Math.exp(-(distance-nearest[0])/18);
  const delta=((position-nearest[1]+perimeter*1.5)%perimeter)-perimeter/2;
  sum+=delta*w;weight+=w;
 }
 let s=((nearest[1]+sum/weight)%perimeter+perimeter)%perimeter;
 const segments=[
  [a,t=>({x:r+t,y:0,angle:0})],
  [c,t=>arc(width-r,r,-Math.PI/2+t/r,r)],
  [b,t=>({x:width,y:r+t,angle:90})],
  [c,t=>arc(width-r,height-r,t/r,r)],
  [a,t=>({x:width-r-t,y:height,angle:180})],
  [c,t=>arc(r,height-r,Math.PI/2+t/r,r)],
  [b,t=>({x:0,y:height-r-t,angle:270})],
  [c,t=>arc(r,r,Math.PI+t/r,r)],
 ];
 for(const [length,sample] of segments){if(s<=length)return sample(s);s-=length;}
 return {x:r,y:0,angle:360};
}
function arc(x,y,angle,r){return {x:x+r*Math.cos(angle),y:y+r*Math.sin(angle),angle:(angle+Math.PI/2)*180/Math.PI};}
