// Shared geometry/intent rules; no animation frame owns document scrolling.
export const catalogGesturePause = 300;
export function assistantStickyTop(height, viewport) {
 return Math.min(0, viewport - height);
}
export function atAssistantEnd(scroll, height, viewport) {
 return scroll >= Math.max(0, height - viewport) - 4;
}
export function freshCatalogGesture({now, last, atEnd, wasAtEnd, downward}) {
 return downward && atEnd && wasAtEnd && now - last >= catalogGesturePause;
}
// Zero velocity at both ends, with an early peak and a longer settling tail.
export const catalogScrollEase = t => 10*t*t - 20*t**3 + 15*t**4 - 4*t**5;

// Accumulate only a fresh gesture begun after the pause, never arrival inertia.
export function catalogWheelIntent(state,{now,delta,eligible,atEnd,wasAtEnd}) {
 const fresh=now-state.last>=catalogGesturePause;
 const armed=eligible&&atEnd&&wasAtEnd&&delta>0&&(fresh||state.armed);
 const distance=armed?(fresh?0:state.distance)+Math.min(delta,40):0;
 const counted=armed&&!fresh&&!!state.counted;
 const show=armed&&distance>=40&&!counted;
 return {last:now,armed,distance,counted:counted||show,show};
}

export function assistantDepthProgress(catalogTop,viewport,header,locked=false){
 if(locked)return 0;
 const start=viewport*.9;
 const progress=Math.max(0,Math.min(1,(start-catalogTop)/Math.max(1,start-header)));
 return progress*progress*(3-2*progress);
}
