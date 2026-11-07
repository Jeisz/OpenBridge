import {useLayoutEffect} from 'react';
import {sessionPalette} from './sessionPalette.mjs';

// One accent per browser tab session; reloading and navigation keep the choice.
// Reuse the tool palette without changing individual tool identities.
export function useSessionAccent(){
 useLayoutEffect(()=>{
  const palette=sessionPalette('interface:primary:v1');
  document.documentElement.style.setProperty('--button-brand',palette.tag);
 },[]);
}
