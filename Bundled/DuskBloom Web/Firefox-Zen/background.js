const DEFAULTS={enabled:true,preset:"obsidian"};
const hostFromUrl=url=>{try{return new URL(url).hostname}catch(_){return""}};
const key=host=>`mf44:${host}`;
async function getSite(host){const d=await browser.storage.local.get(key(host));return {...DEFAULTS,...(d[key(host)]||{})}}
async function setSite(host,patch){const n={...await getSite(host),...patch};await browser.storage.local.set({[key(host)]:n});return n}
async function tell(id,s){try{await browser.tabs.sendMessage(id,{type:"MF44_SET",settings:s})}catch(_){}}
browser.runtime.onInstalled.addListener(()=>browser.contextMenus.removeAll().then(()=>{browser.contextMenus.create({id:"mf-toggle",title:"DuskBloom Web: Toggle on this site",contexts:["page"]});browser.contextMenus.create({id:"mf-reset",title:"DuskBloom Web: Reset this site",contexts:["page"]})}));
browser.contextMenus.onClicked.addListener(async(info,tab)=>{const h=hostFromUrl(tab.url);if(!h)return;if(info.menuItemId==="mf-reset"){await browser.storage.local.remove(key(h));return tell(tab.id,DEFAULTS)}if(info.menuItemId==="mf-toggle"){const s=await getSite(h);tell(tab.id,await setSite(h,{enabled:!s.enabled}))}});
browser.commands.onCommand.addListener(async cmd=>{if(cmd!=="toggle-migraine-filter")return;const [tab]=await browser.tabs.query({active:true,currentWindow:true});if(!tab)return;const h=hostFromUrl(tab.url);if(!h)return;const s=await getSite(h);tell(tab.id,await setSite(h,{enabled:!s.enabled}))});
