import {useState,useMemo} from 'react';
import {useCatalogData} from '../../data/CatalogProvider';
import {filterCatalog} from './filterCatalog.mjs';
export function useCatalogFilters(){
 const {tools}=useCatalogData();
 const [search,setSearch]=useState(''),[category,setCategory]=useState('Todas'),[filters,setFilters]=useState(false),[language,setLanguage]=useState(''),[license,setLicense]=useState(''),[maintenance,setMaintenance]=useState(''),[stars,setStars]=useState('');
 const filtered=useMemo(()=>filterCatalog(tools,{search,category,language,license,maintenance,stars}),[tools,search,category,language,license,maintenance,stars]);
 const active=[language,license,maintenance,stars].filter(Boolean).length;
 function clear(){setSearch('');setCategory('Todas');setLanguage('');setLicense('');setMaintenance('');setStars('');}
 return {search,setSearch,category,setCategory,filters,setFilters,language,setLanguage,license,setLicense,maintenance,setMaintenance,stars,setStars,active,clear,filtered};
}
