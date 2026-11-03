import test from 'node:test';
import assert from 'node:assert/strict';
import {borderLightFrame} from '../src/promptBorderGeometry.mjs';
for(const [width,height] of [[756,180],[340,180],[756,80]]){
 for(const [flipX,flipY] of [[false,false],[true,false],[true,true],[false,true]]){
  test(`glow crosses corner continuously ${width}x${height} ${flipX}/${flipY}`,()=>{
   for(const depth of [5,15,30]){
    let previous;
    for(let delta=-15;delta<=15;delta+=.25){
     const x=depth+delta,y=depth;
     const frame=borderLightFrame(flipX?width-x:x,flipY?height-y:y,width,height);
     if(previous){
      assert.ok(Math.hypot(frame.x-previous.x,frame.y-previous.y)<3,'position must not jump');
      const turn=Math.abs(((frame.angle-previous.angle+540)%360)-180);
      assert.ok(turn<10,'orientation must not snap');
     }
     const qx=Math.max(12-frame.x,0,frame.x-(width-12));
     const qy=Math.max(12-frame.y,0,frame.y-(height-12));
     assert.ok(Math.abs(Math.hypot(qx,qy)-12)<.001,'core stays on rounded contour');
     previous=frame;
    }
   }
  });
 }
}
