import {ArrowUpRight} from 'lucide-react';
import {errorActions} from './errorPresentation.mjs';
export function PromptError({canRetry,onRetry}){
 return <div className="composer-feedback">{canRetry&&<button type="button" className="composer-retry" onClick={onRetry}>{errorActions.retry} <ArrowUpRight size={12} aria-hidden="true"/></button>}</div>;
}
