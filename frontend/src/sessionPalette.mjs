// Decorative fallback palettes, not official brand identities.
export const fallbackPalettes=Object.freeze([
 {id:'blue',start:'#0f1839',end:'#002ec5',tag:'#2749ba'},
 {id:'petrol',start:'#10252e',end:'#075477',tag:'#14617b'},
 {id:'indigo',start:'#171c42',end:'#3847a3',tag:'#4654b1'},
 {id:'forest',start:'#152a21',end:'#245d40',tag:'#2b684b'},
 {id:'magenta',start:'#30152e',end:'#802563',tag:'#8b306e'},
 {id:'amber',start:'#302011',end:'#815020',tag:'#875323'},
 {id:'violet',start:'#25183e',end:'#55358a',tag:'#654396'},
 {id:'plum',start:'#311d32',end:'#65406a',tag:'#754b79'},
 {id:'teal',start:'#102e30',end:'#185e62',tag:'#246d70'},
 {id:'slate',start:'#1d2737',end:'#3c526d',tag:'#48617e'},
]);
const storageKey='openbridge:session-palettes:v1';
export function createSessionPaletteResolver({storage=()=>null,random=Math.random}={}){
 const assignments=new Map();
 return key=>{
  if(!key)return null;
  if(assignments.has(key))return assignments.get(key);
  let palette;
  try{const saved=JSON.parse(storage()?.getItem(storageKey)||'{}');palette=fallbackPalettes.find(p=>p.id===saved[key]);}catch{}
  palette??=fallbackPalettes[Math.min(fallbackPalettes.length-1,Math.max(0,Math.floor(random()*fallbackPalettes.length)))];
  assignments.set(key,palette);
  try{
   const saved=JSON.parse(storage()?.getItem(storageKey)||'{}');
   storage()?.setItem(storageKey,JSON.stringify({...saved,[key]:palette.id}));
  }catch{/* In-memory assignments also work when storage is unavailable. */}
  return palette;
 };
}
export const sessionPalette=createSessionPaletteResolver({storage:()=>window.sessionStorage});
