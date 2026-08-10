# Configuration Setup

## Quick Start

1. Copy the sample file to create your actual config:

```bash
cp config.json.sample config.json
```

2. That's it. The default values match the Docker Compose seeded credentials.

## How It Works

- `config.json` holds environment-specific values (URL, credentials)
- `settings.py` (you create this) loads the JSON and exposes values as properties
- The active environment is controlled by the `ENVIRONMENT` variable (default: `local`)
- Import the singleton: `from tests.config.settings import config`

## Usage Example

```python
from tests.config.settings import config

# In BaseService
self._base_url = config.base_url  # → "http://localhost:3020"

# In conftest.py
email = config.admin_artist_email      # → "artist@beatflow.com"
password = config.admin_artist_password # → "Artist123!"
```

## Running Against Different Environments

```bash
# Default (local)
python -m pytest

# Explicit
ENVIRONMENT=local python -m pytest

# If you add a staging section to config.json:
ENVIRONMENT=staging python -m pytest
```

## See Also

Read `docs/sdet-guide/10-configuration.md` for the full explanation of how to build `settings.py`.
