import {useState,useEffect} from 'react';
const promptExamples = [
 'Quiero gestionar las ventas y el inventario de mis tiendas en un solo lugar.',
 'Necesito que mis clientes reserven citas y reciban recordatorios.',
 'Quiero organizar los pedidos y hacer seguimiento de las entregas de mi negocio.',
 'Necesito centralizar las consultas de mis clientes y asignarlas a mi equipo.',
 'Quiero gestionar las suscripciones de mis clientes y saber qué pagos están pendientes.'
];

export function useExamplePlaceholder(paused, input) {
 const [text, setText] = useState(promptExamples[0]);
 useEffect(() => {
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let timeout;
  let visible = false;
  let index = 0;
  let length = promptExamples[0].length;
  let deleting = true;
  function tick() {
   const current = promptExamples[index];
   length += deleting ? -1 : 1;
   setText(current.slice(0, length));
   let delay = deleting ? 10 : 30;
   if (length === 0) {
    index = (index + 1) % promptExamples.length;
    deleting = false;
    delay = 350;
   } else if (length === current.length && !deleting) {
    deleting = true;
    delay = 2600;
   }
   timeout = window.setTimeout(tick, delay);
  }
  function restart() {
   window.clearTimeout(timeout);
   index = 0;
   length = promptExamples[0].length;
   deleting = true;
   setText(promptExamples[0]);
   if (!paused && visible && !document.hidden && !motion.matches) timeout = window.setTimeout(tick, 2600);
  }
  const observer = new IntersectionObserver(([entry]) => {
   visible = entry.isIntersecting && entry.intersectionRatio > 0;
   restart();
  });
  if (input.current) observer.observe(input.current);
  restart();
  document.addEventListener('visibilitychange', restart);
  motion.addEventListener('change', restart);
  return () => {
   window.clearTimeout(timeout);
   observer.disconnect();
   document.removeEventListener('visibilitychange', restart);
   motion.removeEventListener('change', restart);
  };
 }, [paused, input]);
 return text;
}
