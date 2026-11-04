import {errorPreview} from './mocks/errorPreview.mjs';
import {interfaceErrors} from './errorPresentation.mjs';
import {useEffect,useRef,useState} from 'react';
import {Check,Copy} from 'lucide-react';
import {Highlight,themes} from 'prism-react-renderer';
import {snippetLanguage} from './data/snippetLanguage.mjs';
const theme={...themes.vsDark,plain:{...themes.vsDark.plain,backgroundColor:'transparent'}};
export function Snippet({text,language}){
 const [status,setStatus]=useState('');
 const timer=useRef(null);
 const syntax=snippetLanguage(language);
 useEffect(()=>()=>clearTimeout(timer.current),[]);
 async function copy(){
  clearTimeout(timer.current);
  try{if(errorPreview('copy'))throw new Error('Local copy preview');await navigator.clipboard.writeText(text);setStatus('Copiado');timer.current=setTimeout(()=>setStatus(''),2200);}
  catch{setStatus(interfaceErrors.copy);}
 }
 return <div className="snippet">
  <div className="snippet-toolbar"><span className="snippet-language">{syntax.label}</span><button className="ui-wash" type="button" onClick={copy} aria-label="Copiar snippet">{status==='Copiado'?<Check size={15}/>:<Copy size={15}/>} {status==='Copiado'?'Copiado':'Copiar'}</button></div>
  <Highlight theme={theme} code={text} language={syntax.language}>{({className,style,tokens,getLineProps,getTokenProps})=><pre tabIndex={0} aria-label={`Código: ${syntax.label}`} className={className} style={style}><code data-language={syntax.language}>{tokens.map((line,index)=><span key={index} {...getLineProps({line})} className="snippet-line"><span className="snippet-line-number" aria-hidden="true">{index+1}</span><span className="snippet-line-code">{line.map((token,key)=><span key={key} {...getTokenProps({token})}/>)}</span></span>)}</code></pre>}</Highlight>
  <span className={status===interfaceErrors.copy?"snippet-copy-error":"sr-only"} role="status" aria-live="polite">{status}</span>
 </div>;
}
