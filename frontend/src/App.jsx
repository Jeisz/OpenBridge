import {useWorkspaceView} from './useWorkspaceView';
import {reloadHome} from './reloadHome.mjs';
import {SectionNavigation} from './SectionNavigation';
import {Assistant} from './features/assistant/Assistant';
import {useAssistantFlow} from './features/assistant/useAssistantFlow';
import {Catalog} from './features/catalog/Catalog';
import {ToolModal} from './ToolModal';
import {useToolNavigation} from './useToolNavigation';
import {useCatalogBounce} from './useCatalogBounce';
import {useHeroParallax} from './useHeroParallax';
import {ElasticScrollbar} from './ElasticScrollbar';
import React, {useRef, useCallback} from 'react';
export function App(){
 const navigation=useToolNavigation();
 const openRef=useRef(navigation.open);openRef.current=navigation.open;
 const openTool=useCallback((...args)=>openRef.current(...args),[]);
 const isDetail=navigation.id!==null;
 useHeroParallax(false);
 useCatalogBounce(false);
 const flow=useAssistantFlow(isDetail);
 const {expanded,phase}=flow;
 const workspace=useWorkspaceView(flow.pending);

 return <><a href="#asistente" className="skip" inert={isDetail?true:undefined}>Ir al contenido</a><header inert={isDetail?true:undefined} aria-hidden={isDetail}><div className="nav wrap"><a className="brand" href="/" onClick={reloadHome}><img className="openbridge-logo" src="/assets/brands/openbridge.svg" alt="OpenBridge"/></a><SectionNavigation paused={isDetail} workspace={workspace}/></div></header>
 <main inert={isDetail?true:undefined} aria-hidden={isDetail} id="landing-view" data-has-proposal={expanded}><div hidden={workspace.active&&workspace.view!=='assistant'}><Assistant flow={{...flow,newArchitecture:()=>{flow.newArchitecture();workspace.reset();}}} workspace={workspace.active}/></div>
 <div hidden={workspace.active&&workspace.view!=='catalog'} className={workspace.active?'catalog-workspace':undefined}><Catalog onOpen={openTool} phase={phase}/></div></main>{isDetail&&<ToolModal id={navigation.id} onClose={navigation.back}/>}<ElasticScrollbar/></>;
}
