import presentation from '../mocks/catalog-presentation.json' with {type:'json'};
// Accept canonical owner/name links, while keeping existing card IDs working.
export function detailTarget(id,tools){
 const original=tools.find(tool=>tool.id===id||tool.full_name===id);
 const fullName=original?.full_name??Object.entries(presentation).find(([,value])=>value.id===id)?.[0]??(/^[^/\s]+\/[^/\s]+$/.test(id)?id:null);
 return {original,fullName};
}
