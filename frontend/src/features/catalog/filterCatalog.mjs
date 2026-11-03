import {toolCategoryNames} from '../../data/catalog.mjs';
const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export function filterCatalog(tools,{search='',category='Todas',language='',license='',maintenance='',stars='' }={}){
 return tools.filter(t=>(category==='Todas'||toolCategoryNames(t).includes(category))&&normalize(t.name+' '+t.description).includes(normalize(search))&&(!language||t.language===language)&&(!license||t.license===license)&&(!maintenance||(maintenance==='active'?['github_snapshot','api'].includes(t.dataSource)&&!t.archived&&!t.disabled:maintenance==='archived'?t.archived===true:maintenance==='disabled'?t.disabled===true:false))&&t.stars>=Number(stars));
}
