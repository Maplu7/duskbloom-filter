const browser = globalThis.browser || globalThis.chrome;

const D={enabled:true,preset:"obsidian",customBg:"#171018",customPanel:"#241925",customRaised:"#332336",customText:"#ffffff",customMuted:"#cbb9c6",customAccent:"#e7a1c6"};
let tab,key,s;
async function push(){
 await browser.storage.local.set({[key]:s});
 try{await browser.tabs.sendMessage(tab.id,{type:"MF44_SET",settings:s})}catch(e){}
 draw();
}
function draw(){
 document.querySelector("#enabled").checked=s.enabled!==false;
 document.querySelectorAll("[data-preset]").forEach(b=>b.classList.toggle("active",b.dataset.preset===s.preset));
 ["customBg","customPanel","customRaised","customText","customMuted","customAccent"].forEach(id=>{
  document.querySelector("#"+id).value=s[id]||D[id];
 });
 document.querySelector("#status").textContent=s.enabled===false?"Off — original website":"On — "+(s.preset==="custom"?"My Colors":s.preset.replaceAll("_"," "));
}
(async()=>{
 [tab]=await browser.tabs.query({active:true,currentWindow:true});
 let host;try{host=new URL(tab.url).hostname}catch(e){return}
 key=`mf44:${host}`;
 s={...D,...((await browser.storage.local.get(key))[key]||{})};
 draw();

 document.querySelector("#enabled").addEventListener("change",async e=>{
  s={...s,enabled:e.target.checked};
  await push();
  /* no reload here: reload was causing the old on/off race */
 });

 document.querySelectorAll("[data-preset]").forEach(b=>b.addEventListener("click",async()=>{
  s={...s,enabled:true,preset:b.dataset.preset};
  await push();
 }));

 document.querySelector("#applyCustom").addEventListener("click",async()=>{
  const n={enabled:true,preset:"custom"};
  ["customBg","customPanel","customRaised","customText","customMuted","customAccent"].forEach(id=>n[id]=document.querySelector("#"+id).value);
  s={...s,...n};await push();
 });
})();
