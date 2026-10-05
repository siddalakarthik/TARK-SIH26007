"""Three deterministic SIH presentations through the existing R3 production path.

Only synthetic observations are generated. Decisions are never prescribed.
RecordingStore persists them; isolated production replay verifies the reload.
No live runtime, transport, device or motion command is constructed here.
"""
from copy import deepcopy
import json
from pathlib import Path
from xml.sax.saxutils import escape

from app.replay.store import RecordingStore
from app.r3.reasoning_fixtures import ReasoningFixture
from app.r3.reasoning import observability, purpose_observations
from app.r3.reasoning_models import Environment
from app.r3.replay import recompute_advisory, recompute_evidence
from app.r3.runtime import r3_software_fingerprint

DEMOS = {
    'degraded-visibility': ('TARK-DEMO-01-DEGRADED-VISIBILITY',
        'Trustworthy evidence, not fog alone, limits operating capability.'),
    'collision-risk': ('TARK-DEMO-02-COLLISION-RISK',
        'Qualified target geometry becomes an auditable safety advisory.'),
    'blind-curve': ('TARK-DEMO-03-BLIND-CURVE',
        'Equipped-peer position is cooperative evidence, not local sensing.'),
}


def _stages(scenario):
    fog = Environment(visibility='SEVERE', provenance='CONFIGURED_RESEARCH',
                      evidence_reference='SYNTHETIC_FOG_NOT_FIELD_TRIAL')
    if scenario == 'degraded-visibility':
        return [('A_HEALTHY', [{}] * 10, 'NORMAL'),
                ('B_RGB_FOG', [{'environment': fog}] * 5, 'RESTRICT'),
                ('C_GEOMETRY_LOSS', [{'omit': ('radar-a', 'rgb-a'), 'environment': fog}] * 15, 'UNKNOWN'),
                ('D_SUSTAINED_RECOVERY', [{}] * 15, 'NORMAL')]
    if scenario == 'collision-risk':
        # Independent Cartesian positions, not Doppler-derived velocity.
        # Zero radial field intentionally differs from the inferred -1 m/s vx.
        approach = [{'points': [(4. - i * .1, max(0., 2. - i * .2), 0.)]}
                    for i in range(32)]
        return [('BASELINE', [{}] * 10, 'NORMAL'),
                ('A_TRACK_OUTSIDE', approach[:2], 'UNKNOWN'),
                ('B_ENTER_CORRIDOR', approach[2:11], 'RESTRICT'),
                ('C_CONDITIONAL_TTC', approach[11:21], 'RESTRICT'),
                ('D_STOPPING_LIMIT', approach[21:], 'STOP')]
    if scenario == 'blind-curve':
        return [('A_NO_CONFLICT', [{}] * 10, 'NORMAL'),
                ('B_FRESH_PEER_CONFLICT', [{'peer': True}] * 5, 'RESTRICT'),
                ('C_PEER_EXPIRES', [{'omit': ('gnss-b',)}] * 15, 'UNKNOWN')]
    raise ValueError('unknown SIH scenario')


def _row(fixture, stage, decision):
    # Display per-source contributions through the same production coverage
    # function, not a second range calculation. These are not extra decisions.
    _, usable, _ = purpose_observations(fixture.channel, fixture.now, fixture.config)
    environment = Environment.model_validate(decision['observability']['environment'])
    contributions = {model.source_id: observability(
        {model.source_id: usable[model.source_id]} if model.source_id in usable else {},
        fixture.config, environment).model_dump(mode='json') for model in fixture.config.coverage}
    return {
        'stage': stage, 'timestamp_ns': fixture.now, 'sequence': fixture.sequence,
        'source_mode': decision['source_mode'], 'state': decision['state'],
        'advised_speed_mps': decision['advised_speed_mps'],
        'required_range_m': decision['stopping_requirement_m'],
        'qualified_range_m': decision['observability']['forward_range_m'],
        'environment': decision['observability']['environment'],
        'observability': decision['observability'],
        'source_coverage_contributions': contributions,
        'contributions': [{'source_id': s['source_id'], 'evidence_id': s['evidence_id'],
                           'purposes': s['purposes'], 'exclusion': s['exclusion_reason']}
                          for s in decision['semantic_observations']],
        'excluded_sources': decision['excluded_sources'],
        'tracks': decision['tracks'], 'ttc': decision['ttc'],
        'cooperative_context': decision['cooperative_context'],
        'hazards': decision['hazards'], 'why': decision['explanation'],
        'reason': decision['limiting_reason'],
        'traction': decision['traction'], 'motion_authority': decision['motion_authority'],
        'hardware_verified': decision['hardware_verified'],
    }


def run_demo(scenario, output: Path):
    """Record, close/reopen, recompute, and export one bounded demo.

    UUID session IDs and measured replay timings are store metadata; normalized
    decisions and their evidence sequence are deterministic. Existing outputs
    are never overwritten, including on a failed assertion/recomputation.
    """
    stages = _stages(scenario)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    fingerprint = r3_software_fingerprint()
    fixture = ReasoningFixture(software=fingerprint)
    provenance = fixture.metadata()  # checkpoint BEFORE the first recorded tick
    demo_id, message = DEMOS[scenario]
    rows, endpoints = [], []
    store = RecordingStore(output / 'recording.db')
    try:
        session = store.start(timestamp_ns=fixture.now, source_mode='SIMULATION',
            configuration_hash=fixture.bundle.content_hash, max_records=100,
            metadata={'r3': provenance, 'demo_id': demo_id, 'mode': 'SIMULATION'})
        for stage, inputs, expected in stages:
            for kwargs in inputs:
                decision = fixture.feed(**kwargs)
                if (decision['source_mode'] != 'SIMULATION' or decision['motion_authority']
                    or decision['hardware_verified'] or decision['traction'] != 'DISABLED_PHASE_1'):
                    raise AssertionError('demo claim/authority boundary violated')
                payload = fixture.record(decision, kwargs.get('environment'))['payload']
                payload['schema_version'] = 2
                if not store.append_observation_tick(timestamp_ns=fixture.now,
                    source_mode='SIMULATION', payload=payload):
                    raise AssertionError('bounded recorder refused demo tick')
                rows.append(_row(fixture, stage, decision))
            endpoints.append({'stage': stage, 'expected': expected, 'observed': decision['state'],
                              'sequence': fixture.sequence, 'reason': decision['limiting_reason']})
        store.stop(timestamp_ns=fixture.now)
    finally:
        store.close()
    # Replay consumes persisted evidence, not the original in-memory records.
    before = deepcopy(fixture.channel.record())
    checkpoint = fixture.engine.checkpoint()
    store = RecordingStore(output / 'recording.db')
    try:
        session = store.get(session['session_id'])
        saved = session['metadata']['r3']
        records = list(store.iter_records(session['session_id']))
        advisory = recompute_advisory(iter(records), saved, fingerprint)
        qualification = recompute_evidence(iter(records), saved, fingerprint)
    finally:
        store.close()
    isolated = before == fixture.channel.record() and checkpoint == fixture.engine.checkpoint()
    passed = (all(s['expected'] == s['observed'] for s in endpoints) and isolated
              and advisory['result'] == qualification['result'] == 'MATCH'
              and advisory['verified_ticks'] == len(rows))
    metadata = {'demo_id': demo_id, 'mode': 'SIMULATION', 'origin': 'SYNTHETIC_EVIDENCE',
                'software_fingerprint': fingerprint, 'r3': saved,
                'source_provenance': [i.model_dump(mode='json') for i in fixture.identities.values()],
                'stages': endpoints, 'start_stage': endpoints[0]['stage'], 'end_stage': endpoints[-1]['stage'],
                'replay': advisory, 'qualification_replay': qualification,
                'hardware_verified': False, 'traction': 'DISABLED_PHASE_1'}
    summary = {'demo_id': demo_id, 'message': message, 'mode': 'SIMULATION',
               'synthetic_assumptions': 'Research coverage, transforms, clocks, wheel scale/slip, fixed axes, braking and conflict zone; NOT physical validation.',
               'passed': passed, 'replay_isolated': isolated, 'ticks': len(rows),
               'stages': endpoints, 'rows': rows, 'replay': advisory, 'qualification_replay': qualification,
               'raw_media_replay': 'NOT RECOMPUTABLE — synthetic normalized evidence only; no raw image inference'}
    for name, value in [('metadata.json', metadata), ('summary.json', summary), ('records.json', records)]:
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    (output / 'presentation.svg').write_text(_presentation(summary), encoding='utf-8')
    return summary


def _presentation(summary):
    """Static evidence card, not another dashboard; values from recorded decisions."""
    endpoints = [next(r for r in summary['rows'] if r['sequence'] == s['sequence'])
                 for s in summary['stages']]
    height = 280 + len(endpoints) * 104
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="{height}" viewBox="0 0 1480 {height}">',
             '<rect width="100%" height="100%" fill="#101b25"/>',
             '<g font-family="Arial,sans-serif" fill="#edf3f8">',
             '<text x="40" y="45" font-size="21" fill="#f1c56b">SIMULATION / SYNTHETIC EVIDENCE — NO PHYSICAL VALIDATION</text>',
             f'<text x="40" y="94" font-size="32">{escape(summary["demo_id"])}</text>',
             f'<text x="40" y="134" font-size="23">{escape(summary["message"])}</text>']
    for x, label in [(40,'STAGE'),(380,'R3 STATE'),(560,'CAP m/s'),(735,'RANGE m'),(905,'REQUIRED m'),(1090,'REASON')]:
        parts.append(f'<text x="{x}" y="188" font-size="18" fill="#9eb4c6">{label}</text>')
    colors = {'NORMAL':'#98ddb0','RESTRICT':'#f1c56b','UNKNOWN':'#c8cbd2','STOP':'#ffa0a0','WARN':'#f1c56b'}
    def number(value): return 'UNAVAILABLE' if value is None else f'{value:.3f}'
    for index, row in enumerate(endpoints):
        y = 230 + index * 104
        values = [(40,row['stage'].replace('_',' ')),(380,row['state']),
                  (560,number(row['advised_speed_mps'])),(735,number(row['qualified_range_m'])),
                  (905,number(row['required_range_m']))]
        for x, value in values:
            parts.append(f'<text x="{x}" y="{y}" font-size="21" fill="{colors[row["state"]] if x==380 else "#edf3f8"}">{escape(value)}</text>')
        words = row['reason'].replace('_',' ').split(); lines = ['']
        for word in words:
            if len(lines[-1])+len(word)>27:lines.append('')
            lines[-1] += (' ' if lines[-1] else '')+word
        for line_index, line in enumerate(lines):
            parts.append(f'<text x="1090" y="{y+line_index*23}" font-size="18">{escape(line)}</text>')
        detail = f't={row["timestamp_ns"]/1e9:.1f}s | {row["environment"]["visibility"]} | tracks={len(row["tracks"])} | peers={len(row["cooperative_context"])} | valid TTC={sum(t["valid"] for t in row["ttc"])}'
        parts.append(f'<text x="40" y="{y+36}" font-size="18" fill="#a8bfd0">{escape(detail)}</text>')
        parts.append(f'<path d="M40 {y+67}H1440" stroke="#344854"/>')
    parts.append(f'<text x="40" y="{height-24}" font-size="20">Replay: {escape(summary["replay"]["result"])} | Qualification: {escape(summary["qualification_replay"]["result"])} | Traction DISABLED_PHASE_1 | Advisory only</text></g></svg>')
    return '\n'.join(parts)
