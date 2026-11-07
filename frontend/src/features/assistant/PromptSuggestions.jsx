import React from 'react';
import {ArrowUpRight} from 'lucide-react';

const suggestions=[
 {title:'Gestionar varias tiendas',summary:'Pedidos, inventario y acceso por sucursal.',prompt:'Quiero una plataforma web para gestionar los pedidos y el inventario de cinco tiendas. Cada sucursal debe ver sus ventas y existencias, mientras administración puede consultar todo. Necesitamos buscar productos, actualizar el stock al confirmar pedidos y procesar reportes sin bloquear la aplicación. Empezaremos con 30 empleados y unos 500 pedidos diarios. Queremos alojarla en nuestro servidor y detectar fallos del servicio.'},
 {title:'Consultar documentos internos',summary:'Respuestas con fuentes y permisos por equipo.',prompt:'Necesito un portal donde 50 empleados puedan buscar respuestas en manuales y documentos internos. Cada respuesta debe indicar de qué documento salió y respetar los permisos de cada equipo. Los documentos se actualizan semanalmente y deben procesarse sin interrumpir las consultas. Queremos mantener los datos en nuestra infraestructura y conocer los tiempos de respuesta y los errores.'},
 {title:'Unificar reportes de ventas',summary:'Importaciones automáticas y métricas del negocio.',prompt:'Quiero reunir las ventas de nuestras tiendas y nuestra web en un panel para gerencia. Necesitamos importar datos cada hora, detectar registros duplicados y comparar ingresos, productos y sucursales. Si una importación falla, debe poder reintentarse sin repetir ventas. Empezaremos con unos 100.000 registros diarios y necesitamos controlar si la información está actualizada.'}
];

export function PromptSuggestions({flow,onSelect}){
 const hidden=flow.expanded;
 const select=text=>{
  flow.setQuery(text);
  onSelect?.(text);
  flow.setError('');
  flow.setCanRetry(false);
  flow.input.current?.focus({preventScroll:true});
 };
 return <div className={'prompt-suggestions'+(hidden?' is-hidden':'')} aria-hidden={hidden} inert={hidden?true:undefined}>
  <div className="prompt-suggestions-clip">
   <section className="prompt-suggestions-list" aria-label="Ejemplos de prompts">
    <p className="prompt-suggestions-label">¿Por dónde empezar? Prueba una idea</p>
    {suggestions.map(({title,summary,prompt})=><button key={title} type="button" className="prompt-suggestion" onPointerMove={event=>{
     if(event.pointerType==='touch'||!matchMedia('(hover:hover) and (prefers-reduced-motion:no-preference)').matches)return;
     const card=event.currentTarget,bounds=card.getBoundingClientRect();
     card.style.setProperty('--example-glow-x',`${event.clientX-bounds.left}px`);
     card.style.setProperty('--example-glow-y',`${event.clientY-bounds.top}px`);
    }} onClick={()=>select(prompt)}><span className="prompt-suggestion-title">{title}</span><ArrowUpRight size={18} aria-hidden="true"/><span className="prompt-suggestion-summary">{summary}</span></button>)}
   </section>
  </div>
 </div>;
}
