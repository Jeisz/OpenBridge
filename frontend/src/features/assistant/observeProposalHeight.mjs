// The disclosure owns its 260ms expansion. The surface only animates discrete
// changes (tabs/results), never each intermediate frame of an inner transition.
export function observeProposalHeight(content, surface, Observer = ResizeObserver) {
 if (!content || !surface) return () => {};
 let previousHeight;
 const measure = () => {
  const height = `${Math.ceil(content.getBoundingClientRect().height)}px`;
  const expanding = content.getAnimations({subtree:true}).some(animation =>
   animation.transitionProperty === 'grid-template-rows' &&
   (animation.playState === 'running' || animation.pending));
  surface.style.transitionProperty = expanding ? 'none' : '';
  if (height !== previousHeight) {
   surface.style.height = height;
   previousHeight = height;
  }
 };
 const observer = new Observer(measure);
 observer.observe(content);
 content.addEventListener('transitionend', measure);
 content.addEventListener('transitioncancel', measure);
 measure();
 return () => {
  observer.disconnect();
  content.removeEventListener('transitionend', measure);
  content.removeEventListener('transitioncancel', measure);
 };
}
