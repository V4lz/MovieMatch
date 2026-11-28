# MovieMatch


## Requirements

- Python 3.11
- Docker Desktop
- MongoDB Atlas account

### Python compatibility

Python 3.11 is recommended for this project because the Cassandra driver requires compatibility with the `asyncore` module, which was removed in Python 3.12.

### Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install all project dependencies:

```bash
pip install -r requirements.txt
```
