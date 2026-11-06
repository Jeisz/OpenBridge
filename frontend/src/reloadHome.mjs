export function reloadHome(event){
 if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
 event.preventDefault();
 window.history.replaceState(null,'',window.location.pathname);
 window.scrollTo(0,0);
 window.location.reload();
}
