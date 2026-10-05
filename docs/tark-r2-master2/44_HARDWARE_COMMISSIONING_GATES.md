# 44 — Hardware commissioning gates

No physical testing performed or authorized by this document. A qualified responsible person must approve the actual setup and later test request. UNKNOWN is a stop condition for an unresolved electrical rating, not an invitation to experiment with full power.

## Before energization

Require actual board/device labels and revisions, correct supply and range, polarity, current capacity/inrush, fuse and conductor/connector ratings, mapped grounds/returns, no shorts/alternate feeds, current limiting where appropriate, thermal monitoring, accessible rated traction interruption, secured mechanics and software STOP/inhibited state. Verify chemistry/matched charger before battery use. Do not use damaged LM2596 or L298N regulator for compute/controllers.

| Gate | Entry / work | Evidence and exit |
|---|---|---|
| H0 Unpowered identity | Photos/labels, board schematic/pin inventory, hub/wheel/chassis measurements | Open electrical/mechanical detail closed enough for reviewed drawing |
| H1 Device alone | Approved supply/polarity/protection and controlled bench plan | Voltage/current/inrush/temperature within documented limits |
| H2 Host communication | Verified device/port and one owner; traction isolated | Actual identity, formats, source times and truthful errors |
| H3 Data validation | Qualified reference/known inputs | Checksums/units/frame/quality/freshness and no fabricated samples |
| H4 Multi-device | Reviewed total load/returns/USB topology | Concurrent load, noise, unplug/reconnect and bounded queues |
| H5 Stationary integration | Mounted/calibrated full stack; no traction | Correct source/mode/time, software zero outputs and recordings |
| H6 Lifted-wheel motion | Separately approved phase/pins/enables, guarded setup, qualified cutoff | Reset/expiry/link loss zero behavior first; measured wheel response, no people in path |
| H7 Contained ground | H6 plus payload/stability and measured coast/stop domain | Low-energy supervised course, margins and interruption evidence |
| H8 Full demonstration | Required technical/safety gates complete | Labelled reproducible run, known limitations and emergency procedure |

No automatic jump from a host-test PASS to H6. Port enumeration is not identity/calibration. A current-limited source does not remove all electrical/mechanical risks. Physical interruption may allow coasting; prove mechanical outcome separately.

Physical outputs remain DISABLED_PHASE_1 until separately reviewed authorization changes phase. Stop on unexpected heating, smell, current, movement, brownout, inconsistent pin mapping, fluid ingress, loose mounts or missing supervising engineer. Preserve failure evidence and revise the test plan before retrying.
