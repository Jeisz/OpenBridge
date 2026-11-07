export const CATALOG_PAGE_SIZE=24;
export function paginateCatalog(items,requestedPage,pageSize=CATALOG_PAGE_SIZE){
 const pages=Math.max(1,Math.ceil(items.length/pageSize));
 const page=Math.min(pages,Math.max(1,requestedPage));
 return {page,pages,items:items.slice((page-1)*pageSize,page*pageSize)};
}
export function pageNumbers(page,pages){
 const visible=new Set([1,pages,page-1,page,page+1]);
 if(page<=3)[2,3,4].forEach(n=>visible.add(n));
 if(page>=pages-2)[pages-3,pages-2,pages-1].forEach(n=>visible.add(n));
 const result=[];
 [...visible].filter(n=>n>0&&n<=pages).sort((a,b)=>a-b).forEach(n=>{
  const last=result.at(-1);
  if(last&&n-last>1)result.push('gap-'+n);
  result.push(n);
 });
 return result;
}
