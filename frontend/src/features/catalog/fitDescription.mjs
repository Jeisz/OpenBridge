// fits receives the text plus whether the inline continuation must fit with it.
export function fitDescription(text,fits){
 if(fits(text,false))return {text,clipped:false};
 const chars=Array.from(text);let low=0,high=chars.length;
 while(low<high){const mid=Math.ceil((low+high)/2);if(fits(chars.slice(0,mid).join('').trimEnd(),true))low=mid;else high=mid-1;}
 let prefix=chars.slice(0,low).join('').trimEnd();
 if(low<chars.length&&chars[low]&&!/\s/u.test(chars[low])){const boundary=prefix.lastIndexOf(' ');if(boundary>0)prefix=prefix.slice(0,boundary);}
 return {text:prefix,clipped:true};
}
