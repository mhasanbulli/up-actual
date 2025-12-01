# Up + Actual Budget

![ci-workflow](https://github.com/mhasanbulli/up-actual/actions/workflows/ci.yaml/badge.svg)

A Python CLI tool that synchronises transactions from Up Banking (Australian bank) to Actual Budget for personal finance management.

## Overview

This tool fetches transactions from the Up Banking API and reconciles them with Actual Budget using the `actualpy` library. It automatically creates new transactions and updates existing ones, applying category mappings and running Actual Budget rules.

## Features

- Fetches transactions from Up Banking accounts
- Syncs transactions to Actual Budget
- Handles transaction reconciliation (updates existing transactions)
- Maps Up Banking categories to simplified Actual Budget categories
- Supports round-up amounts
- Pagination support for large transaction sets
- Configurable date ranges and batch sizes

## Requirements

- Python 3.12+
- Up Banking account with API token
- Actual Budget server instance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mhasanbulli/up-actual.git
cd up-actual
```

2. Install dependencies using `uv`:
```bash
make install
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:

### Required Environment Variables

- `UP_TOKEN` - Your Up Banking API token
  - Obtain from: Up Banking app → Settings → API

- `ACTUAL__URL` - Your Actual Budget server URL
  - Example: `https://actual.yourdomain.com` or `http://localhost:5006`

- `ACTUAL__PASSWORD` - Your Actual Budget password
  - The password you use to log in to Actual Budget

- `ACTUAL__ENCRYPTION_PASSWORD` - Your Actual Budget file encryption password
  - Set when creating your budget file in Actual Budget

- `ACTUAL__FILE` - Your Actual Budget file name
  - Example: `My Budget` (the name shown in Actual Budget)

## Usage

### Basic Usage

Sync transactions from the last 30 days:
```bash
uv run python -m up.app reconcile
```

### Advanced Usage

Specify a custom start date:
```bash
# Sync from a specific date
uv run python -m up.app reconcile --start-date 2025-01-01

# Sync from 90 days ago
uv run python -m up.app reconcile --days-back 90

# Customize page size for API calls
uv run python -m up.app reconcile --page-size 50
```

### CLI Options

- `--start-date TEXT` - Start date in ISO format (YYYY-MM-DD). Overrides `--days-back`
- `--days-back INTEGER` - Number of days back from today to sync (default: 30)
- `--page-size INTEGER` - Number of transactions per API request (default: 100)
- `--help` - Show help message

## Development

### Setup

```bash
make install
```

### Running Tests

```bash
# Run unit tests (excluding integration/schema tests)
make test

# Run all tests
make test-all
```

### Code Quality

```bash
# Format and lint
make format

# Format, lint, and type check
make check

# Type check only
make pyright
```

## Troubleshooting

### Common Issues

**"UP_TOKEN environment variable is not set"**
- Ensure your `.env` file exists and contains `UP_TOKEN`
- Check that `python-dotenv` is loading the file correctly

**"Connection refused" to Actual Budget**
- Verify your `ACTUAL__URL` is correct
- Ensure your Actual Budget server is running
- Check firewall/network settings

**"File encryption password incorrect"**
- Verify `ACTUAL__ENCRYPTION_PASSWORD` matches your budget file's encryption password
- Try re-entering the password in Actual Budget to confirm it

## Licence

See repository for licence information.
