# TARK R2 — budget allocation

Revision M1 • Currency INR • 1 October 2026.

**Additional planning total: INR 247,150. Ceiling: INR 250,000. Unallocated headroom: INR 2,850.** This includes INR 5,000 pricing uncertainty and INR 5,000 contingency as separate allocations, plus INR 4,000 ordinary integration spares. These are not three spare premium sensors.

All numbers are technical planning allowances, not quotes, landed-cost guarantees, orders or delivery commitments. Owned equipment has zero incremental acquisition cost, not zero historical/economic value. No labor, HEMM purchase, commercial mine survey, certification or industrial field deployment is funded here.

## Reconciliation

| Allocation | BOM IDs | INR |
|---|---|---:|
| Main edge computer | M01 | 50,000 |
| Radar | M02 | 42,500 |
| RGB | M03 | 6,500 |
| Thermal core + acquisition bridge | M04–M05 | 33,000 |
| Three complete RTK kits | M06–M08; antennas M17 bundled | 28,500 |
| IMU | M09 | 3,500 |
| Display + NVMe | M10–M11 | 16,000 |
| Powered USB hub + local AP | M12–M13 | 6,000 |
| DP adapter + four USB data cables | M14–M15 | 5,400 |
| Audible alert | M16 | 750 |
| **New exact-part electronics subtotal** | M01–M17 | **192,150** |
| Two wheel-sensing assemblies | R01 | 4,000 |
| Protected power, conversion, chargers, fusing and manual disconnect | R02 | 18,000 |
| Mast/mounts/guards/enclosures | R03 | 6,500 |
| Remaining harness, strain relief and connectors | R04 | 2,500 |
| Calibration/reference fixtures and instrument-access allowance | R05 | 5,000 |
| Controlled artificial-aerosol experiment | R06 | 5,000 |
| Cables/connectors/ordinary integration spares | R07 | 4,000 |
| Price/tax/import-charge uncertainty reserve | R08 | 5,000 |
| Contingency | R09 | 5,000 |
| **Assemblies / integration / reserves subtotal** | R01–R09 | **55,000** |
| Owned equipment | O01–O12 | 0 |
| **Total additional allocation** | All BOM records | **247,150** |
| Ceiling minus total | 250,000 − 247,150 | **2,850** |

Spreadsheet authoring uses quantity × unit allocation for every row, recalculation, independent summation and CSV round-trip checks. No missing price is silently treated as zero: nonzero unquoted categories are expressly estimated. Zero only denotes owned or already bundled items.

## Price provenance and uncertainty

The source ledger for technical identity is in document 03. Price sources support approximate planning only. An exact selection can be technically decided even when a listing is unavailable or its stock is zero.

| Selection | Observed anchor / retrieval basis | Allocation rationale |
|---|---|---|
| Jetson 0000 | [MG Super Labs](https://mgsl.in/products/nvidia-jetson-orin-nano-super-developer-kit-67-tops), opened INR 47,499 tax-inclusive | INR 50,000; explicit regional-SKU caveat in document 03 |
| IWR1843BOOST | [Mouser India](https://www.mouser.in/en/ProductDetail/Texas-Instruments/IWR1843BOOST?qs=RcG8xmE7yp2iITEK4ql0DA%3D%3D), indexed INR 35,892; direct retrieval unavailable | INR 42,500; approximately base × 1.18, rounded. 18% is a planning provision, not confirmed invoice treatment |
| B0200 | [Fab.to.Lab family listing](https://www.fabtolab.com/arducam-b0200-b0201-b0202-1080p-low-light-wide-angle-usb-camera-module-microphone-computer-2mp-1-2-8-inch-cmos-imx291-120-degree-mini-uvc-usb2.0-webcam-board-3-3ft-1m-cable-windows-linux-mac-os), INR 5,262 | INR 6,500; exact B0200 retained, not B0201/0202 optics |
| Lepton 3.5 | [DigiKey](https://www.digikey.in/en/products/detail/flir-lepton/500-0771-01/500-0771-01-ND/7606616), INR 16,434.60 from earlier same-day review | INR 19,400 includes approximate 18% tax provision; no double purchase of bridge |
| PureThermal 3 | [DigiKey](https://www.digikey.in/en/products/detail/groupgets-llc/PURETHERMAL-3/18677153), INR 11,465.04 from earlier same-day review | INR 13,600 includes approximate 18% provision |
| Waveshare 33000 | [Hubtronics](https://hubtronics.in/lg290p-gnss-rtk-module), INR 9,099 incl GST | INR 9,500 each; antennas included, USB cables separate |
| BNO085 breakout | [DigiKey 4754](https://www.digikey.in/en/products/detail/adafruit-industries-llc/4754/13426653), search index INR 2,818.73; differing indexed prices exist | INR 3,500 approximate allocation, not a verified checkout price |
| Display | [Hubtronics 11199](https://hubtronics.in/7inch-hdmi-lcd-c), INR 4,479 incl GST | INR 5,000; missing bundled display cable covered by harness allocation, not assumed free |
| SSD | [Green Apple](https://greenapplecompunet.com/product/kingston-500gb-nv3-m-2-2280-nvme-ssd/), opened INR 10,539 incl GST; [PrimeABGB](https://www.primeabgb.com/online-price-reviews-india/kingston-nv3-500gb-gen4x4-m-2-internal-ssd-snv3s-500g/) INR 10,308 | INR 11,000; no outdated low price used |
| UH720 | [Moglix](https://www.moglix.com/tp-link-7-port-usb-30-data-hub-with-2-port-smart-charger-uh720/mp/msnm9xy2zj7mkj), INR 2,905 incl tax | INR 3,500; exact V5.0 remains selected even though retailer revision isn't confirmed |
| AP | [Flipkart](https://www.flipkart.com/tp-link-tl-wr902ac-750-mbps-router/p/itmf47djfhyzrhzf), INR 2,099 + 29 listed fee | INR 2,500; V3 chosen, not an undocumented revision substitution |
| DP2HDMI2 | [DigiKey](https://www.digikey.in/en/products/detail/startech-com/DP2HDMI2/21399111), indexed INR 2,420.40 | INR 3,000 approximate allowance |
| UGREEN data cable | Manufacturer identifies 60116; no verified Indian quote used | INR 600 each engineering estimate; deliberately not the far more expensive StarTech USB2AC1M price |
| Buzzer | Manufacturer identifies 107020000; no verified INR quote used | INR 750 engineering estimate, not acoustic certification |
| Wheel/power/mechanics/test/reserves | Engineering allocations, no retailer claims | Exact assembled SKUs and quantities sized during detailed design; no false price precision |

The INR 250,000 conclusion is a **planning** conclusion. It is not robust to arbitrary price rises: spending the INR 5,000 price reserve and INR 5,000 contingency plus INR 2,850 headroom absorbs INR 12,850 unforeseen cost if other allocations hold. Do not double-count those reserves as still available after spending. A 10% rise across the INR 192,150 exact-part allocation would exceed that flexibility; a later quote must trigger budget reconciliation, not a quiet reduction in protection or a false “within budget” claim. The 0007 kit at the earlier INR 68,000 observation would add INR 18,000 and requires an explicit revised budget, not an automatic substitution.

## Why 500 GB, not 1 TB

Illustrative retention sizing, **not measured bitrate**: RGB compressed at 8 Mb/s gives 3.6 GB/h. Thermal at 160 × 120 × 2 bytes × 8.7 frames/s gives about 1.20 GB/h before overhead. A deliberately conservative assumed 0.5 MB/s for radar/other records adds 1.8 GB/h. Total example: about 6.60 GB/h. A 400 GB dataset allocation supports roughly 60 hours in that example; actual retention depends on formats, metadata, filesystem, bitrate and reserved free space.

Uncompressed 1080p RGB at 30 fps and 3 bytes/pixel would be approximately 672 GB/h and is not the planned continuous-recording mode. Preserve useful timestamps/data, use supported camera compressed output where suitable, measure decode/inference/recording load, and enforce bounded retention. A larger SSD does not fix uncontrolled recording or lost metadata. 1 TB remains excluded for this budget.

## No hidden costs or hidden guarantees

- Power allocation includes protected electronics energy source/matched charger, compute/sensor/USB regulation, Pi-node power, fusing, manual disconnect and suitable mains leads. Existing unknown traction pack is not treated as a qualified free charger/battery system.
- Mount allocation includes guards and rigid thermal/RGB/radar alignment, not just decorative enclosure.
- Calibration allocation includes optical chart/radar reflector/thermal reference/GNSS reference fixtures and access to basic measurement tools. A surveyed absolute RTK accuracy claim needs reference equipment of adequate uncertainty; if unavailable, report repeatability only.
- Aerosol equipment may be borrowed/rented within the allocation; it is not an owned purchase at an invented exact SKU.
- Local AP, USB hub and display package cables must be inventoried; harness allocation covers the remaining leads. Four M15 cables are not charged again there.
- Borrowed instruments, student labor and the owned laptop are disclosed assumptions. Real mine survey, industrial ruggedization and certification require a separate budget.
