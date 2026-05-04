### Google Ads KPI

Google Ads integration

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app google_ads_kpi
```

### Compatibility

- Supports Frappe `15.x` and `16.x`.
- Does not require ERPNext. Google Ads `source` values are stored as plain text so the app can install on plain Frappe sites.
- AI actions and pipeline writes are restricted to `System Manager`.
- Optional OpenAI answers use `openai_api_key` from site config. Without it, the app falls back to rule-based responses.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/google_ads_kpi
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
