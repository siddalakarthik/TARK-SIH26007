# TARK universal access and public deployment

TARK is one same-origin FastAPI application: the browser loads the React build, REST endpoints and WebSocket from the hostname in its address bar. The frontend uses relative `/api/...` paths and derives `ws://` or `wss://` from the current page protocol and host. It does not embed `localhost`, an IP address, or port 8000 in production transport code.

## Deployment profiles

| Profile | `TARK_ENV` | Access | Intended use |
|---|---|---|---|
| Local development | `development` | `public_demo` | `http://localhost:8000` on the developer workstation |
| Edge / Raspberry Pi | `edge` | `authenticated` recommended | browser reaches Pi through `http://tark.local` or a configured LAN hostname |
| Public demo | `public_demo` | `public_demo` | public HTTPS simulation only; no physical hardware or actuation |
| Public hardware monitoring | `public_hardware` | `authenticated` | future outbound tunnel from Pi; Pi remains safety authority |

`PUBLIC_DEMO_MODE` is read-only simulation. `AUTHENTICATED_MODE` requires `TARK_ACCESS_TOKEN`; the server creates a strict, HttpOnly session cookie after a bearer-token session request. The visible role selector changes presentation only and never grants backend privileges. Do not place the token in frontend environment variables or commit it.

The deployment configuration rejects unsafe profile combinations: `public_demo` requires `public_demo` authentication and reviewed simulation configuration; `public_hardware` requires `authenticated` mode. `TARK_CORS_ORIGINS`, when needed for an approved cross-origin console, accepts only explicit `http(s)` origins—never `*` or paths. Public-demo CSP permits `https:`/`wss:` connections and does not permit insecure `ws:` transport.

## Local and LAN

Build and start on Windows:

```powershell
.\scripts\build_frontend.ps1
.\scripts\test.ps1
.\scripts\run.ps1
```

Open `http://localhost:8000`. For LAN, run this same service on the edge host and use a locally configured DNS/mDNS hostname such as `http://tark.local`; do not hard-code an IP address in source. LAN access is **supported but not verified from a second device in this task**.

## Public demo using Render

The repository includes `render.yaml` and `Dockerfile`. The Blueprint explicitly requests Render's `free` plan. An administrator must create/connect a Render account and repository, then create a web service using the Blueprint. Render supplies a stable `onrender.com` hostname and HTTPS, and its WebSocket-capable web service routes public traffic to the process port supplied as `PORT`. The container uses `0.0.0.0:$PORT` rather than 8000. Free services have an ephemeral filesystem and can sleep after inactivity; public TARK remains simulation-only and must never be treated as connected vehicle hardware.

1. Push this repository to an administrator-controlled Git repository.
2. In Render, create a Blueprint/web service from that repository.
3. Confirm `TARK_ENV=public_demo` and `TARK_AUTH_MODE=public_demo`. The reviewed `config/phase1.json` selects simulation, and application startup rejects a public demo if that configuration is changed away from simulation.
4. Deploy, then use the assigned HTTPS hostname. Do not describe it as real vehicle telemetry.
5. Verify `/ready`, `/health`, `/api/v1/status`, browser HMI and WSS from a different network before announcing the URL.

For a custom domain, add it to the Render service, create the DNS record Render requests at the domain registrar, complete verification in Render, and test the resulting HTTPS/WSS URL. Render documents its public hostnames, WebSocket support, and managed TLS/custom-domain workflow: [web services](https://render.com/docs/web-services), [WebSockets](https://render.com/docs/websocket), and [custom domains](https://render.com/docs/custom-domains).

## Edge public access option: Cloudflare Tunnel

For future Pi-based monitoring, keep the TARK service local and configure an administrator-owned Cloudflare Tunnel to map an approved public hostname to `http://localhost:8000`. Use [deploy/cloudflared.config.example.yml](../deploy/cloudflared.config.example.yml) only as a template; credentials and tunnel tokens are secrets and must remain outside the repository. Cloudflare documents that tunnels map a public hostname to a local service without opening inbound ports: [Tunnel routing](https://developers.cloudflare.com/tunnel/concepts/routing/).

In `public_hardware`, use `TARK_AUTH_MODE=authenticated`, a secret `TARK_ACCESS_TOKEN`, an approved hostname, HTTPS/WSS, and an access policy before exposing telemetry. This does not make public infrastructure a safety authority: browser access remains monitoring-only, Pi remains the decision authority, ESP32 validates bounded commands, and the physical E-stop remains independent.

## Map, routing and device truth

Map style configuration is optional. The HMI defaults to OpenFreeMap Liberty without a key; `VITE_MAP_STYLE_URL` takes priority over legacy `VITE_MAPTILER_STYLE_URL`. Set `TARK_DEFAULT_MAP_CENTER` only for an approved display location. Without a vehicle location or approved display centre, the HMI uses a labelled India overview and does not fabricate GPS. Routing is `NOT CONNECTED` unless an actual provider is configured and tested. Hardware must remain `NOT_CONNECTED_PHASE_2`/`DISABLED_PHASE_1` until verified; no deployment profile enables traction.

## Verification limits

This repository has been locally built and browser-automated on a desktop viewport and responsive emulated viewports. A public URL, real WSS through a provider, custom DNS, an external network, real Chrome/Edge/Firefox installations, and physical iPhone/Android devices have **not** been verified because no hosting/DNS account or external test device was provided.
