/* SPDX-License-Identifier: MIT */
// Labeled measurements around Home Assistant's native tile controls.
class CamperInetCard extends HTMLElement {
  constructor() { super(); this.attachShadow({mode: 'open'}); this._revision = 0; }
  setConfig(config) {
    if (!config.entity || !['climate', 'water'].includes(config.kind)) throw new Error('entity und kind sind erforderlich');
    this._config = config;
    this._revision++;
    this.shadowRoot.innerHTML = `<style>
      :host {display:block} ha-card {overflow:hidden}
      .native {--ha-card-border-width:0;--ha-card-box-shadow:none;--ha-card-background:transparent;--ha-card-border-radius:0px}
      .readings {display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 16px 16px}
      .reading {min-width:0;padding:12px;border-radius:12px;background:var(--secondary-background-color)}
      .label,.note {color:var(--secondary-text-color);font-size:12px;line-height:1.5}
      .value {font-size:24px;font-weight:600;line-height:1.4;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
      .error {padding:12px 16px;color:var(--error-color)}
    </style><ha-card><div class="native"></div><div class="readings">
      <div class="reading"><div class="label" id="label-a"></div><div class="value" id="value-a"></div><div class="note" id="note-a"></div></div>
      <div class="reading"><div class="label" id="label-b"></div><div class="value" id="value-b"></div><div class="note" id="note-b"></div></div>
    </div></ha-card>`;
    this._tile = undefined;
    this._createTile(this._revision);
    this._render();
  }
  async _createTile(revision) {
    try {
      const helpers = await window.loadCardHelpers();
      if (revision !== this._revision) return;
      const c = this._config;
      this._tile = helpers.createCardElement({type:'tile', entity:c.entity,
        name:c.name || (c.kind === 'climate' ? 'Raumheizung' : 'Warmwasser einstellen'),
        hide_state:true, features_position:'bottom',
        features:c.kind === 'climate' ? [
          {type:'target-temperature'}, {type:'climate-hvac-modes',hvac_modes:['heat','off']},
          {type:'climate-fan-modes',style:'dropdown'}
        ] : [{type:'select-options'}]});
      if (this._hass) this._tile.hass = this._hass;
      this.shadowRoot.querySelector('.native').replaceChildren(this._tile);
    } catch (error) {
      if (revision !== this._revision) return;
      const note = document.createElement('div'); note.className='error';
      note.textContent='Bedienelemente konnten nicht geladen werden. Bitte das Dashboard neu laden.';
      this.shadowRoot.querySelector('.native').replaceChildren(note);
    }
  }
  set hass(hass) { this._hass=hass; if(this._tile) this._tile.hass=hass; this._render(); }
  _render() {
    if (!this._config || !this._hass) return;
    const c=this._config, state=this._hass.states[c.entity];
    const available = state && !['unavailable','unknown'].includes(state.state);
    const measured=this._hass.states[c.temperature_entity];
    const format=(v,unit='°C') => v !== null && v !== undefined && v !== '' && Number.isFinite(Number(v))
      ? new Intl.NumberFormat(this._hass.locale?.language || 'de-DE',{maximumFractionDigits:1}).format(Number(v))+' '+unit : '—';
    const set=(id,value)=>{this.shadowRoot.getElementById(id).textContent=value;};
    set('label-a',c.kind==='climate'?'Im Raum':'Wassertemperatur');
    set('value-a',format(available && measured ? measured.state : null, measured?.attributes.unit_of_measurement || '°C'));
    set('note-a',available && measured && !['unavailable','unknown'].includes(measured.state)?'Gemessen':'Nicht verfügbar');
    if(c.kind==='climate') {
      set('label-b','Zieltemperatur'); set('value-b',format(available?state.attributes.temperature:null,this._hass.config?.unit_system?.temperature || '°C'));
      set('note-b',!available?'Nicht verfügbar':state.state==='off'?'Vorgemerkt · Heizung aus':'Bestätigt');
    } else {
      set('label-b','Warmwasserstufe'); set('value-b',available?state.state:'—');
      set('note-b',available?'Bestätigt':'Nicht verfügbar');
    }
  }
  getCardSize() { return this._config?.kind==='climate'?5:3; }
  getGridOptions() { return {columns:12,min_columns:6,min_rows:3}; }
}
if (!customElements.get('camper-inet-card')) customElements.define('camper-inet-card',CamperInetCard);
window.customCards=window.customCards||[];
window.customCards.push({type:'camper-inet-card',name:'Camper Heater Bridge',description:'Truma-Steuerung mit beschrifteten Messwerten'});
