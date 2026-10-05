# 32 — Viability and scalability

## Operation and maintenance

Assign owners for hardware identity, calibration, map/closures, model/configuration release, device credentials and incident review. Operators need startup health/phase/source indication and understandable actions. Maintainers need connector/mount/thermal inspection, manufacturer battery/charger practice, disk retention checks and calibration invalidation after repair. A screen saying ONLINE is not maintenance evidence.

Modular adapters and replaceable documented assemblies reduce repair scope, but every replacement must revalidate identity, electrical compatibility, configuration and affected calibration. Firmware/model updates are versioned with rollback and recorded compatibility; no automatic update changes safety parameters during operation.

## Scaling model

For N nodes at f state messages/s and payload B bytes, application ingress is N f B before TLS/transport overhead. Naive relay-to-all grows O(N² f B); industrial scaling needs region subscriptions and bounded relevant-peer sets with explicit coverage limits. Never silently exclude peers to claim no conflict. Example sizing uses declared N/f/B, not a promised AP capacity.

High-rate media stays edge-local unless bandwidth/consent permit incident upload. Metadata/time-indexed incidents replicate to control room; chunk objects have retention/priority rules. Storage GB/h is computed from actual bitrates plus overhead, not SSD label capacity. Local safety independence survives cloud outages; cooperative corrections/awareness may not.

Student network is a small local experiment. Mine Wi-Fi/private LTE/5G/V2X choice follows RF survey, latency/loss/availability/security requirements and site ownership, not a new purchase now. Base/reference and map services need integrity/lifecycle management; adding more nodes does not fix wrong coordinates.

## Economic viability

INR 247,150 is additional prototype planning cost, NOT per-truck industrial price. A later lifecycle model needs ruggedized BOM, installation, survey, calibration, infrastructure, support, downtime, licenses, training and compliance. Expected production module/custom carrier savings require volume quotes and engineering NRE; no savings percentage is invented.

Start shadow-mode monitoring, then advisory, then supervised operational pilot, and only separately approved OEM intervention. Financial value must be demonstrated with matched operational data and equal safety constraints. Faster travel alone is not a benefit if warning misses or risk increase.
