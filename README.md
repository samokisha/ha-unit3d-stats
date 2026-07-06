# UNIT3D Stats

A Home Assistant custom integration that polls a UNIT3D-engine private tracker's API endpoint and exposes your profile statistics as sensors, including upload/download stats, seeding activity, and more.

## Overview

This integration connects to a private tracker running the [UNIT3D](https://github.com/HDInnovations/UNIT3D) engine using your personal API token and retrieves your account statistics. Each statistic is exposed as a sensor entity, allowing you to monitor your tracker activity, trigger automations, or create dashboards based on your ratio, transfer totals, seeding activity, and other profile metrics.

## Getting an API Key

To use this integration, you need an API key from your UNIT3D tracker:

1. Log in to your tracker account in a web browser
2. Navigate to **Settings** (usually accessible from your profile menu)
3. Find the **API Key** section
4. Copy your API key

**Keep your API key secret** — treat it like a password. Do not share it or commit it to version control.

## Installation

### Step 1: Copy the Integration

1. Download or clone the [`ha-unit3d-stats`](https://github.com/samokisha/ha-unit3d-stats) repository
2. Copy the `custom_components/unit3d_stats` directory into your Home Assistant `config/custom_components/` folder
   - Typical path: `~/.homeassistant/custom_components/unit3d_stats`
3. Restart Home Assistant

### Step 2: Add the Integration

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **"UNIT3D Stats"** and select it
4. Enter the **Tracker Base URL** (e.g., `https://tracker.example.com`)
5. Enter your **API Token** (from Step 1 above)
6. Click **Submit**

The integration will validate your credentials and create your entry. A set of sensors will be automatically discovered and available in Home Assistant.

## Sensors

The integration exposes the following sensors from your tracker profile:

| Sensor | Key | Unit | Type | Description |
|--------|-----|------|------|-------------|
| Ratio | `ratio` | — | Measurement | Upload-to-download ratio (e.g., 50.0 = 50:1) |
| Uploaded | `uploaded` | GiB | Total Increasing | Total amount of data uploaded |
| Downloaded | `downloaded` | GiB | Total Increasing | Total amount of data downloaded |
| Buffer | `buffer` | GiB | Measurement | Available bonus buffer/credit |
| Seeding | `seeding` | — | Measurement | Number of releases currently seeding |
| Leeching | `leeching` | — | Measurement | Number of releases currently downloading |
| Seed Bonus | `seedbonus` | — | Measurement | Accumulated seed bonus points |
| Hit & Runs | `hit_and_runs` | — | Measurement | Number of hit-and-run violations |

All numeric values are updated at regular intervals (see Options below).

## Options

After adding the integration, you can configure the update interval:

1. Go to **Settings → Devices & Services** and find your UNIT3D Stats entry
2. Click **Configure**
3. Set the **Update Interval** (in minutes; default is 60 minutes)
4. Click **Submit**

The integration respects the tracker's rate limits by defaulting to a 1-hour polling interval. Adjust as needed, but avoid very frequent updates to prevent being rate-limited by the tracker.

## Local Development

### Setup

To set up a development environment:

```bash
./scripts/setup
```

This installs all required dependencies.

### Running with Mock Data

For testing without hitting the real tracker API:

```bash
UNIT3D_MOCK=1 ./scripts/develop
```

This starts Home Assistant on `http://localhost:8123` with mock data loaded from the integration's fixture file (`custom_components/unit3d_stats/fixtures/user_response.json`). In this mode:
- You can use any tracker URL and API token in the configuration form
- No actual HTTP requests are made to the tracker
- No rate-limit impact
- Useful for UI testing and development

### Running with the Real API

To test against a real tracker:

```bash
./scripts/develop
```

This starts Home Assistant and uses the actual tracker API. You will need a valid tracker URL and API token.

### Linting

Run code quality checks with:

```bash
./scripts/lint
```

This uses `ruff` to check formatting and code style.

## Notes

- **Personal stats only**: The API endpoint only returns statistics for the account owner associated with the API token. You cannot use this integration to monitor other users' accounts.
- **Rate limits**: The default update interval is 1 hour to respect tracker rate limits. If you experience rate-limit errors, increase the interval further.
- **HACS**: This integration is not currently published to HACS. Install manually by copying the `custom_components/unit3d_stats` directory as described above.

## Troubleshooting

### Invalid API Token

If you see an "Invalid API token" error, ensure:
- Your API key is correctly copied from the tracker settings (including any spaces or special characters)
- Your tracker account is still active
- The API key has not been revoked

### Cannot Connect to Tracker

If you see a connection error:
- Verify the tracker base URL is correct (e.g., `https://tracker.example.com` without trailing slash)
- Check that the tracker is online and accessible from your Home Assistant instance
- Ensure your network or firewall does not block outbound HTTPS requests to the tracker

### No Sensors Appearing

After adding the integration:
- Go to **Settings → Devices & Services** and verify the integration shows as "Loaded"
- Check the Home Assistant logs for any error messages from the `custom_components.unit3d_stats` component
- Try restarting Home Assistant

## Contributing

Contributions are welcome! Please ensure all changes pass linting (`scripts/lint`) and any existing tests before submitting a pull request.
