
(() => {
 const KEY=`mf44:${location.hostname}`;
 const ID="mf44-theme";
 const ON="data-mf44-on";
 const DEFAULTS={
  enabled:true,preset:"obsidian",
  customBg:"#171018",customPanel:"#241925",customRaised:"#332336",
  customText:"#ffffff",customMuted:"#cbb9c6",customAccent:"#e7a1c6"
 };
 const P={
  pink_blackout:{bg:"#090609",panel:"#1b0e17",raised:"#34182a",text:"#fff",muted:"#d8b8c8",accent:"#ff77b5"},
  pink:{bg:"#321827",panel:"#542a42",raised:"#743a5c",text:"#fff",muted:"#edc4d8",accent:"#ff9dcc"},
  dark_pink:{bg:"#180a12",panel:"#351526",raised:"#55203d",text:"#fff",muted:"#d9aec2",accent:"#eb70ad"},
  rose_dim:{bg:"#28161c",panel:"#44262f",raised:"#603742",text:"#fff",muted:"#d9bbc2",accent:"#e18fa4"},
  dusty_rose:{bg:"#21151a",panel:"#38252c",raised:"#523640",text:"#fff",muted:"#d9c0c8",accent:"#d58fa5"},
  peach:{bg:"#2b1b15",panel:"#493026",raised:"#684538",text:"#fff",muted:"#ead0c2",accent:"#f2a47e"},
  sepia:{bg:"#201a12",panel:"#393024",raised:"#554837",text:"#fff",muted:"#d8c9ae",accent:"#c9a873"},
  sage:{bg:"#141b14",panel:"#263326",raised:"#3b4c3a",text:"#fff",muted:"#c5d3c1",accent:"#91b58b"},
  soft_cyan:{bg:"#101b1c",panel:"#203537",raised:"#315054",text:"#fff",muted:"#c1d8d9",accent:"#83bec1"},
  mauve:{bg:"#1d151d",panel:"#352635",raised:"#4e394c",text:"#fff",muted:"#d4c0d0",accent:"#b985b2"},
  smoke:{bg:"#151619",panel:"#292b30",raised:"#40434a",text:"#fff",muted:"#c7c9ce",accent:"#9ca1aa"},
  cocoa:{bg:"#1b1412",panel:"#302420",raised:"#493630",text:"#fff",muted:"#d4c4bd",accent:"#a77d6f"},
  navy:{bg:"#0c111c",panel:"#18243a",raised:"#263855",text:"#fff",muted:"#bdc9dc",accent:"#6f8fc4"},
  burgundy:{bg:"#1a0b0f",panel:"#34151e",raised:"#50202d",text:"#fff",muted:"#d9bac3",accent:"#b85d78"},
  lavender:{bg:"#171023",panel:"#32204b",raised:"#513471",text:"#fff",muted:"#d1bce7",accent:"#c08cff"},
  amber:{bg:"#261804",panel:"#493008",raised:"#6a470e",text:"#fff",muted:"#e5c98f",accent:"#ffb62f"},
  forest_green:{bg:"#0b1810",panel:"#173723",raised:"#23553a",text:"#fff",muted:"#b7d7c0",accent:"#63d28b"},
  warm_white:{bg:"#332c24",panel:"#514538",raised:"#6b5b49",text:"#fff",muted:"#e2d4c2",accent:"#efc486"},
  deep_red:{bg:"#1d0709",panel:"#401018",raised:"#631724",text:"#fff",muted:"#dfb0b6",accent:"#ed6273"},
  blue_light:{bg:"#0b1724",panel:"#173650",raised:"#245678",text:"#fff",muted:"#bdd8e8",accent:"#69c0f0"},
  dark_dimmer:{bg:"#131317",panel:"#292930",raised:"#41414c",text:"#fff",muted:"#c6c6cf",accent:"#aaa8bd"},
  midnight:{bg:"#060d1c",panel:"#102442",raised:"#183c69",text:"#fff",muted:"#b7cae5",accent:"#6da3ed"},
  obsidian:{bg:"#07070a",panel:"#111116",raised:"#1d1d24",text:"#fff",muted:"#bbb2bc",accent:"#d19bbc"}
 };

 let s={...DEFAULTS};

 function pal(){
  return s.preset==="custom" ? {
   bg:s.customBg,panel:s.customPanel,raised:s.customRaised,
   text:s.customText,muted:s.customMuted,accent:s.customAccent
  } : (P[s.preset]||P.obsidian);
 }

 function clear(){
  document.getElementById(ID)?.remove();
  const r=document.documentElement;
  r.removeAttribute(ON);
  ["--mf-bg","--mf-panel","--mf-raised","--mf-text","--mf-muted","--mf-accent"].forEach(v=>r.style.removeProperty(v));
 }

 function apply(){
  clear();
  if(s.enabled===false) return; // IMPORTANT: never auto-reenable after OFF
  const p=pal(),r=document.documentElement;
  r.setAttribute(ON,"1");
  Object.entries(p).forEach(([k,v])=>r.style.setProperty("--mf-"+k,v,"important"));
  const st=document.createElement("style");st.id=ID;
  st.textContent=`
   html[${ON}="1"],html[${ON}="1"] body{background:var(--mf-bg)!important;color:var(--mf-text)!important;color-scheme:dark!important}
   html[${ON}="1"] :where(#wrapper,#main,#not_right_side,#content-wrapper,#content,.ic-Layout-contentWrapper,.ic-Layout-contentMain){
    background:var(--mf-bg)!important;background-color:var(--mf-bg)!important;color:var(--mf-text)!important}
   html[${ON}="1"] :where(.header-bar,.page-toolbar,.form-actions,.item-group-container,.item-group-condensed,
    .context_module,.context_module_item,.ig-list,.ig-row,.ig-row-empty,.content,.content_details,
    .module-sequence-footer-content,.ui-dialog,.ui-dialog-content,.ui-widget-content,.ui-menu,.ui-autocomplete,
    .popover,.panel,.well,.list-group){
    background:var(--mf-panel)!important;background-color:var(--mf-panel)!important;color:var(--mf-text)!important}
   html[${ON}="1"] :where(input:not([type=checkbox]):not([type=radio]),textarea,select,[contenteditable=true],button,[role=button],.btn,.Button){
    background:var(--mf-raised)!important;background-color:var(--mf-raised)!important;color:var(--mf-text)!important;
    -webkit-text-fill-color:var(--mf-text)!important;border-color:var(--mf-accent)!important}
   html[${ON}="1"] a:not(.ic-app-header__menu-list-link){color:var(--mf-accent)!important}

   /* Cards */
   html[${ON}="1"] .ic-DashboardCard{background:transparent!important}
   html[${ON}="1"] .ic-DashboardCard :where(.ic-DashboardCard__content,.ic-DashboardCard__action-container,
    .ic-DashboardCard__assignments,.ic-DashboardCard__assignment,.ic-DashboardCard__assignments-list,
    .ic-DashboardCard__body,.ic-DashboardCard__footer){
    background:var(--mf-panel)!important;background-color:var(--mf-panel)!important;color:var(--mf-text)!important;
    animation:none!important;transition:none!important}
   html[${ON}="1"] .ic-DashboardCard__action-container{background:var(--mf-raised)!important;background-color:var(--mf-raised)!important}

   /* Sidebar */
   html[${ON}="1"] .ic-app-header{background:#111116!important}
   html[${ON}="1"] .ic-app-header :where(.ic-app-header__menu-list-link,.menu-item__text,.ic-icon-svg){
    color:#fff!important;-webkit-text-fill-color:#fff!important;opacity:1!important}
   html[${ON}="1"] .ic-app-header svg,html[${ON}="1"] .ic-app-header svg *{color:#fff!important;fill:currentColor!important;opacity:1!important}

   /* Images/course artwork are NEVER filtered */
   html[${ON}="1"] :where(img,picture,video,canvas,[role=img],.ic-DashboardCard__header,
    .ic-DashboardCard__header_hero,.ic-DashboardCard__header_image){
    filter:none!important;-webkit-filter:none!important;opacity:1!important;mix-blend-mode:normal!important;visibility:visible!important}
   html[${ON}="1"] :where(.ic-DashboardCard__header,.ic-DashboardCard__header_hero,.ic-DashboardCard__header_image){
    background-color:transparent!important}

   /* Google Docs */
   html[${ON}="1"] body:has(.docs-editor-container) :where(.docs-editor-container,.kix-appview-editor,
    .kix-appview-editor-container,.kix-page,.kix-page-content-wrapper,.kix-page-content){
    background:#09090c!important;background-color:#09090c!important}
   html[${ON}="1"] body:has(.docs-editor-container) :where(.kix-lineview-text-block,.kix-lineview-text-block *,
    .kix-lineview-content,.kix-lineview-content *,.kix-wordhtmlgenerator-word-node,.docs-title-input,.docs-title-input-label){
    color:#fff!important;-webkit-text-fill-color:#fff!important}
   html[${ON}="1"] body:has(.docs-editor-container) :where(#docs-chrome,.docs-material,.docs-menubar,
    .docs-toolbar-wrapper,.docs-primary-toolbars,.goog-toolbar){
    background:var(--mf-panel)!important;background-color:var(--mf-panel)!important;color:#fff!important}
  `;
  (document.head||document.documentElement).appendChild(st);
 }

 browser.storage.local.get(KEY).then(o=>{s={...DEFAULTS,...(o[KEY]||{})};apply()});
 browser.storage.onChanged.addListener((c,a)=>{
  if(a!=="local"||!c[KEY])return;
  s={...DEFAULTS,...(c[KEY].newValue||{})};
  apply();
 });
 browser.runtime.onMessage.addListener(msg=>{
  if(msg?.type==="MF44_SET"){
   s={...DEFAULTS,...msg.settings};
   apply();
  }
 });
})();


/* ============================================================
   V45 — RESTORE OLD GOOGLE DOCS LOOK
   Restores the earlier dark-page Docs treatment from the stable pre-rebuild
   version while keeping V44 controls/themes/off behavior untouched.
   ============================================================ */
(() => {
 const KEY=`mf44:${location.hostname}`;
 const ID="mf45-old-docs";
 if(location.hostname!=="docs.google.com") return;

 function remove(){document.getElementById(ID)?.remove();}
 function apply(s){
   remove();
   if(s?.enabled===false) return;
   const st=document.createElement("style"); st.id=ID;
   st.textContent=`
     html[data-mf44-on="1"] body,
     html[data-mf44-on="1"] .docs-editor-container,
     html[data-mf44-on="1"] .docs-editor,
     html[data-mf44-on="1"] .kix-appview-editor,
     html[data-mf44-on="1"] .kix-appview-editor-container,
     html[data-mf44-on="1"] .kix-appview-editor-container-inner,
     html[data-mf44-on="1"] .kix-editor,
     html[data-mf44-on="1"] .kix-page-paginated,
     html[data-mf44-on="1"] .kix-page-paginated-container {
       background:#111216 !important;
     }

     html[data-mf44-on="1"] .kix-page,
     html[data-mf44-on="1"] .kix-page-content-wrapper,
     html[data-mf44-on="1"] .kix-page-content {
       background:#18191e !important;
       background-color:#18191e !important;
       box-shadow:0 0 0 1px #393a42,0 10px 32px rgba(0,0,0,.38) !important;
     }

     html[data-mf44-on="1"] :is(
       .kix-lineview,.kix-lineview-content,.kix-lineview-text-block,
       .kix-wordhtmlgenerator-word-node,.kix-lineview-text-block span,
       .kix-lineview-content span
     ){
       color:#ffffff !important;
       -webkit-text-fill-color:#ffffff !important;
     }

     html[data-mf44-on="1"] .kix-cursor-caret{border-color:#ffb6d6 !important}
     html[data-mf44-on="1"] :is(.kix-selection-overlay,.kix-selection-overlay-container){
       mix-blend-mode:screen !important;
     }

     /* Restore old toolbar/title treatment, but use the currently selected theme. */
     html[data-mf44-on="1"] :is(
       #docs-header,#docs-bars,#docs-toolbar-wrapper,.docs-titlebar,.docs-menubar,
       .docs-toolbar-wrapper,.docs-primary-toolbars,.goog-toolbar,
       .goog-toolbar-button,.goog-toolbar-combo-button,.goog-toolbar-menu-button,
       .docs-material-gm-select-outer-box,.docs-material-gm-select-inner-box
     ){
       background-color:var(--mf-panel,#111116) !important;
       color:#ffffff !important;
       border-color:#55515c !important;
     }

     html[data-mf44-on="1"] :is(
       #docs-title-input,.docs-title-input,.docs-title-input-label,
       .docs-titlebar .docs-title-input,input.docs-title-input
     ){
       background-color:var(--mf-panel,#111116) !important;
       color:#ffffff !important;
       -webkit-text-fill-color:#ffffff !important;
       caret-color:#ffb6d6 !important;
       border-color:#55515c !important;
       opacity:1 !important;
     }

     /* Modern Docs canvas rendering: this is the old working behavior that
        darkened the white canvas while keeping the document readable. */
     html[data-mf44-on="1"] :is(
       canvas.kix-canvas-tile-content,.kix-canvas-tile-content,
       .kix-canvas-tile-content canvas,.kix-canvas-tile-selection,
       .kix-canvas-tile-content-container canvas
     ){
       filter:invert(.88) hue-rotate(180deg) brightness(.82) contrast(.92) !important;
     }
   `;
   (document.head||document.documentElement).appendChild(st);
 }
 browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
 browser.storage.onChanged.addListener((c,a)=>{
   if(a==="local"&&c[KEY]) apply({enabled:true,...(c[KEY].newValue||{})});
 });
 browser.runtime.onMessage.addListener(msg=>{
   if(msg?.type==="MF44_SET") apply(msg.settings||{enabled:true});
 });
})();


/* V46 — Canvas artwork protection only. V45 behavior otherwise unchanged. */
(() => {
 if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
 const KEY=`mf44:${location.hostname}`, ID="mf46-canvas-artwork";
 const remove=()=>document.getElementById(ID)?.remove();
 function apply(s){
   remove(); if(s?.enabled===false) return;
   const st=document.createElement("style"); st.id=ID;
   st.textContent=`
     /* Protect real media. */
     html[data-mf44-on="1"] :is(img,picture,video,canvas,[role="img"]){
       filter:none!important;-webkit-filter:none!important;opacity:1!important;
       mix-blend-mode:normal!important;visibility:visible!important;
     }

     /* Protect Canvas course artwork, including CSS background images.
        Do NOT override background-image. */
     html[data-mf44-on="1"] :is(
       .ic-DashboardCard__header,
       .ic-DashboardCard__header_hero,
       .ic-DashboardCard__header_image,
       .ic-DashboardCard [style*="background-image"]
     ){
       filter:none!important;-webkit-filter:none!important;opacity:1!important;
       mix-blend-mode:normal!important;visibility:visible!important;
       background-color:transparent!important;
     }

     /* Keep theme paint only on the lower card UI. */
     html[data-mf44-on="1"] .ic-DashboardCard :is(
       .ic-DashboardCard__content,.ic-DashboardCard__action-container,
       .ic-DashboardCard__assignments,.ic-DashboardCard__assignment,
       .ic-DashboardCard__assignments-list,.ic-DashboardCard__body,.ic-DashboardCard__footer
     ){
       background-color:var(--mf-panel)!important;color:var(--mf-text)!important;
     }
     html[data-mf44-on="1"] .ic-DashboardCard__action-container{
       background-color:var(--mf-raised)!important;
     }
   `;
   (document.head||document.documentElement).appendChild(st);
 }
 browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
 browser.storage.onChanged.addListener((c,a)=>{if(a==="local"&&c[KEY])apply({enabled:true,...(c[KEY].newValue||{})})});
 browser.runtime.onMessage.addListener(msg=>{if(msg?.type==="MF44_SET")apply(msg.settings||{enabled:true})});
})();


/* V47 — preserve Canvas artwork + theme remaining Canvas containers */
(() => {
 if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
 const KEY=`mf44:${location.hostname}`, ID="mf47-canvas";
 const remove=()=>document.getElementById(ID)?.remove();
 function apply(s){
  remove(); if(s?.enabled===false)return;
  const st=document.createElement("style"); st.id=ID;
  st.textContent=`
   /* Never touch Snoopy/course artwork or real media. */
   html[data-mf44-on="1"] #dashboard :is(
    img,picture,video,canvas,[role="img"],
    .ic-DashboardCard__header,.ic-DashboardCard__header_hero,.ic-DashboardCard__header_image,
    [style*="background-image"]
   ){
    filter:none!important;-webkit-filter:none!important;opacity:1!important;
    visibility:visible!important;mix-blend-mode:normal!important;
   }
   html[data-mf44-on="1"] #dashboard :is(
    .ic-DashboardCard__header,.ic-DashboardCard__header_hero,.ic-DashboardCard__header_image,
    [style*="background-image"]
   ){background-color:transparent!important}

   /* Theme Canvas main-page containers, but never artwork/background-image nodes. */
   html[data-mf44-on="1"] #not_right_side :is(
    section,article,fieldset,dialog,table,thead,tbody,tfoot,tr,td,th,ul,ol,li,
    [role="dialog"],[role="menu"],[role="listbox"],[role="option"],[role="tabpanel"],[role="region"],
    [class*="container" i],[class*="panel" i],[class*="content" i],[class*="module" i],
    [class*="item" i],[class*="row" i],[class*="list" i],[class*="card" i],
    [class*="assignment" i],[class*="todo" i],[class*="due" i],
    [class*="announcement" i],[class*="feedback" i],[class*="popover" i],
    [class*="dialog" i],[class*="modal" i],[class*="toolbar" i]
   ):not(.ic-DashboardCard__header):not(.ic-DashboardCard__header_hero):
     not(.ic-DashboardCard__header_image):not([style*="background-image"]){
    background-color:var(--mf-panel)!important;color:var(--mf-text)!important;
    border-color:color-mix(in srgb,var(--mf-muted) 30%,transparent)!important;
   }

   /* Specifically catch stubborn lower card/module nested containers. */
   html[data-mf44-on="1"] #not_right_side :is(
    .ic-DashboardCard__content,.ic-DashboardCard__action-container,
    .ic-DashboardCard__assignments,.ic-DashboardCard__assignment,
    .ic-DashboardCard__assignments-list,.ic-DashboardCard__body,.ic-DashboardCard__footer,
    .context_module,.context_module_item,.item-group-container,.item-group-condensed,
    .ig-list,.ig-row,.ig-row-empty
   ),
   html[data-mf44-on="1"] #not_right_side :is(
    .ic-DashboardCard__content,.ic-DashboardCard__assignments,.ic-DashboardCard__assignment,
    .ic-DashboardCard__assignments-list,.ic-DashboardCard__body,.ic-DashboardCard__footer,
    .context_module,.context_module_item,.item-group-container,.item-group-condensed,
    .ig-list,.ig-row,.ig-row-empty
   ) > :is(div,section,article,ul,li){
    background-color:var(--mf-panel)!important;color:var(--mf-text)!important;
   }
   html[data-mf44-on="1"] #not_right_side :is(
    button,[role="button"],input:not([type="checkbox"]):not([type="radio"]),
    textarea,select,.btn,.Button,.ic-DashboardCard__action-container
   ){background-color:var(--mf-raised)!important;color:var(--mf-text)!important}

   /* Reassert media after all broad rules. */
   html[data-mf44-on="1"] #not_right_side :is(img,picture,video,canvas,[role="img"]){
    filter:none!important;-webkit-filter:none!important;opacity:1!important;
    visibility:visible!important;mix-blend-mode:normal!important;background-color:transparent!important;
   }
  `;
  (document.head||document.documentElement).appendChild(st);
 }
 browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
 browser.storage.onChanged.addListener((c,a)=>{if(a==="local"&&c[KEY])apply({enabled:true,...(c[KEY].newValue||{})})});
 browser.runtime.onMessage.addListener(msg=>{if(msg?.type==="MF44_SET")apply(msg.settings||{enabled:true})});
})();


/* ============================================================
   V48 — EXACT CANVAS FIXES FROM INSPECTOR HTML
   ============================================================ */
(() => {
 if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
 const KEY=`mf44:${location.hostname}`, ID="mf48-exact-canvas";
 const remove=()=>document.getElementById(ID)?.remove();

 function apply(s){
  remove(); if(s?.enabled===false)return;
  const st=document.createElement("style"); st.id=ID;
  st.textContent=`
   /* DASHBOARD TOP HEADER */
   html[data-mf44-on="1"] .ic-Dashboard-header__layout,
   html[data-mf44-on="1"] .ic-Dashboard-header__actions,
   html[data-mf44-on="1"] #DashboardOptionsMenu_Container,
   html[data-mf44-on="1"] #dashboard-planner-header,
   html[data-mf44-on="1"] #dashboard-planner-header-aux {
     background-color:var(--mf-panel)!important;
     color:var(--mf-text)!important;
     border-color:var(--mf-muted)!important;
   }
   html[data-mf44-on="1"] .ic-Dashboard-header__layout :is(
     span,h1,h2,h3,p,label
   ){
     color:var(--mf-text)!important;
     -webkit-text-fill-color:var(--mf-text)!important;
   }
   html[data-mf44-on="1"] .ic-Dashboard-header__layout button {
     background-color:var(--mf-raised)!important;
     color:var(--mf-text)!important;
     -webkit-text-fill-color:var(--mf-text)!important;
     border-color:var(--mf-accent)!important;
   }
   html[data-mf44-on="1"] .ic-Dashboard-header__layout button svg,
   html[data-mf44-on="1"] .ic-Dashboard-header__layout button svg * {
     fill:var(--mf-text)!important;
     color:var(--mf-text)!important;
   }

   /* COURSE ART / SNOOPY
      The actual image is a CSS background-image on __header_image.
      Keep that image and REMOVE Canvas's translucent color veil over it. */
   html[data-mf44-on="1"] .ic-DashboardCard__header_image {
     filter:none!important;
     -webkit-filter:none!important;
     opacity:1!important;
     visibility:visible!important;
     mix-blend-mode:normal!important;
     background-color:transparent!important;
     background-repeat:no-repeat!important;
     background-position:center!important;
     background-size:cover!important;
   }
   html[data-mf44-on="1"] .ic-DashboardCard__header_hero,
   html[data-mf44-on="1"] .ic-DashboardCard__header-button-bg {
     background:transparent!important;
     background-color:transparent!important;
   }
   html[data-mf44-on="1"] .ic-DashboardCard__header_hero {
     opacity:0!important;
     pointer-events:none!important;
   }

   /* Keep header content readable WITHOUT painting over the artwork. */
   html[data-mf44-on="1"] .ic-DashboardCard__header,
   html[data-mf44-on="1"] .ic-DashboardCard__header_content,
   html[data-mf44-on="1"] .ic-DashboardCard__link {
     background-color:transparent!important;
   }
   html[data-mf44-on="1"] .ic-DashboardCard__header :is(img,picture,video,canvas,[role="img"]) {
     filter:none!important;opacity:1!important;visibility:visible!important;
   }

   /* BETTER CANVAS "DUE" CARD — exact classes from the inspector dump */
   html[data-mf44-on="1"] .bettercanvas-card-assignment,
   html[data-mf44-on="1"] .bettercanvas-card-header-container,
   html[data-mf44-on="1"] .bettercanvas-card-container,
   html[data-mf44-on="1"] .bettercanvas-assignment-container {
     background:var(--mf-panel)!important;
     background-color:var(--mf-panel)!important;
     color:var(--mf-text)!important;
     border-color:var(--mf-muted)!important;
     animation:none!important;
     transition:none!important;
   }
   html[data-mf44-on="1"] .bettercanvas-card-header,
   html[data-mf44-on="1"] .bettercanvas-assignment-dueat {
     color:var(--mf-text)!important;
     -webkit-text-fill-color:var(--mf-text)!important;
   }
   html[data-mf44-on="1"] .bettercanvas-assignment-link {
     color:var(--mf-accent)!important;
     -webkit-text-fill-color:var(--mf-accent)!important;
   }

   /* BETTER CANVAS GPA containers shown in the same inspector dump */
   html[data-mf44-on="1"] :is(
     .bettercanvas-gpa-card,.bettercanvas-gpa,.bettercanvas-gpa-courses-container,
     .bettercanvas-gpa-courses,.bettercanvas-gpa-course,
     .bettercanvas-gpa-percent-container,.bettercanvas-course-weights,
     .bettercanvas-course-credits
   ){
     background:var(--mf-panel)!important;
     background-color:var(--mf-panel)!important;
     color:var(--mf-text)!important;
     border-color:var(--mf-muted)!important;
   }

   /* BETTER CANVAS reminder popups — exact selector from the working older fix */
   html[data-mf44-on="1"] #bettercanvas-reminders,
   html[data-mf44-on="1"] #bettercanvas-reminders .bettercanvas-reminder-wrapper,
   html[data-mf44-on="1"] #bettercanvas-reminders .bettercanvas-reminder-wrapper > div {
     background:var(--mf-panel)!important;
     background-color:var(--mf-panel)!important;
     color:var(--mf-text)!important;
     border-color:var(--mf-muted)!important;
     animation:none!important;
     transition:none!important;
   }
   html[data-mf44-on="1"] #bettercanvas-reminders :is(
     p,span,label,strong,small,h1,h2,h3,h4,h5,h6
   ){
     color:var(--mf-text)!important;
     -webkit-text-fill-color:var(--mf-text)!important;
   }
   html[data-mf44-on="1"] #bettercanvas-reminders :is(button,[role="button"]) {
     background:var(--mf-raised)!important;
     background-color:var(--mf-raised)!important;
     color:var(--mf-text)!important;
     border-color:var(--mf-accent)!important;
   }

   /* Final media protection: must come LAST. */
   html[data-mf44-on="1"] :is(
     img,picture,video,canvas,[role="img"],
     .ic-DashboardCard__header_image
   ){
     filter:none!important;
     -webkit-filter:none!important;
     opacity:1!important;
     visibility:visible!important;
     mix-blend-mode:normal!important;
   }
  `;
  (document.head||document.documentElement).appendChild(st);
 }
 browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
 browser.storage.onChanged.addListener((c,a)=>{if(a==="local"&&c[KEY])apply({enabled:true,...(c[KEY].newValue||{})})});
 browser.runtime.onMessage.addListener(msg=>{if(msg?.type==="MF44_SET")apply(msg.settings||{enabled:true})});
})();


/* V49 — exact Better Canvas reminder card coverage */
(() => {
 if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
 const KEY=`mf44:${location.hostname}`, ID="mf49-reminders";
 const remove=()=>document.getElementById(ID)?.remove();
 function apply(s){
  remove(); if(s?.enabled===false)return;
  const st=document.createElement("style"); st.id=ID;
  st.textContent=`
    html[data-mf44-on="1"] .bettercanvas-reminder-wrapper,
    html[data-mf44-on="1"] .bettercanvas-reminder-container,
    html[data-mf44-on="1"] .bettercanvas-reminder-content {
      background:var(--mf-panel)!important;
      background-color:var(--mf-panel)!important;
      color:var(--mf-text)!important;
      border-color:var(--mf-muted)!important;
      box-shadow:none!important;
      animation:none!important;
      transition:none!important;
    }

    html[data-mf44-on="1"] .bettercanvas-reminder-wrapper > *,
    html[data-mf44-on="1"] .bettercanvas-reminder-container > div {
      background-color:transparent!important;
    }

    html[data-mf44-on="1"] .bettercanvas-reminder-title,
    html[data-mf44-on="1"] .bettercanvas-reminder-due {
      color:var(--mf-text)!important;
      -webkit-text-fill-color:var(--mf-text)!important;
    }

    html[data-mf44-on="1"] .bettercanvas-reminder-content {
      text-decoration:none!important;
    }

    html[data-mf44-on="1"] .bettercanvas-reminder-hide {
      background:var(--mf-raised)!important;
      background-color:var(--mf-raised)!important;
      color:var(--mf-text)!important;
      -webkit-text-fill-color:var(--mf-text)!important;
      border-color:var(--mf-muted)!important;
    }

    /* Preserve the red reminder icon rather than recoloring/hiding it. */
    html[data-mf44-on="1"] .bettercanvas-reminder-container svg {
      filter:none!important;
      opacity:1!important;
      visibility:visible!important;
      background:transparent!important;
    }
    html[data-mf44-on="1"] .bettercanvas-reminder-container svg path {
      fill:#ff4545!important;
    }
  `;
  (document.head||document.documentElement).appendChild(st);
 }
 browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
 browser.storage.onChanged.addListener((c,a)=>{if(a==="local"&&c[KEY])apply({enabled:true,...(c[KEY].newValue||{})})});
 browser.runtime.onMessage.addListener(msg=>{if(msg?.type==="MF44_SET")apply(msg.settings||{enabled:true})});
})();


/* ============================================================
   V50 — UNIVERSAL CONTAINER ENGINE
   Broad, defensive coverage for bright UI containers on arbitrary sites.
   Keeps media/artwork intact and follows dynamically inserted SPA content.
   ============================================================ */
(() => {
  const KEY = `mf44:${location.hostname}`;
  const STYLE_ID = "mf50-universal-containers";
  const MARK = "data-mf50-container";
  const BRIGHT = "data-mf50-bright";
  const SHADOW_STYLE = "mf50-shadow-style";
  const DEFAULTS = { enabled:true, preset:"obsidian" };
  let state = {...DEFAULTS};
  let queued = false;

  const SKIP_TAGS = new Set(["IMG","PICTURE","VIDEO","CANVAS","SVG","PATH","IFRAME","OBJECT","EMBED","SCRIPT","STYLE","LINK","META"]);
  const CONTAINER_HINT = /(container|panel|card|dialog|modal|popover|menu|dropdown|drawer|sidebar|toolbar|header|footer|content|wrapper|surface|paper|sheet|box|tile|module|widget|notice|alert|toast|list|row|item|section|main|nav|form)/i;

  function enabled(){ return state.enabled !== false && document.documentElement?.getAttribute("data-mf44-on")==="1"; }

  function parseColor(v){
    if(!v || v==="transparent") return null;
    const m=v.match(/rgba?\(([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)(?:[ ,/]+([\d.]+))?\)/i);
    if(!m) return null;
    const a=m[4]===undefined?1:Number(m[4]);
    if(a < .08) return null;
    return [Number(m[1]),Number(m[2]),Number(m[3]),a];
  }
  function luminance(rgb){
    if(!rgb) return 0;
    const [r,g,b]=rgb;
    return (0.2126*r+0.7152*g+0.0722*b)/255;
  }
  function isMedia(el){
    if(!el || el.nodeType!==1) return true;
    if(SKIP_TAGS.has(el.tagName)) return true;
    if(el.matches?.('img,picture,video,canvas,svg,[role="img"],[style*="background-image"]')) return true;
    try {
      const cs=getComputedStyle(el);
      if(cs.backgroundImage && cs.backgroundImage!=="none") return true;
    } catch(e){}
    return false;
  }
  function isCanvasLMS(){
    return /(^|\.)instructure\.com$/i.test(location.hostname);
  }
  function canvasProtected(el){
    if(!isCanvasLMS() || !el?.closest) return false;
    return !!el.closest([
      "#left-side",
      "#right-side-wrapper",
      "#right-side",
      "#assignment_show",
      ".assignment-title",
      ".assignment-buttons",
      ".assignment_dates",
      ".student-assignment-overview",
      ".ic-Layout-columns",
      ".ic-Layout-contentMain",
      ".ic-Layout-contentWrapper",
      ".ic-app-nav-toggle-and-crumbs",
      ".ic-app-nav-toggle-and-crumbs__button",
      ".header-bar",
      ".module-sequence-footer",
      ".module-sequence-footer-content",
      ".comments",
      ".comment_list",
      ".submission-details",
      ".submission-details-header",
      ".rubric_container",
      ".rubric",
      ".enhanced-rubric",
      "[data-testid*='assignment']",
      "[class*='Assignment']"
    ].join(","));
  }
  function looksLikeContainer(el){
    if(!el || el.nodeType!==1 || isMedia(el)) return false;
    // Canvas already has targeted compatibility rules earlier in this file.
    // Do not let the generic v50 engine recolor its assignment/side-column UI.
    if(canvasProtected(el)) return false;
    if(el===document.documentElement || el===document.body) return true;
    const role=(el.getAttribute("role")||"").toLowerCase();
    if(/dialog|menu|listbox|navigation|main|region|toolbar|alert|status|tabpanel|form/.test(role)) return true;
    const hint=((el.id||"")+" "+(typeof el.className==="string"?el.className:""));
    if(CONTAINER_HINT.test(hint)) return true;
    const kids=el.children?.length||0;
    if(kids >= 2) return true;
    return false;
  }
  function inspect(el){
    if(canvasProtected(el)){
      el?.removeAttribute?.(MARK); el?.removeAttribute?.(BRIGHT); return;
    }
    if(!enabled() || !looksLikeContainer(el)) {
      el?.removeAttribute?.(MARK); el?.removeAttribute?.(BRIGHT); return;
    }
    try{
      const cs=getComputedStyle(el);
      const bg=parseColor(cs.backgroundColor);
      const lum=luminance(bg);
      const rect=el.getBoundingClientRect();
      const meaningful = rect.width>=40 && rect.height>=20;
      if(!meaningful){ el.removeAttribute(MARK); el.removeAttribute(BRIGHT); return; }
      if(bg && lum >= .72){
        el.setAttribute(MARK,"1");
        if(lum >= .88) el.setAttribute(BRIGHT,"1"); else el.removeAttribute(BRIGHT);
      } else {
        el.removeAttribute(MARK); el.removeAttribute(BRIGHT);
      }
    }catch(e){}
  }
  function scan(root=document){
    if(!enabled()) return cleanupMarks();
    if(root.nodeType===1) inspect(root);
    const selector = isCanvasLMS()
      ? 'dialog,[role="dialog"],[role="alertdialog"],[role="menu"],[role="listbox"],[role="tooltip"],.ui-dialog,.ui-menu,.ui-datepicker,.popover,.tray-with-space-for-global-nav'
      : 'div,section,article,main,aside,nav,header,footer,form,fieldset,table,thead,tbody,tr,td,th,ul,ol,li,details,summary,[role],[class],[id]';
    const els=root.querySelectorAll?.(selector)||[];
    for(const el of els) inspect(el);
    scanOpenShadowRoots(root);
  }
  function cleanupMarks(){
    document.querySelectorAll?.(`[${MARK}],[${BRIGHT}]`).forEach(el=>{el.removeAttribute(MARK);el.removeAttribute(BRIGHT)});
  }
  function shadowCSS(){
    return `
      :host-context(html[data-mf44-on="1"]) [${MARK}="1"]{
        background-color:var(--mf-panel,#111116)!important;
        color:var(--mf-text,#fff)!important;
        border-color:color-mix(in srgb,var(--mf-muted,#bbb2bc) 42%,transparent)!important;
      }
      :host-context(html[data-mf44-on="1"]) [${BRIGHT}="1"]{
        background-color:var(--mf-raised,#1d1d24)!important;
      }
      :host-context(html[data-mf44-on="1"]) input,
      :host-context(html[data-mf44-on="1"]) textarea,
      :host-context(html[data-mf44-on="1"]) select{
        background-color:var(--mf-raised,#1d1d24)!important;
        color:var(--mf-text,#fff)!important;
      }`;
  }
  function injectShadow(root){
    if(!root || root.querySelector?.(`#${SHADOW_STYLE}`)) return;
    try{
      const st=document.createElement("style"); st.id=SHADOW_STYLE; st.textContent=shadowCSS();
      root.appendChild(st);
    }catch(e){}
  }
  function scanOpenShadowRoots(root=document){
    const all=root.querySelectorAll?.("*")||[];
    for(const el of all){
      if(el.shadowRoot){
        injectShadow(el.shadowRoot);
        scan(el.shadowRoot);
      }
    }
  }
  function installStyle(){
    document.getElementById(STYLE_ID)?.remove();
    const st=document.createElement("style"); st.id=STYLE_ID;
    st.textContent=`
      html[data-mf44-on="1"] [${MARK}="1"]{
        background:var(--mf-panel)!important;
        background-color:var(--mf-panel)!important;
        color:var(--mf-text)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 42%,transparent)!important;
      }
      html[data-mf44-on="1"] [${BRIGHT}="1"]{
        background:var(--mf-raised)!important;
        background-color:var(--mf-raised)!important;
      }
      html[data-mf44-on="1"] [${MARK}="1"] :is(p,span,label,strong,small,h1,h2,h3,h4,h5,h6){
        color:inherit;
      }
      html[data-mf44-on="1"]:not([data-mf50-canvas="1"]) :is(dialog,[role="dialog"],[role="alertdialog"],[role="menu"],[role="listbox"],[role="tooltip"]){
        background-color:var(--mf-panel)!important;color:var(--mf-text)!important;
      }
      html[data-mf44-on="1"]:not([data-mf50-canvas="1"]) :is(input:not([type="checkbox"]):not([type="radio"]),textarea,select,[contenteditable="true"]){
        background-color:var(--mf-raised)!important;color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
      }
      html[data-mf44-on="1"] :is(img,picture,video,canvas,svg,[role="img"],[style*="background-image"]){
        filter:none!important;-webkit-filter:none!important;opacity:1!important;visibility:visible!important;
      }`;
    (document.head||document.documentElement).appendChild(st);
  }
  function queue(root=document){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>{queued=false; scan(root)});
  }

  // Catch open shadow roots created after page load.
  try{
    const original=Element.prototype.attachShadow;
    if(!original.__mf50){
      const patched=function(init){
        const root=original.call(this,init);
        if(init?.mode==="open"){setTimeout(()=>{injectShadow(root);scan(root)},0)}
        return root;
      };
      patched.__mf50=true;
      Element.prototype.attachShadow=patched;
    }
  }catch(e){}

  installStyle();
  if(isCanvasLMS()) document.documentElement?.setAttribute("data-mf50-canvas","1");
  browser.storage.local.get(KEY).then(d=>{state={...DEFAULTS,...(d[KEY]||{})};queue(document)});
  browser.storage.onChanged.addListener((c,a)=>{
    if(a!=="local"||!c[KEY])return;
    state={...DEFAULTS,...(c[KEY].newValue||{})};
    if(enabled()) queue(document); else cleanupMarks();
  });
  browser.runtime.onMessage.addListener(msg=>{
    if(msg?.type==="MF44_SET"){
      state={...DEFAULTS,...(msg.settings||{})};
      setTimeout(()=>enabled()?queue(document):cleanupMarks(),0);
    }
  });

  const mo=new MutationObserver(muts=>{
    if(!enabled()) return;
    for(const m of muts){
      for(const n of m.addedNodes||[]){
        if(n.nodeType===1) queue(n);
      }
      if(m.type==="attributes" && m.target?.nodeType===1) queue(m.target);
    }
  });
  const start=()=> {
    if(document.documentElement) {
      mo.observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:["class","style","role","open","hidden"]});
      queue(document);
    }
  };
  if(document.documentElement) start(); else document.addEventListener("DOMContentLoaded",start,{once:true});

  // SPA/navigation safety pass without constant heavy scanning.
  let lastURL=location.href;
  setInterval(()=>{
    if(location.href!==lastURL){lastURL=location.href;queue(document)}
  },1200);
})();


/* ============================================================
   V52 — CANVAS SYLLABUS / ASSIGNMENT SIDEBAR TABLE FIX
   Exact selectors from the user's Canvas inspector HTML.
   ============================================================ */
(() => {
  if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
  const KEY=`mf44:${location.hostname}`;
  const ID="mf52-canvas-tables";
  const remove=()=>document.getElementById(ID)?.remove();

  function apply(s){
    remove();
    if(s?.enabled===false) return;

    const st=document.createElement("style");
    st.id=ID;
    st.textContent=`
      /* Course Summary / Syllabus assignment rows.
         The real Canvas rows use:
         tr.detail_list.syllabus_assignment,
         th.day_date, td.name, td.dates. */
      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment,
      html[data-mf44-on="1"] tr.date.detail_list,
      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment > th.day_date,
      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment > td.name,
      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment > td.dates,
      html[data-mf44-on="1"] tr.date.detail_list > th.day_date,
      html[data-mf44-on="1"] tr.date.detail_list > td.name,
      html[data-mf44-on="1"] tr.date.detail_list > td.dates {
        background:var(--mf-bg)!important;
        background-color:var(--mf-bg)!important;
        color:var(--mf-text)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 38%,transparent)!important;
        opacity:1!important;
        filter:none!important;
      }

      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment :is(
        a,span,i,button,strong,small
      ){
        opacity:1!important;
        filter:none!important;
      }

      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment a {
        color:var(--mf-accent)!important;
        -webkit-text-fill-color:var(--mf-accent)!important;
      }

      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment :is(
        th.day_date,td.dates
      ),
      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment :is(
        th.day_date,td.dates
      ) * {
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
      }

      /* Canvas due-time buttons arrive with huge inline "unset" style blocks.
         Keep them dark but subtle instead of gray/white. */
      html[data-mf44-on="1"] tr.detail_list.syllabus_assignment
      .tooltip-time-mount button[data-popover-trigger="true"] {
        background:var(--mf-raised)!important;
        background-color:var(--mf-raised)!important;
        color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
        border:1px solid color-mix(in srgb,var(--mf-muted) 35%,transparent)!important;
        border-radius:4px!important;
        opacity:1!important;
      }

      /* Right-side assignment-group blocks / "Upcoming Assignments".
         Exact toggle uses aria-controls=assignment_group_upcoming_assignments. */
      html[data-mf44-on="1"] button.element_toggler.accessible-toggler[
        aria-controls="assignment_group_upcoming_assignments"
      ],
      html[data-mf44-on="1"] #assignment_group_upcoming_assignments,
      html[data-mf44-on="1"] #assignment_group_upcoming_assignments :is(
        table,thead,tbody,tfoot,tr,th,td
      ) {
        background:var(--mf-panel)!important;
        background-color:var(--mf-panel)!important;
        color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 38%,transparent)!important;
        opacity:1!important;
        filter:none!important;
      }

      html[data-mf44-on="1"] #assignment_group_upcoming_assignments a {
        color:var(--mf-accent)!important;
        -webkit-text-fill-color:var(--mf-accent)!important;
      }

      /* Assignment-group weight tables on the right side.
         Do not allow generic table rules to produce a flat gray block. */
      html[data-mf44-on="1"] #right-side-wrapper :is(
        table,thead,tbody,tfoot,tr,th,td
      ),
      html[data-mf44-on="1"] #right-side :is(
        table,thead,tbody,tfoot,tr,th,td
      ) {
        background:var(--mf-panel)!important;
        background-color:var(--mf-panel)!important;
        color:var(--mf-text)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 38%,transparent)!important;
        opacity:1!important;
        filter:none!important;
      }

      html[data-mf44-on="1"] #right-side-wrapper :is(table,thead,tbody,tfoot,tr,th,td) *,
      html[data-mf44-on="1"] #right-side :is(table,thead,tbody,tfoot,tr,th,td) * {
        opacity:1!important;
      }

      html[data-mf44-on="1"] #right-side-wrapper table a,
      html[data-mf44-on="1"] #right-side table a {
        color:var(--mf-accent)!important;
        -webkit-text-fill-color:var(--mf-accent)!important;
      }
    `;
    (document.head||document.documentElement).appendChild(st);
  }

  browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
  browser.storage.onChanged.addListener((c,a)=>{
    if(a==="local"&&c[KEY]) apply({enabled:true,...(c[KEY].newValue||{})});
  });
  browser.runtime.onMessage.addListener(msg=>{
    if(msg?.type==="MF44_SET") apply(msg.settings||{enabled:true});
  });
})();


/* ============================================================
   V53 — CANVAS GLOBAL NAV + BREADCRUMB FIX
   Prevents selected/hover/focus nav states from becoming gray/white.
   Also themes Canvas breadcrumbs while leaving course artwork/media alone.
   ============================================================ */
(() => {
  if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
  const KEY=`mf44:${location.hostname}`;
  const ID="mf53-canvas-nav";
  const remove=()=>document.getElementById(ID)?.remove();

  function apply(s){
    remove();
    if(s?.enabled===false) return;
    const st=document.createElement("style");
    st.id=ID;
    st.textContent=`
      /* ---------- GLOBAL NAV ---------- */
      html[data-mf44-on="1"] #application,
      html[data-mf44-on="1"] #wrapper,
      html[data-mf44-on="1"] #main,
      html[data-mf44-on="1"] #not_right_side,
      html[data-mf44-on="1"] .ic-app,
      html[data-mf44-on="1"] .ic-app-main-content {
        background-color:var(--mf-bg)!important;
      }

      html[data-mf44-on="1"] #global_nav,
      html[data-mf44-on="1"] #menu,
      html[data-mf44-on="1"] .ic-app-header,
      html[data-mf44-on="1"] .ic-app-header__main-navigation,
      html[data-mf44-on="1"] .ic-app-header__menu-list,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item {
        background:var(--mf-bg)!important;
        background-color:var(--mf-bg)!important;
        color:var(--mf-text)!important;
      }

      html[data-mf44-on="1"] .ic-app-header__menu-list-item > a,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item > button,
      html[data-mf44-on="1"] .ic-app-header__menu-list-link {
        background:transparent!important;
        background-color:transparent!important;
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
        box-shadow:none!important;
        filter:none!important;
        opacity:1!important;
      }

      /* Canvas uses active/selected/hover/focus states that can create the
         large light rectangle seen in the left navigation. */
      html[data-mf44-on="1"] .ic-app-header__menu-list-item:hover,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item:focus,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item:focus-within,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item.ic-app-header__menu-list-item--active,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item[aria-current="page"],
      html[data-mf44-on="1"] .ic-app-header__menu-list-item > a:hover,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item > a:focus,
      html[data-mf44-on="1"] .ic-app-header__menu-list-item > a:active,
      html[data-mf44-on="1"] .ic-app-header__menu-list-link:hover,
      html[data-mf44-on="1"] .ic-app-header__menu-list-link:focus,
      html[data-mf44-on="1"] .ic-app-header__menu-list-link:active,
      html[data-mf44-on="1"] .ic-app-header__menu-list-link.ic-app-header__menu-list-link--active {
        background:var(--mf-raised)!important;
        background-color:var(--mf-raised)!important;
        color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
        box-shadow:inset 3px 0 0 var(--mf-accent)!important;
        filter:none!important;
        opacity:1!important;
      }

      /* Course-level left navigation */
      html[data-mf44-on="1"] #section-tabs,
      html[data-mf44-on="1"] #section-tabs li,
      html[data-mf44-on="1"] #section-tabs li a {
        background:transparent!important;
        background-color:transparent!important;
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
        opacity:1!important;
      }
      html[data-mf44-on="1"] #section-tabs li a:hover,
      html[data-mf44-on="1"] #section-tabs li a:focus,
      html[data-mf44-on="1"] #section-tabs li a.active,
      html[data-mf44-on="1"] #section-tabs li a[aria-current="page"] {
        background:var(--mf-raised)!important;
        background-color:var(--mf-raised)!important;
        color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
      }

      /* ---------- CANVAS UI ICONS ----------
         Recolor icon-font / inline UI SVGs, but NOT course images, card artwork,
         video, canvas drawings, or image-role content. */
      html[data-mf44-on="1"] :is(
        .ic-app-header,
        #section-tabs,
        .ic-app-nav-toggle-and-crumbs,
        .ic-app-crumbs
      ) i[class*="icon-"] {
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
        opacity:1!important;
      }

      html[data-mf44-on="1"] :is(
        .ic-app-header,
        #section-tabs,
        .ic-app-nav-toggle-and-crumbs,
        .ic-app-crumbs
      ) svg:not([role="img"]) path {
        fill:currentColor!important;
      }

      /* ---------- BREADCRUMBS ----------
         Exact structure supplied:
         <ol><li class="home">...<li id="crumb_course_...">...
         <li aria-current="page">... */
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs,
      html[data-mf44-on="1"] .ic-app-crumbs,
      html[data-mf44-on="1"] .ic-app-crumbs ol,
      html[data-mf44-on="1"] .ic-app-crumbs ol > li,
      html[data-mf44-on="1"] .ic-app-crumbs ol > li > a,
      html[data-mf44-on="1"] .ic-app-crumbs ol > li > span {
        background:transparent!important;
        background-color:transparent!important;
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
        filter:none!important;
        opacity:1!important;
      }

      html[data-mf44-on="1"] .ic-app-crumbs ol > li.home a,
      html[data-mf44-on="1"] .ic-app-crumbs ol > li[id^="crumb_course_"] a {
        color:var(--mf-accent)!important;
        -webkit-text-fill-color:var(--mf-accent)!important;
      }

      html[data-mf44-on="1"] .ic-app-crumbs ol > li[aria-current="page"],
      html[data-mf44-on="1"] .ic-app-crumbs ol > li[aria-current="page"] .ellipsible {
        color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
      }

      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs {
        border-color:color-mix(in srgb,var(--mf-muted) 25%,transparent)!important;
      }

      /* Never let the universal v50 catcher override these Canvas nav pieces. */
      html[data-mf44-on="1"] :is(
        #global_nav,#menu,.ic-app-header,.ic-app-header__main-navigation,
        .ic-app-header__menu-list,.ic-app-header__menu-list-item,
        #section-tabs,.ic-app-nav-toggle-and-crumbs,.ic-app-crumbs
      )[data-mf50-container="1"],
      html[data-mf44-on="1"] :is(
        #global_nav,#menu,.ic-app-header,.ic-app-header__main-navigation,
        .ic-app-header__menu-list,.ic-app-header__menu-list-item,
        #section-tabs,.ic-app-nav-toggle-and-crumbs,.ic-app-crumbs
      )[data-mf50-bright="1"] {
        background-color:var(--mf-bg)!important;
      }
    `;
    (document.head||document.documentElement).appendChild(st);

    /* Remove stale universal marks from nav/breadcrumb nodes that may have been
       marked before this v53 style loaded. */
    document.querySelectorAll(
      '#global_nav,#menu,.ic-app-header,.ic-app-header__main-navigation,'+
      '.ic-app-header__menu-list,.ic-app-header__menu-list-item,#section-tabs,'+
      '.ic-app-nav-toggle-and-crumbs,.ic-app-crumbs'
    ).forEach(el=>{
      el.removeAttribute("data-mf50-container");
      el.removeAttribute("data-mf50-bright");
    });
  }

  browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
  browser.storage.onChanged.addListener((c,a)=>{
    if(a==="local"&&c[KEY]) apply({enabled:true,...(c[KEY].newValue||{})});
  });
  browser.runtime.onMessage.addListener(msg=>{
    if(msg?.type==="MF44_SET") apply(msg.settings||{enabled:true});
  });
})();


/* ============================================================
   V54 — CANVAS TOP BREADCRUMB / IMMERSIVE READER FIX
   Fixes the remaining light-gray strip around the course crumb
   and the bright Immersive Reader control.
   ============================================================ */
(() => {
  if(!/(^|\.)instructure\.com$/i.test(location.hostname)) return;
  const KEY=`mf44:${location.hostname}`;
  const ID="mf54-canvas-topbar";
  const remove=()=>document.getElementById(ID)?.remove();

  function apply(s){
    remove();
    if(s?.enabled===false) return;
    const st=document.createElement("style");
    st.id=ID;
    st.textContent=`
      /* Top Canvas navigation / crumb shell */
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs,
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs__navigation,
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs__button,
      html[data-mf44-on="1"] .ic-app-crumbs,
      html[data-mf44-on="1"] .ic-app-crumbs ol {
        background:var(--mf-bg)!important;
        background-color:var(--mf-bg)!important;
        color:var(--mf-text)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 30%,transparent)!important;
        box-shadow:none!important;
        filter:none!important;
        opacity:1!important;
      }

      /* The long gray course breadcrumb itself */
      html[data-mf44-on="1"] .ic-app-crumbs ol > li,
      html[data-mf44-on="1"] .ic-app-crumbs ol > li > a,
      html[data-mf44-on="1"] .ic-app-crumbs ol > li > span,
      html[data-mf44-on="1"] .ic-app-crumbs .ellipsible,
      html[data-mf44-on="1"] .ic-app-crumbs [id^="crumb_course_"] {
        background:transparent!important;
        background-color:transparent!important;
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
        box-shadow:none!important;
        filter:none!important;
        opacity:1!important;
      }

      html[data-mf44-on="1"] .ic-app-crumbs [id^="crumb_course_"] > a,
      html[data-mf44-on="1"] .ic-app-crumbs [id^="crumb_course_"] .ellipsible {
        color:var(--mf-accent)!important;
        -webkit-text-fill-color:var(--mf-accent)!important;
      }

      /* Some Canvas/InstUI builds put a generated background on the crumb
         flex wrapper rather than the ol/li itself. */
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs :is(
        [class*="Breadcrumb"],
        [class*="breadcrumb"],
        [class*="Flex"],
        [class*="View"]
      ) {
        background-color:transparent!important;
      }

      /* Menu/hamburger button */
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs button:not([data-mf54-keep]) {
        background:var(--mf-raised)!important;
        background-color:var(--mf-raised)!important;
        color:var(--mf-muted)!important;
        -webkit-text-fill-color:var(--mf-muted)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 35%,transparent)!important;
        box-shadow:none!important;
      }

      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs button:not([data-mf54-keep]):hover,
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs button:not([data-mf54-keep]):focus {
        background:var(--mf-panel)!important;
        background-color:var(--mf-panel)!important;
        color:var(--mf-text)!important;
      }

      /* Immersive Reader — Canvas has used both class/test-id and accessible
         text wrappers across versions, so cover its common InstUI containers. */
      html[data-mf44-on="1"] :is(
        [data-testid*="immersive-reader" i],
        [class*="immersive-reader" i],
        [class*="ImmersiveReader" i],
        [aria-label*="Immersive Reader" i],
        [title*="Immersive Reader" i]
      ),
      html[data-mf44-on="1"] :is(
        [data-testid*="immersive-reader" i],
        [class*="immersive-reader" i],
        [class*="ImmersiveReader" i],
        [aria-label*="Immersive Reader" i],
        [title*="Immersive Reader" i]
      ) button {
        background:var(--mf-raised)!important;
        background-color:var(--mf-raised)!important;
        color:var(--mf-text)!important;
        -webkit-text-fill-color:var(--mf-text)!important;
        border-color:color-mix(in srgb,var(--mf-muted) 35%,transparent)!important;
        box-shadow:none!important;
        filter:none!important;
        opacity:1!important;
      }

      /* Do not let v50's universal marks turn the top bar light again. */
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs [data-mf50-container="1"],
      html[data-mf44-on="1"] .ic-app-nav-toggle-and-crumbs [data-mf50-bright="1"],
      html[data-mf44-on="1"] .ic-app-crumbs[data-mf50-container="1"],
      html[data-mf44-on="1"] .ic-app-crumbs[data-mf50-bright="1"] {
        background:transparent!important;
        background-color:transparent!important;
      }
    `;
    (document.head||document.documentElement).appendChild(st);

    document.querySelectorAll(
      '.ic-app-nav-toggle-and-crumbs,.ic-app-nav-toggle-and-crumbs *,.ic-app-crumbs,.ic-app-crumbs *'
    ).forEach(el=>{
      el.removeAttribute("data-mf50-container");
      el.removeAttribute("data-mf50-bright");
    });
  }

  browser.storage.local.get(KEY).then(d=>apply({enabled:true,...(d[KEY]||{})}));
  browser.storage.onChanged.addListener((c,a)=>{
    if(a==="local"&&c[KEY]) apply({enabled:true,...(c[KEY].newValue||{})});
  });
  browser.runtime.onMessage.addListener(msg=>{
    if(msg?.type==="MF44_SET") apply(msg.settings||{enabled:true});
  });
})();
