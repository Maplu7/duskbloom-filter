/* DuskBloom Web 2.0 — single low-memory theme engine. */
(() => {
  'use strict';
  const ext = globalThis.browser || globalThis.chrome;
  if (!ext?.storage?.local) return;

  const host = location.hostname;
  const KEY = `mf44:${host}`; // keep old settings compatible
  const STYLE_ID = 'duskbloom-web-theme';
  const ROOT_ATTR = 'data-duskbloom-web';
  const DEFAULTS = {
    enabled: true, preset: 'obsidian',
    customBg:'#171018', customPanel:'#241925', customRaised:'#332336',
    customText:'#ffffff', customMuted:'#cbb9c6', customAccent:'#e7a1c6'
  };
  const PRESETS = {
    pink_blackout:{bg:'#110b10',panel:'#21131d',raised:'#34202d',text:'#fff8fc',muted:'#d8bdcb',accent:'#ff8fc1'},
    pink:{bg:'#24141e',panel:'#35202d',raised:'#493043',text:'#fff8fc',muted:'#e5c5d5',accent:'#f4a2ca'},
    dark_pink:{bg:'#180e15',panel:'#291824',raised:'#3c2434',text:'#fff8fc',muted:'#d8b8c8',accent:'#e989b7'},
    rose_dim:{bg:'#211619',panel:'#342328',raised:'#493139',text:'#fffaf8',muted:'#d8c0c3',accent:'#df9bab'},
    lavender:{bg:'#171421',panel:'#28213a',raised:'#3a3051',text:'#fbf8ff',muted:'#d0c5df',accent:'#bc9ae7'},
    amber:{bg:'#211a0f',panel:'#352a17',raised:'#4a3a20',text:'#fffaf0',muted:'#dfcfaa',accent:'#e7b85f'},
    forest_green:{bg:'#101a14',panel:'#1c2b22',raised:'#2a4032',text:'#f7fcf8',muted:'#bfd3c5',accent:'#7fc49a'},
    warm_white:{bg:'#2b2721',panel:'#3d372e',raised:'#51483c',text:'#fffaf1',muted:'#e1d5c2',accent:'#e8c58d'},
    deep_red:{bg:'#1b0d10',panel:'#30161c',raised:'#48212a',text:'#fff8f8',muted:'#dcbfc3',accent:'#df7b89'},
    blue_light:{bg:'#101b26',panel:'#1b2d3c',raised:'#29445a',text:'#f7fbff',muted:'#bfd3e1',accent:'#7fc1e7'},
    dark_dimmer:{bg:'#151519',panel:'#25252b',raised:'#35353e',text:'#f7f7fa',muted:'#c6c6cf',accent:'#aaa8bd'},
    midnight:{bg:'#0c1422',panel:'#16243a',raised:'#223653',text:'#f7faff',muted:'#becbe0',accent:'#7da6df'},
    obsidian:{bg:'#101014',panel:'#1b1b21',raised:'#292932',text:'#f8f8fb',muted:'#c4bec7',accent:'#d3a5bf'}
  };

  let settings = {...DEFAULTS};
  let scheduled = false;

  function palette() {
    if (settings.preset === 'custom') return {
      bg:settings.customBg, panel:settings.customPanel, raised:settings.customRaised,
      text:settings.customText, muted:settings.customMuted, accent:settings.customAccent
    };
    return PRESETS[settings.preset] || PRESETS.obsidian;
  }

  function removeTheme() {
    document.getElementById(STYLE_ID)?.remove();
    document.documentElement?.removeAttribute(ROOT_ATTR);
  }

  function css(p) {
    const docs = host === 'docs.google.com';
    const canvas = /(^|\.)instructure\.com$/i.test(host);
    return `
:root[${ROOT_ATTR}="on"]{--db-bg:${p.bg};--db-panel:${p.panel};--db-raised:${p.raised};--db-text:${p.text};--db-muted:${p.muted};--db-accent:${p.accent};color-scheme:dark}
:root[${ROOT_ATTR}="on"],:root[${ROOT_ATTR}="on"] body{background:var(--db-bg)!important;color:var(--db-text)!important}
:root[${ROOT_ATTR}="on"] :where(main,article,section,aside,nav,header,footer,[role="main"],[role="dialog"],[role="menu"],[role="listbox"],.card,.panel,.modal,.popover,.dropdown-menu,.menu,.content,.container){border-color:color-mix(in srgb,var(--db-muted) 25%,transparent)}
:root[${ROOT_ATTR}="on"] :where(input:not([type="checkbox"]):not([type="radio"]),textarea,select,[contenteditable="true"]){background:var(--db-raised)!important;color:var(--db-text)!important;-webkit-text-fill-color:var(--db-text)!important;border-color:var(--db-muted)!important}
:root[${ROOT_ATTR}="on"] :where(a){color:var(--db-accent)!important}
:root[${ROOT_ATTR}="on"] :where(img,picture,video,svg,canvas,[role="img"]){opacity:1!important;mix-blend-mode:normal!important}
${canvas ? `
:root[${ROOT_ATTR}="on"] :where(#wrapper,#main,#content-wrapper,#content,.ic-Layout-contentWrapper,.ic-Layout-contentMain,.ic-app-nav-toggle-and-crumbs,.ic-app-crumbs,.ic-app-crumbs ol){background:var(--db-bg)!important;color:var(--db-text)!important}
:root[${ROOT_ATTR}="on"] :where(.header-bar,.page-toolbar,.form-actions,.item-group-container,.context_module,.context_module_item,.ig-list,.ig-row,.ui-dialog,.ui-dialog-content,.ui-widget-content,.popover,.panel,.well,.list-group,.ic-DashboardCard__content,.ic-DashboardCard__assignments,.ic-DashboardCard__assignment,.ic-DashboardCard__body,.ic-DashboardCard__footer){background:var(--db-panel)!important;color:var(--db-text)!important}
:root[${ROOT_ATTR}="on"] :where(.ic-DashboardCard__action-container,button,.btn,.Button){background:var(--db-raised)!important;color:var(--db-text)!important;-webkit-text-fill-color:var(--db-text)!important}
:root[${ROOT_ATTR}="on"] .ic-app-header{background:#111116!important}
:root[${ROOT_ATTR}="on"] .ic-app-header :where(.ic-app-header__menu-list-link,.menu-item__text,.ic-icon-svg){color:#fff!important;-webkit-text-fill-color:#fff!important}
:root[${ROOT_ATTR}="on"] :where(.ic-DashboardCard__header,.ic-DashboardCard__header_hero,.ic-DashboardCard__header_image,[style*="background-image"]){filter:none!important;opacity:1!important;visibility:visible!important}
` : ''}
${docs ? `
:root[${ROOT_ATTR}="on"] :where(#docs-chrome,#docs-header,#docs-bars,.docs-material,.docs-menubar,.docs-toolbar-wrapper,.docs-primary-toolbars,.goog-toolbar){background:var(--db-panel)!important;color:var(--db-text)!important}
:root[${ROOT_ATTR}="on"] :where(.docs-title-input,.docs-title-input-label){background:var(--db-panel)!important;color:var(--db-text)!important;-webkit-text-fill-color:var(--db-text)!important}
:root[${ROOT_ATTR}="on"] :where(.kix-appview-editor,.kix-appview-editor-container,.kix-editor){background:var(--db-bg)!important}
:root[${ROOT_ATTR}="on"] :where(.kix-page,.kix-page-content-wrapper,.kix-page-content){background:var(--db-panel)!important;box-shadow:0 0 0 1px var(--db-raised),0 10px 30px rgba(0,0,0,.25)!important}
:root[${ROOT_ATTR}="on"] :where(.kix-lineview-text-block,.kix-lineview-text-block *,.kix-lineview-content,.kix-lineview-content *){color:var(--db-text)!important;-webkit-text-fill-color:var(--db-text)!important}
` : ''}
`;
  }

  function apply() {
    scheduled = false;
    removeTheme();
    if (settings.enabled === false || !document.documentElement) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = css(palette());
    (document.head || document.documentElement).appendChild(style);
    document.documentElement.setAttribute(ROOT_ATTR, 'on');
  }

  function scheduleApply() {
    if (scheduled) return;
    scheduled = true;
    queueMicrotask(apply);
  }

  Promise.resolve(ext.storage.local.get(KEY)).then(data => {
    settings = {...DEFAULTS, ...(data?.[KEY] || {})};
    scheduleApply();
  });

  ext.storage.onChanged.addListener((changes, area) => {
    if (area !== 'local' || !changes[KEY]) return;
    settings = {...DEFAULTS, ...(changes[KEY].newValue || {})};
    scheduleApply();
  });

  ext.runtime?.onMessage?.addListener(msg => {
    if (msg?.type !== 'MF44_SET') return;
    settings = {...DEFAULTS, ...(msg.settings || {})};
    scheduleApply();
  });
})();
