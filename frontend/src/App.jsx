import {useSessionAccent} from './useSessionAccent';
import {ArrowUp} from 'lucide-react';
import {useSmoothPageScroll} from './useSmoothPageScroll';
import {useWorkspaceView} from './useWorkspaceView';
import {reloadHome} from './reloadHome.mjs';
import {SectionNavigation} from './SectionNavigation';
import {Assistant} from './features/assistant/Assistant';
import {useAssistantFlow} from './features/assistant/useAssistantFlow';
import {Catalog} from './features/catalog/Catalog';
import {ToolModal} from './ToolModal';
import {useToolNavigation} from './useToolNavigation';
import {ElasticScrollbar} from './ElasticScrollbar';
import React, {useRef, useCallback} from 'react';
export function App(){
 useSessionAccent();
 const navigation=useToolNavigation();
 const openRef=useRef(navigation.open);openRef.current=navigation.open;
 const openTool=useCallback((...args)=>openRef.current(...args),[]);
 const isDetail=navigation.id!==null;
 const flow=useAssistantFlow(isDetail);
 const {expanded,phase}=flow;
 const workspace=useWorkspaceView(flow.pending,isDetail);
 useSmoothPageScroll(isDetail);

 return <><a href="#asistente" className="skip" inert={isDetail?true:undefined}>Ir al contenido</a><header inert={isDetail?true:undefined} aria-hidden={isDetail}><div className="nav wrap"><a className="brand" href="/" onClick={reloadHome}><img className="openbridge-logo" src="/assets/brands/openbridge.svg" alt="OpenBridge"/></a><SectionNavigation paused={isDetail} workspace={workspace}/></div></header>
 <main inert={isDetail?true:undefined} aria-hidden={isDetail} id="landing-view" data-has-proposal={expanded} data-surface-mode={workspace.mode}><div ref={workspace.assistantRef} className="assistant-surface" inert={workspace.covered?true:undefined}><Assistant flow={{...flow,newArchitecture:()=>{flow.newArchitecture();workspace.reset();}}} workspace={workspace.active}/></div>
 <div ref={workspace.catalogRef} hidden={workspace.mode==='locked'} className="catalog-surface"><Catalog onOpen={openTool} phase={phase}/></div>{workspace.offer&&!isDetail&&<button ref={workspace.buttonRef} type="button" className="ui-button ui-button--primary catalog-access" onClick={()=>workspace.openCatalog()}><span>Ver catálogo</span><ArrowUp size={16} aria-hidden="true"/></button>}</main>{isDetail&&<ToolModal id={navigation.id} onClose={navigation.back}/>}<ElasticScrollbar/></>;
}
