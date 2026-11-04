import fixtures from '../mocks/proposal-layout.fixtures.json' with {type:'json'};

// Curated demo content, separate from the unconfirmed assistant HTTP contract.
// Never attach example instructions to an unknown or changed response.
export function resolveProposalExample(response){
 const example=fixtures[response?.id];
 if(response?.status!=='ok'||!example||!Array.isArray(response.components)||!Array.isArray(example.layers)||example.layers.length!==response.components.length)return null;
 const matches=example.layers.every(layer=>response.components.some(c=>c.key===layer.key&&c.full_name===layer.full_name));
 if(!matches)return null;
 const result=structuredClone(example);
 return result;
}

// Relationships come from the response, independently of curated demo layout.
export function resolveProposalConnections(response){
 if(response?.status!=='ok')return [];
 const labels=new Map(response.components.map(c=>[c.key,c.label]));
 return (response.connections??[]).map(connection=>({
  ...connection,title:`${labels.get(connection.from_key)} → ${labels.get(connection.to_key)} · ${connection.protocol}`
 }));
}
