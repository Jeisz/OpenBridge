import {AssistantError} from '../data/assistant.mjs';
// Explicit local QA scenarios; never modify the published catalog to simulate bad data.
export function assistantScenarioOptions(scenario,catalog){
 const options={scenario,delay:10000,slowMs:60000};
 const previewCodes=['invalid_query','invalid_response','provider_unavailable','connection_error','unavailable_tool','unverified_license','technical_error'];
 if(scenario.startsWith('error_')&&previewCodes.includes(scenario.slice(6)))return {provider:{async ask(){throw new AssistantError(scenario.slice(6),'');}}};
 if(scenario==='slow')options.delay=15000;
 if(scenario==='timeout')Object.assign(options,{delay:30000,slowMs:60000,timeoutMs:6000});
 if(scenario==='archived_tool')options.catalog=catalog.map(tool=>tool.full_name==='keycloak/keycloak'?{...tool,archived:true}:tool);
 if(scenario==='provider_unavailable')options.provider={async ask(){throw new AssistantError('provider_unavailable','El asistente no está disponible ahora. Tu descripción se conserva; puedes reintentar.');}};
 if(scenario==='unverified_license')options.catalog=catalog.map(tool=>tool.full_name==='keycloak/keycloak'?{...tool,license_spdx_id:'NOASSERTION'}:tool);
 return options;
}
