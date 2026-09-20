import type {State} from '../types';
const glyph:Record<State,string>={NORMAL:'●',WARN:'▲',RESTRICT:'▼',UNKNOWN:'?',STOP:'■'};
export function StateBadge({state}:{state:State}){return <span className={`state-badge state-${state.toLowerCase()}`} aria-label={`Safety state ${state}`}><b aria-hidden="true">{glyph[state]}</b>{state}</span>}
