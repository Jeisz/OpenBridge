import {catalogRecords,catalogRepos} from './data/catalog.mjs';
import {integrationIdeasForTool} from './data/integrationIdeas.mjs';
// Detail prose comes only from Repo; there is no editorial profile fallback.
const repos=new Map(catalogRepos.map(repo=>[repo.full_name,repo]));
export const profiles=Object.fromEntries(catalogRecords.map(tool=>{
 const repo=repos.get(tool.full_name);
 return [tool.id,{summary:repo?.summary_es||repo?.description||null,
  homepage:repo?.homepage||null,ideas:integrationIdeasForTool(tool)}];
}));
