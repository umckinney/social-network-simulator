# Social Network Simulator

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Test Coverage](https://img.shields.io/badge/coverage->85%25-brightgreen.svg)](https://github.com/your-username/social-network-simulator/actions)
![Last Updated](https://img.shields.io/badge/last%20updated-September%202025-orange)
![Made with ❤️](https://img.shields.io/badge/made%20with-%E2%9D%A4-red)

---

## Overview

Social Network Simulator is a layered, test-driven CLI + API project built in Python 3.12 to model a lightweight social networking platform. It supports user, status, and picture records, tag-based reconciliation, and exposes a RESTful API using Flask.

This project complements the [Architecture Documentation](architecture.md), which provides detailed breakdowns of layers, responsibilities, and test coverage.

---

## Features

- Command-line and web-based (REST API) interfaces
- CRUD for Users and Statuses
- Picture read/reconcile support via tag-driven folder structure
- Cascading deletes (e.g., delete user → delete associated statuses and pictures)
- Structured logging with Loguru
- Validation layer with normalization and field checks
- JSON/CSV import-export support

---

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/your-username/social-network-simulator.git
cd social-network-simulator
```

2. Set up a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Launch the CLI interface:

```bash
python menu.py
```

4. Launch the API server:

```bash
python api.py
```

---

## Testing

This project uses `unittest` with >85% test coverage. Run all tests with:

```bash
python -m unittest discover tests
```

---

## Technologies Used

- Python 3.12
- Dataset (SQLite wrapper)
- Flask + Flask-RESTful
- Loguru (logging)
- Unittest + Mock
- Email-validator

---

## License

This project is licensed under the MIT License.
