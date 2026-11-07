import {Prism} from 'prism-react-renderer';
const aliases={js:'javascript',ts:'typescript',py:'python',yml:'yaml',html:'markup',xml:'markup'};
const labels={text:'Texto',javascript:'JavaScript',typescript:'TypeScript',jsx:'JSX',tsx:'TSX',python:'Python',json:'JSON',sql:'SQL',yaml:'YAML',markup:'HTML / XML',css:'CSS',go:'Go',rust:'Rust',bash:'Bash',shell:'Shell',dockerfile:'Dockerfile'};
export function snippetLanguage(value){
 const raw=typeof value==='string'?value.trim().toLowerCase():'';
 const name=aliases[raw]??raw;
 const supported=Object.hasOwn(Prism.languages,name)&&typeof Prism.languages[name]==='object';
 return {language:supported?name:'text',label:labels[name]??(raw||'Texto'),supported};
}
