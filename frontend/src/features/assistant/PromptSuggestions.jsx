import React from 'react';
import {ArrowUpRight} from 'lucide-react';

const suggestions=[
 'Quiero gestionar las ventas y el inventario de mis tiendas en un solo lugar.',
 'Necesito que mis clientes reserven citas y reciban recordatorios.',
 'Quiero organizar los pedidos y hacer seguimiento de las entregas de mi negocio.'
];

export function PromptSuggestions({flow}){
 const hidden=flow.expanded||flow.isDetail;
 const select=text=>{
  flow.setQuery(text);
  flow.setError('');
  flow.setCanRetry(false);
  flow.input.current?.focus({preventScroll:true});
 };
 return <div className={'prompt-suggestions'+(hidden?' is-hidden':'')} aria-hidden={hidden} inert={hidden?true:undefined}>
  <div className="prompt-suggestions-clip">
   <section className="prompt-suggestions-list" aria-label="Ejemplos de prompts">
    {suggestions.map(text=><button key={text} type="button" className="prompt-suggestion" onClick={()=>select(text)}><span>{text}</span><ArrowUpRight size={18} aria-hidden="true"/></button>)}
   </section>
  </div>
 </div>;
}
