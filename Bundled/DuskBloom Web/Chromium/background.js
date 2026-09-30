const browser = globalThis.browser || globalThis.chrome;

const DEFAULTS = {
  enabled: true,
  preset: "obsidian",
  imageDim: 0.72,
  hoverRestoreImages: true,
  reduceMotion: true,
  reduceFlash: true,
  catcher: true,
  readability: true,
  formProtection: true,
  focusMode: false,
  rescue: false
};

function hostFromUrl(url) {
  try { return new URL(url).hostname; } catch { return ""; }
}
function key(host) { return `mf_site_${host}`; }

async function getSite(host) {
  const data = await browser.storage.local.get(key(host));
  return {...DEFAULTS, ...(data[key(host)] || {})};
}
async function setSite(host, patch) {
  const s = await getSite(host);
  const next = {...s, ...patch};
  await browser.storage.local.set({[key(host)]: next});
  return next;
}
async function tell(tabId, settings) {
  try { await browser.tabs.sendMessage(tabId, {type:"MF_APPLY_SETTINGS", settings}); } catch {}
}

browser.runtime.onInstalled.addListener(() => {
  browser.contextMenus.removeAll().then(() => {
    browser.contextMenus.create({id:"mf-toggle", title:"DuskBloom Web: Toggle on this site", contexts:["page"]});
    browser.contextMenus.create({id:"mf-extra", title:"DuskBloom Web: Extra Dark", contexts:["page"]});
    browser.contextMenus.create({id:"mf-rescue", title:"DuskBloom Web: Site Rescue", contexts:["page"]});
    browser.contextMenus.create({id:"mf-reset", title:"DuskBloom Web: Reset this site", contexts:["page"]});
  });
});

browser.contextMenus.onClicked.addListener(async (info, tab) => {
  const host = hostFromUrl(tab.url);
  if (!host) return;
  if (info.menuItemId === "mf-reset") {
    await browser.storage.local.remove(key(host));
    return tell(tab.id, DEFAULTS);
  }
  const s = await getSite(host);
  let next = s;
  if (info.menuItemId === "mf-toggle") next = await setSite(host, {enabled: !s.enabled});
  if (info.menuItemId === "mf-extra") next = await setSite(host, {enabled:true, preset:"extra"});
  if (info.menuItemId === "mf-rescue") next = await setSite(host, {rescue: !s.rescue});
  tell(tab.id, next);
});

browser.commands.onCommand.addListener(async (command) => {
  if (command !== "toggle-migraine-filter") return;
  const [tab] = await browser.tabs.query({active:true, currentWindow:true});
  if (!tab) return;
  const host = hostFromUrl(tab.url);
  if (!host) return;
  const s = await getSite(host);
  const next = await setSite(host, {enabled: !s.enabled});
  tell(tab.id, next);
});
