// Explicit local-only visual QA. Disabled unless enabled at build time.
export function errorPreview(name){
 return process.env.NEXT_PUBLIC_ERROR_PREVIEW==='true'&&typeof window!=='undefined'&&['localhost','127.0.0.1'].includes(window.location.hostname)&&new URLSearchParams(window.location.search).get('errorPreview')===name;
}
