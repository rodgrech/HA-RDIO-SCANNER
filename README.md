# Rdio Scanner for Home Assistant

A custom Home Assistant integration and dashboard card for a local
[Rdio Scanner](https://github.com/chuot/rdio-scanner) server.

Default scanner URL used by the setup form and examples:

```text
http://192.168.1.49:3000
```

## Features

- UI-based Home Assistant setup
- Polls the local Rdio Scanner web UI for availability
- Optional admin password support for config count sensors
- Sensors for status, URL, systems, talkgroups, groups, tags, branding, and email
- Lovelace card that embeds the live Rdio Scanner interface for scanner audio
- HACS-ready repository layout

## Important Note About Audio

Rdio Scanner exposes its live calls and playback controls through its own web
client. This project does not clone that client or use the reserved WebSocket
API directly. The custom card embeds the official local Rdio Scanner web UI in
Home Assistant, so audio playback stays handled by Rdio Scanner itself.

The Home Assistant integration uses supported HTTP endpoints:

- `/` to check that the scanner server is reachable
- `/api/admin/login` and `/api/admin/config` when an admin password is supplied

## Installation

### HACS custom repository

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Select `Integration` as the repository category.
4. Install **Rdio Scanner**.
5. Restart Home Assistant.

### Manual installation

Copy this folder into Home Assistant:

```text
custom_components/rdio_scanner
```

Then restart Home Assistant.

## Configuration

1. Go to **Settings** -> **Devices & services**.
2. Select **Add integration**.
3. Search for **Rdio Scanner**.
4. Enter your scanner URL:

```text
http://192.168.1.49:3000
```

The admin password is optional. If you leave it blank, Home Assistant creates
the status and URL sensors only. If you provide it, the integration can also
read configuration counts such as systems and talkgroups.

## Dashboard Card

Copy the card file into Home Assistant:

```text
www/rdio-scanner-card.js
```

Add it as a dashboard resource:

```text
/local/rdio-scanner-card.js
```

Resource type:

```text
JavaScript module
```

Example card:

```yaml
type: custom:rdio-scanner-card
title: Rdio Scanner
url: http://192.168.1.49:3000
status_entity: sensor.rdio_scanner_status
systems_entity: sensor.rdio_scanner_systems
talkgroups_entity: sensor.rdio_scanner_talkgroups
height: 640
```

The same example is available at:

```text
examples/rdio-scanner-card.yaml
```

## Notes

- If Home Assistant is served over HTTPS and Rdio Scanner is served over HTTP,
  some browsers may block the embedded frame as mixed content. Use HTTP for
  both on the LAN, or put Rdio Scanner behind HTTPS.
- If you change the Rdio Scanner port, update both the integration URL and card
  `url`.

## License

MIT
