# 35 — Security architecture

PROPOSED controls, not a cybersecurity certification or assertion the current demo already implements all of them.

Trust zones: sensor/endpoint local interfaces; edge decision service; authenticated local fleet/correction network; operator browser; administrative/configuration workflow; recording/export storage. Internet/public demo is simulation-only, never a bridge to hardware authority.

Use TLS for fleet/control-room transport with explicit trust provisioning and hostname verification. Per-device identities bind vehicle IDs to credentials; unknown/mismatched nodes cannot publish authoritative peer state. OIDC for human login and short-lived validated JWTs are an industrial/control-room direction; validate issuer, audience, expiry and role server-side. An isolated student deployment may use a simpler reviewed local auth setup, but must not be described as OIDC-complete.

RBAC: driver observes/acknowledges receipt; supervisor inspects events/proposes operational context; maintainer records evidence; administrator provisions identities; approved reviewer releases map/configuration. None has arbitrary browser motor API. Origin/CORS is not authorization. CSRF/session protections apply to mutation workflows; replay/public-demo mutation restrictions remain.

Signed configurations/maps/models include version/hash, issuer, validity and rollback policy. Signature proves approved origin, not safe parameter values. Reject unknown schemas/units and incompatible hardware/calibration. Changes affecting authority require review and a safe stopped deployment procedure, not hot edits.

Credentials remain outside source, docs and recordings; use protected environment/secret stores with least privilege. Do not print tokens in logs. Audit actor/action/result/version and device/session transitions; bound logs and protect retention. Hashes identify data; signed manifests/access controls improve tamper evidence but do not create legal forensic certification.

Threats: replayed/forged peer positions, malicious closures, huge packets, slow clients, wrong clocks/base coordinates, compromised browser and sensor spoofing. Counter with schema/time/identity checks, bounded queues/rate limits, network segmentation, authenticated publishers and independent plausibility. GNSS authenticity is not guaranteed by TLS around downstream telemetry.

Protocol V2 CRC is corruption detection, not cryptographic authentication. Local cable trust and later threat-based endpoint security review remain separate. A network attacker cannot be given motor authority by changing a displayed state. Security failures remove affected context and produce UNKNOWN, not fake healthy fallback.
