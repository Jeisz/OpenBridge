import test from 'node:test';
import assert from 'node:assert/strict';
import {assistantStickyTop,atAssistantEnd,freshCatalogGesture,catalogScrollEase,catalogWheelIntent,assistantDepthProgress} from '../src/catalogSurface.mjs';
test('short assistant stays at top; long assistant remains readable before pinning',()=>{
 assert.equal(assistantStickyTop(700,900),0);
 assert.equal(assistantStickyTop(1800,900),-900);
});
test('end detection tolerates subpixel scroll and short pages',()=>{
 assert.equal(atAssistantEnd(0,700,900),true);
 assert.equal(atAssistantEnd(890,1800,900),false);
 assert.equal(atAssistantEnd(899.5,1800,900),true);
});
test('arrival and inertia cannot offer the catalog; a fresh downward gesture can',()=>{
 const gesture={now:1000,last:400,atEnd:true,wasAtEnd:true,downward:true};
 assert.equal(freshCatalogGesture(gesture),true);
 assert.equal(freshCatalogGesture({...gesture,last:900}),false);
 assert.equal(freshCatalogGesture({...gesture,wasAtEnd:false}),false);
 assert.equal(freshCatalogGesture({...gesture,atEnd:false}),false);
 assert.equal(freshCatalogGesture({...gesture,downward:false}),false);
});
test('opening decelerates without overshooting the scroll destination',()=>{
 assert.equal(catalogScrollEase(0),0);assert.equal(catalogScrollEase(1),1);
 assert.ok(catalogScrollEase(.9)-catalogScrollEase(.8)<catalogScrollEase(.2)-catalogScrollEase(.1));
 for(let i=0;i<=100;i++)assert.ok(catalogScrollEase(i/100)>=0&&catalogScrollEase(i/100)<=1);
});

test('wheel intent accepts a clear new gesture but rejects inertia and tiny deltas',()=>{
 const event={eligible:true,atEnd:true,wasAtEnd:true};
 let state={last:0,armed:false,distance:0};
 state=catalogWheelIntent(state,{...event,now:100,delta:100});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:700,delta:1000});assert.equal(state.show,true);
 state=catalogWheelIntent(state,{...event,now:720,delta:40});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:730,delta:-1});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:740,delta:100});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:1300,delta:2});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:1320,delta:80,eligible:false});assert.equal(state.distance,0);
});

test('counts each completed wheel gesture once, not its inertia',()=>{
 const event={eligible:true,atEnd:true,wasAtEnd:true,delta:40};
 let state={last:0,armed:false,distance:0},count=0;
 for(const now of [600,620,640,660,1200,1220,1240,1800,1820]){
  state=catalogWheelIntent(state,{...event,now});if(state.show)count++;
  if(now<1800)assert.ok(count<3);
 }
 assert.equal(count,3);
});

test('a small trackpad gesture accumulates after a pause without requiring three attempts',()=>{
 const event={eligible:true,atEnd:true,wasAtEnd:true};
 let state={last:0,armed:false,distance:0};
 state=catalogWheelIntent(state,{...event,now:350,delta:15});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:370,delta:15});assert.equal(state.show,false);
 state=catalogWheelIntent(state,{...event,now:390,delta:12});assert.equal(state.show,true);
 state=catalogWheelIntent(state,{...event,now:410,delta:12});assert.equal(state.show,false);
});

test('assistant depth tracks coverage and reverses without keeping blur when locked',()=>{
 assert.equal(assistantDepthProgress(900,900,66),0);
 assert.equal(assistantDepthProgress(66,900,66),1);
 assert.equal(assistantDepthProgress(66,900,66,true),0);
 const mid=assistantDepthProgress(400,900,66);
 assert.ok(mid>0&&mid<1);
 assert.ok(assistantDepthProgress(500,900,66)<mid);
});
