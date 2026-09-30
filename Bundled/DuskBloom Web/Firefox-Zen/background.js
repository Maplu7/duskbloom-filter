// DuskBloom Web v54 background helper.
// IMPORTANT: v54 content.js + popup.js own site state under mf44:<hostname>.
// Keep the background script on the same protocol so it cannot overwrite v54 settings.
const DEFAULTS = { enabled:true, preset:"obsidian" };
const key = host => `mf44:${host}`;
const hostFromUrl = url => { try { return new URL(url).hostname; } catch (_) { return ""; } };

async function getSite(host) {
  const data = await browser.storage.local.get(key(host));
  return {...DEFAULTS, ...(data[key(host)] || {})};
}
async function setSite(host, patch) {
  const next = {...await getSite(host), ...patch};
  await browser.storage.local.set({[key(host)]: next});
  return next;
}
async function tell(tabId, settings) {
  try { await browser.tabs.sendMessage(tabId, {type:"MF44_SET", settings}); } catch (_) {}
}

browser.runtime.onInstalled.addListener(() => {
  browser.contextMenus.removeAll().then(() => {
    browser.contextMenus.create({id:"mf-toggle", title:"DuskBloom Web: Toggle on this site", contexts:["page"]});
    browser.contextMenus.create({id:"mf-reset", title:"DuskBloom Web: Reset this site", contexts:["page"]});
  });
});

browser.contextMenus.onClicked.addListener(async (info, tab) => {
  const host=hostFromUrl(tab.url); if(!host) return;
  if(info.menuItemId==="mf-reset"){
    await browser.storage.local.remove(key(host));
    return tell(tab.id, DEFAULTS);
  }
  if(info.menuItemId==="mf-toggle"){
    const s=await getSite(host);
    const next=await setSite(host,{enabled:!s.enabled});
    tell(tab.id,next);
  }
});

browser.commands.onCommand.addListener(async command => {
  if(command!=="toggle-migraine-filter") return;
  const [tab]=await browser.tabs.query({active:true,currentWindow:true}); if(!tab) return;
  const host=hostFromUrl(tab.url); if(!host) return;
  const s=await getSite(host);
  const next=await setSite(host,{enabled:!s.enabled});
  tell(tab.id,next);
});
