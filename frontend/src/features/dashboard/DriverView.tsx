import type {Snapshot,State} from '../../types';
import {StateBadge} from '../../components/StateBadge';
import {Icon} from '../flagship/Icons';

const instruction:Record<State,{title:string;detail:string}>={
  NORMAL:{title:'Observe the surroundings.',detail:'The research state is normal. This is not permission to move.'},
  WARN:{title:'Pay attention.',detail:'A warning needs your attention. Review the reason below.'},
  RESTRICT:{title:'Movement is restricted.',detail:'The local decision engine has reported a restriction.'},
  UNKNOWN:{title:'Guidance is unavailable.',detail:'The system does not have enough reliable information. Do not treat this as a clear path.'},
  STOP:{title:'Stop and assess.',detail:'The local decision engine has reported a stop. The browser cannot apply a brake.'},
};
const readable=(text:string)=>text.replaceAll('_',' ').toLowerCase().replace(/^./,letter=>letter.toUpperCase());

export function DriverView({snapshot}:{snapshot:Snapshot}){
  const decision=snapshot.decision;
  const message=instruction[decision.state]??instruction.UNKNOWN;
  return <div className="driver-workspace">
    <section className={`driver-advisory driver-advisory-${decision.state.toLowerCase()}`} aria-label="Current driver advisory">
      <div className="driver-advisory-heading"><span className="eyebrow-r2">LOCAL RESEARCH DECISION</span><StateBadge state={decision.state}/></div>
      <div className="driver-advisory-message"><span className="driver-advisory-symbol"><Icon name="safety" size={42}/></span><div><h2>{message.title}</h2><p>{message.detail}</p></div></div>
      <div className="driver-reason"><span>Why</span><strong>{readable(decision.reason_code)}</strong><small>{decision.reason_code}</small></div>
      <p className="driver-no-authority">Keep traction disabled. This is a monitoring display, not a driving command.</p>
    </section>
    <div className="driver-value-grid">
      <article className="r2-card"><span className="eyebrow-r2">OBSERVATION</span><dl><dt>Measured speed</dt><dd>UNAVAILABLE</dd></dl><p>No ground-speed measurement is supplied by this contract.</p></article>
      <article className="r2-card"><span className="eyebrow-r2">RESEARCH LIMIT</span><dl><dt>Commanded permitted speed</dt><dd>{Number.isFinite(decision.permitted_speed_mps)?decision.permitted_speed_mps.toFixed(2):'UNAVAILABLE'}<small> m/s</small></dd></dl><p>Parameterized output. Not a validated safe driving speed.</p></article>
      <article className="r2-card"><span className="eyebrow-r2">COLLISION EVIDENCE</span><dl><dt>TTC</dt><dd>NOT COMPUTED</dd></dl><p>The display never invents a time-to-collision value.</p></article>
    </div>
    <section className="r2-card driver-observations"><div className="card-heading"><h2><Icon name="sensors"/> Observation sources</h2><span className="small-badge">{snapshot.mode}</span></div>
      <div className="driver-source-grid">{['radar','camera','thermal','imu'].map(id=>{const sensor=snapshot.sensors.find(item=>item.device_id===id||(id==='radar'&&item.device_id==='ld2450'));return <div key={id}><span>{id==='camera'?'RGB camera':id==='imu'?'IMU':readable(id)}</span><strong>{readable(sensor?.state??'NOT_CONNECTED')}</strong><small>{sensor?.source_mode??'SOURCE UNAVAILABLE'}</small></div>;})}</div>
      <p className="subtle">{snapshot.tracks.length} local radar targets. Targets are not geographic route guidance. Use the Sensors workspace for detailed evidence.</p>
    </section>
    <div className="driver-communication"><Icon name="connection"/><span>Command sequence <b>{snapshot.command.sequence}</b> · heartbeat <b>{snapshot.command.heartbeat}</b></span><span>Traction <b>DISABLED_PHASE_1</b></span></div>
  </div>;
}
