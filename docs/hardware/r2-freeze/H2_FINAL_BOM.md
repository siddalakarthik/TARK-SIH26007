# TARK R2 — H2 component selection and cost review

Revision A0, 1 October 2026. **BATCH A FREEZE FAILED. DO NOT ORDER FROM THIS FILE.**

The required filename does not imply a released BOM. The CSV records one selected design-review item per resolved function, owned assets and explicit engineering reserves. `INCLUDED` means included in this assessed design, not cleared for purchase or energization. Unresolved mandatory selections are listed openly below instead of disguising generic placeholders as exact parts. All CSV rows carry `NOT FROZEN`.

## Selected design-review configuration

| BOM | Qty | Selected identity | Role / release qualification |
|---|---:|---|---|
| A01 | 1 | NVIDIA Jetson Orin Nano Super Developer Kit 8 GB, **945-13766-0007-000** | Main edge compute; India/Taiwan SKU verified by NVIDIA; budget not closed |
| A02 | 1 | Texas Instruments **IWR1843BOOST** | Primary processed-measurement radar; not AWR1843BOOST |
| A03 | 1 | Arducam **B0200**, IMX291 RGB, supplied 100-degree diagonal lens | UVC color evidence; not B0201/B0202 variants |
| A04 | 1 | Teledyne FLIR Lepton 3.5 **500-0771-01** | LWIR core; installed in A05 |
| A05 | 1 | GroupGets **PURETHERMAL-3** | Complete core host-interface selection; USB data cable A14 required |
| A06 | 1 | Waveshare LG290P GNSS RTK Module **33000**, with RTC battery | Main rover; supplier identity recorded, full manufacturer board/antenna verification open |
| A07 | 1 | Same exact **33000** kit | Second physical rover, hosted by A15 |
| A08 | 1 | Same exact **33000** kit | Fixed local base, hosted by A25; not a third vehicle |
| A09 | 1 | Waveshare **11199**, 7inch HDMI LCD (C), 1024 × 600 | Local driver display; HDMI model, not DSI |
| A10 | 1 | Kingston NV3 500 GB **SNV3S/500G**, M.2 2280 | Main boot/recording SSD; host/boot compatibility still requires confirmation |
| A11 | 1 | TP-Link **UH720(UN), hardware V5.0** | Powered USB expansion; retailer has not guaranteed V5.0 |
| A12 | 1 | TP-Link **TL-WR902AC, hardware V3** | Local network in AP mode; retailer hardware-version confirmation open |
| A13 | 1 | StarTech **DP2HD4K60S** | Active DisplayPort-to-HDMI conversion; exact display mode must be confirmed |
| A14 | 4 | StarTech **USB2AC1M** | Data/power cables for thermal and three GNSS kits; cable prices not obtained |
| A15 | 1 | Owned Raspberry Pi **3 Model B+** | Second-node positioning/correction relay only; no duplicate perception engine |
| A16 | 1 | Owned ESP32-S3 **N16R8 / HW678-style board** | Local supervisor candidate; exact PCB identity remains missing |
| A17 | 1 | Owned **HLK-LD2450** | Bench comparison/reference only, not a second active primary radar |
| A18 | 1 | Owned **L298N breakout** | Existing robot bridge; exact board/current compatibility not released |
| A19 | 4 | Owned yellow **TT geared DC motors** | Existing drivetrain retained for assessment; exact variants unverified |
| A20 | 1 | Owned acrylic four-wheel chassis | Reuse intent; dimension/load/encoder-fit evidence missing |
| A21 | 1 | Owned traction pack, reported **7.78 V measured** | Identity, chemistry, capacity, protection and suitability unknown |
| A22 | 1 | Owned **12 V SLA**, reported approximately **1.3 Ah** | Bench asset only; label/condition not verified; no onboard payload assumption |
| A23 | 1 | Owned SanDisk Ultra **32 GB microSDHC A1** | Pi node-B boot card; suffix/condition not verified |
| A24 | 1 | Owned unidentified working USB webcam | Bench/reference stream only; not a second flagship RGB channel |
| A25 | 1 | Existing development PC, exact asset record required | Shared stationary base relay and control-room browser; availability/identity open |
| A26 | 3 | Antennas supplied in the exact **33000** kits | Included in kit cost; antenna part number, bands, connector and bias compatibility unverified |

R01–R08 are budget allocations, not purchased components. They are listed in the CSV so integration costs cannot disappear. Quantities of bundled accessories are not extra kit purchases.

## Mandatory selections not resolved

| Gap | Why no exact item is released | Required evidence/decision |
|---|---|---|
| GAP-ENCODER | Shaft access, dimensions and current GPIO allocation are not established | P03/P09 photos; compare attachable quadrature pickup versus contactless angular sensing against actual geometry. Do not order generic encoders on assumed TT compatibility. |
| GAP-POWER | No identified mobile electronics energy source with a justified load/runtime/payload budget | Battery labels, load envelopes, duty-duration requirement and chassis allowance. Existing SLA is not silently selected as the onboard source. |
| GAP-CUTOFF | Existing red switch/relay have no verified DC interruption or coil/driver information | Establish maximum pack voltage and load current before selecting a rated independent traction-interruption assembly. |

These three absent exact selections alone prevent a freeze. PCB identities, antenna match, delivered revisions, accessory completeness and procurement costs also remain release gates. H4/H5/H6 may not silently fill these gaps after a claimed PASS.

## Interfaces and accessories audit

### Main host

NVIDIA documents four USB-A host ports, DisplayPort, Gigabit Ethernet and M.2 2280 PCIe 3.0 x4 storage. USB-C is not an HDMI/DisplayPort output. The proposed allocation is RGB, radar and ESP32 directly on three host ports, with A11 on the fourth. A11 carries thermal, main GNSS and display touch. This is a capacity allocation, not physical routing or proof of simultaneous bandwidth/power performance. The hub's two charging-only ports are not data ports.

The supplied NVIDIA bench PSU is 19 V. Super-mode module power is not the complete system power budget. Carrier, SSD, fan, USB loads and conversion losses must be accounted separately. A21 or A22 must not be connected directly by inference from nominal voltage. The included fan/heatsink must remain serviceable.

A10 fits the documented 2280 NVMe form-factor/interface class; PCIe generation negotiation and chosen JetPack boot support must be confirmed. No tested SSD compatibility or recording duration is claimed. The owned 32 GB card remains with Pi; it is not counted twice.

### Radar

TI specifies the IWR1843 device as 76–81 GHz with three transmit and four receive channels. The BOOST board has onboard XDS110 programming/debug and USB-UART paths. The TI guide lists a micro-USB cable and vertical mounting brackets in the kit, but an external 5 V, greater-than-2.5 A supply is not included. Its 2.1 mm centre-positive barrel connection is not the Jetson's 5.5 × 2.5 mm connector.

Use a documented IWR1843-compatible mmWave SDK processed-output application later. No firmware is flashed now. DCA1000/raw-ADC capture and a second debugger are excluded: they are unnecessary for the chosen processed-UART architecture. Exact board dimensions/mass and the versioned application-output contract remain open engineering fields, not invented specifications.

### Thermal

The selected assembly is **A04 + A05 + one A14**, plus the mounting allowance. The core is 160 × 120, 57-degree horizontal FOV and 8.7 Hz effective frame rate in FLIR's datasheet. PureThermal supplies Linux-compatible UVC acquisition. Radiometric transport/interpretation is a later software integration task; a colorized stream alone is not calibrated temperature evidence.

PureThermal Rev2 documents 3.4–5.5 V VIN and 350 mA peak, but its VIN pin row says 320 mA. Record the discrepancy; use the larger value only as a conservative design bound pending supplier clarification. Do not confuse the 3 V logic field in distributor metadata with USB input voltage. PT3 dimensions are 25.8 × 28.9 mm; manufacturer mass is under 3 g without the core. Assembled lens clearance and mount need review. No direct 5 V feed to the bare core is specified here.

### RGB

A03 is selected for documented Linux UVC, repeatable M12 optics and compressed 1080p acquisition, rather than guessing the existing webcam identity. Arducam publishes 30 fps H.264/MJPEG at 1920 × 1080, 5 V supply, maximum 300 mA working current, 38 × 38 mm board and a 1 m cable. Published focus begins at 1 m. Nearer demonstrations therefore require a verified optical setup; no close-focus guarantee is assumed. Manual exposure controls and acquisition latency must be characterized. Vendor low-light advertising is not evidence of fog penetration.

### GNSS and corrections

Three exact kits provide two rovers and one base. A08 connects to the stationary A25 host, which forwards corrections over A12 to Jetson/A06 and Pi/A07. A15 owns node-B position/health relay only. No second Jetson, cellular modem, subscription NTRIP assumption or duplicated simulated node is introduced.

Quectel's LG290P(03) RTK application note documents base/rover operation and RTCM correction handling. This does not establish the firmware/version or full antenna specification of a retailer's assembled Waveshare kit. The manufacturer board pages were search-visible but direct retrieval failed. The retailer lists a USB-C UART bridge, antenna and RTC battery; treat those as package-identification leads, not replacement electrical specifications. Three matching bundled antennas are costed with the kits, but their exact band coverage, connector, bias requirements and reference-plane mounting are not frozen. USB cables are not listed in that kit's package, hence A14.

RTK fixed/float/single/no-fix and correction age remain distinct. A self-surveyed base can support relative experiments but does not by itself establish survey-grade absolute coordinates. One antenna does not supply reliable stationary vehicle heading. No indoor centimetre claim or GNSS-to-motion authority is introduced.

### Display, network and hub

The display requires HDMI video and USB touch/power, not CSI/DSI. The Jetson therefore needs A13 and an HDMI cable; display kit cable contents, input current, exact board revision and EDID/mode support must be confirmed. A13's general DP compatibility does not prove this panel's 1024 × 600 mode.

The AP is a local-network appliance, not a base-station GNSS computer or safety controller. Its 100 Mbps Ethernet port and nominal radio rates are not measured TARK throughput. V3's supply is documented as 5 V/2 A. Its datasheet calls the power connector mini-USB while the current web page says micro-USB: require actual revision/package confirmation and use its supplied cable until resolved.

UH720 V5.0 documents a 12 V/3.3 A adapter; the general product page describes 12 V/4 A. Do not substitute the latter specification into a V5.0 power design. Retailer revision not yet guaranteed. The supplied hub upstream cable and power adapter are included in the hub row, not separately purchased.

## Cost evidence and arithmetic

**No purchases were made. This pass committed INR 0. Prior spending is not audited here.** The following is an observed-price scenario, not a delivered quote or a released procurement total. Currency INR throughout. Sources are in the ledger. Unknown landed costs remain `UNKNOWN` in the CSV and are never summed as zero.

| Item | Listed unit price used | Qty | Listed-price extension | Material price limitation |
|---|---:|---:|---:|---|
| A01 Jetson | 68,000.00 | 1 | 68,000.00 | Opened retailer page; search index showed 33,600; tax/stock/arrival not confirmed |
| A02 radar | 35,892.00 | 1 | 35,892.00 | Attributed Mouser indexed page, direct fetch failed; taxes/freight unresolved |
| A03 RGB | 5,262.00 | 1 | 5,262.00 | Listing combines lens variants; exact B0200 quote/tax confirmation required |
| A04 core | 16,434.60 | 1 | 16,434.60 | DigiKey INR listing, not complete landed charge |
| A05 interface | 11,465.04 | 1 | 11,465.04 | DigiKey INR listing, not complete landed charge |
| A06–A08 GNSS | 9,099.00 | 3 | 27,297.00 | GST included; listing explicitly out of stock |
| A09 display | 4,479.00 | 1 | 4,479.00 | GST included; actual PIN/arrival not confirmed |
| A10 SSD | 10,616.00 | 1 | 10,616.00 | Opened page differs from indexed 10,450; use higher observation, not a quote |
| A11 hub | 2,905.00 | 1 | 2,905.00 | All taxes included; V5.0 not guaranteed |
| A12 AP | 2,099.00 | 1 | 2,099.00 | Generic model listing, not confirmed V3 quote; fees/shipping extra |
| **Priced subset** | | | **184,449.64** | Excludes A13/A14 and incomplete landed charges |

| Reserve | Purpose | Engineering allowance INR |
|---|---|---:|
| R01 | Power conversion, protected mobile supply, physical cutoff and electrical protection | 12,000 |
| R02 | Mounting, fabrication, guards, enclosure and strain-relief supports | 6,500 |
| R03 | Remaining cables, connectors and harness consumables | 2,500 |
| R04 | Calibration references, wheel-response pickup provision and test fixtures | 5,000 |
| R05 | Approved low-visibility experiment equipment and safe arrangement | 5,000 |
| R06 | Essential spares; no second premium sensor presumed | 4,000 |
| R07 | Shipping/import uncertainty buffer; not a tax or freight quotation | 5,000 |
| R08 | General integration contingency | 5,000 |
| **Protected total** | | **45,000** |

These are explicit engineering allocations, not vendor prices. They require revalidation once power and geometry are known. A13/A14 are explicit unpriced purchases outside the remaining-harness reserve; do not count them twice later. Taxes missing from the priced electronics are not assumed fully covered by R07.

- Listed subset plus reserves = **INR 229,449.64**, already **INR 24,449.64 above** the hard ceiling, before unpriced accessories or additional landed charges.
- Remaining room under the ceiling after the listed subset = **INR 20,550.36**, versus INR 45,000 protected reserves.
- Full landed purchase total / compliant remaining H4–H12 budget = **UNKNOWN / NOT ESTABLISHED**.
- Holding the other listed figures constant, Jetson would need to cost at most **INR 43,550.36** merely to remove this preliminary excess. That threshold still excludes A13/A14 and missing charges; it is not a vendor offer or final allowable purchase price.

Do not respond by deleting protection/test reserves. First seek a dated exact-SKU Jetson quote or a documented lab loan and a complete RTK supply quote. No loan is assumed available or free. If those cannot close the budget, reopen the affected component decision explicitly before release. Pi-only inference has not been benchmarked sufficiently to call it an equivalent replacement; MLX90640 is a materially lower-resolution thermal direction and is not silently substituted.

## Procurement deadline risks and fallback priority

| Part | Evidence on 1 October | 15 October risk | Best next procurement action |
|---|---|---|---|
| Jetson | Major indexed/opened price conflict; no committed dispatch date | HIGH | Seek authorized/local exact-SKU quote first; documented same-kit lab loan is preferable to an unverified import promise |
| IWR1843BOOST | Indexed Mouser 63 units; 12-week factory lead applies beyond shown stock | HIGH until orderable stock/arrival verified | Confirm distributor allocated stock and delivery; same-EVM lab loan preferable to waiting for factory replenishment |
| Lepton/PT3 | DigiKey displayed 14,718 cores and 378 PT3; GroupGets core out of stock | HIGH until India shipment/export/charges confirmed | Quote complete DigiKey assembly; lab loan of same full assembly if shipment cannot meet target |
| Three GNSS kits | Hubtronics 0 stock at INR 9,099 | HIGH | Ask local supplier for three actual units; matched three-kit lab loan preferred over unsupported replacement/NTRIP assumption |
| RGB | Multi-variant page says in stock | MEDIUM/HIGH | Confirm B0200 100-degree variant and dispatch, not family-page availability |
| Display | Listing reports 38 units | MEDIUM | Confirm exact revision/accessories and PIN delivery |
| SSD/AP/hub/cables | Quotes/revisions or price conflicts unresolved | MEDIUM/HIGH | Obtain exact-part all-in quote and arrival confirmation; do not use expired offer/delivery labels |

No supplier has been contacted and no loan/rental agreed in this task. Stock observations are web evidence, not reserved stock. The 15 October target is not a promised delivery date.
