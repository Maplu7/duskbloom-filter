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
    pink_blackout:{bg:'#21151b',panel:'#35242d',raised:'#4a3340',text:'#fff8fc',muted:'#d8bdcb',accent:'#d67e9c'},
    pink:{bg:'#261820',panel:'#3a2731',raised:'#513644',text:'#fff8fc',muted:'#e5c5d5',accent:'#eb9ab8'},
    dark_pink:{bg:'#1d1118',panel:'#301d28',raised:'#432937',text:'#fff8fc',muted:'#d8b8c8',accent:'#9b4b6c'},
    rose_dim:{bg:'#21171a',panel:'#35252b',raised:'#4a343c',text:'#fffaf8',muted:'#d8c0c3',accent:'#be7087'},
    lavender:{bg:'#191520',panel:'#2a2435',raised:'#3c334a',text:'#fbf8ff',muted:'#d0c5df',accent:'#8f74a6'},
    amber:{bg:'#21190f',panel:'#352a18',raised:'#4a3a21',text:'#fffaf0',muted:'#dfcfaa',accent:'#d69949'},
    forest_green:{bg:'#111a14',panel:'#1e2c22',raised:'#2c4032',text:'#f7fcf8',muted:'#bfd3c5',accent:'#46694c'},
    warm_white:{bg:'#2b2720',panel:'#3d372d',raised:'#51483b',text:'#fffaf1',muted:'#e1d5c2',accent:'#ffe0b4'},
    deep_red:{bg:'#1c0d11',panel:'#30171c',raised:'#48222a',text:'#fff8f8',muted:'#dcbfc3',accent:'#691c24'},
    blue_light:{bg:'#111a25',panel:'#1d2c3a',raised:'#2b4256',text:'#f7fbff',muted:'#bfd3e1',accent:'#4e6f94'},
    dark_dimmer:{bg:'#111113',panel:'#202024',raised:'#303036',text:'#f7f7fa',muted:'#c6c6cf',accent:'#141414'},
    midnight:{bg:'#0c0c14',panel:'#171522',raised:'#242135',text:'#f7faff',muted:'#becbe0',accent:'#0e0c16'},
    obsidian:{bg:'#09090d',panel:'#17171c',raised:'#25252c',text:'#f8f8fb',muted:'#c4bec7',accent:'#08080c'},
    dusty_rose:{bg:'#20161b',panel:'#33242b',raised:'#47323b',text:'#fff9fc',muted:'#d7c0ca',accent:'#a66c7e'},
    peach:{bg:'#251a16',panel:'#3a2a24',raised:'#503a31',text:'#fff9f5',muted:'#dfc8bc',accent:'#de9d7e'},
    sepia:{bg:'#1d1812',panel:'#30281d',raised:'#433829',text:'#fff9ef',muted:'#d7cbb8',accent:'#967956'},
    sage:{bg:'#151a15',panel:'#252d24',raised:'#354034',text:'#f8fcf8',muted:'#c5d2c3',accent:'#748b70'},
    soft_cyan:{bg:'#141b1c',panel:'#243032',raised:'#344447',text:'#f6fcfc',muted:'#c1d4d5',accent:'#709799'},
    mauve:{bg:'#1b151a',panel:'#2d242c',raised:'#40333e',text:'#fcf8fb',muted:'#d1c2cd',accent:'#82607d'},
    smoke:{bg:'#161719',panel:'#27292c',raised:'#383b3f',text:'#f8f9fa',muted:'#c7c9cc',accent:'#5c6067'},
    cocoa:{bg:'#181311',panel:'#2a211e',raised:'#3b2f2b',text:'#fff9f6',muted:'#d3c5bf',accent:'#4c3732'},
    navy:{bg:'#10131c',panel:'#1d2434',raised:'#2b354b',text:'#f7f9ff',muted:'#c0c8dc',accent:'#23304b'},
    burgundy:{bg:'#190f13',panel:'#2c1b22',raised:'#402730',text:'#fff8fa',muted:'#d4c0c7',accent:'#522230'}
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
