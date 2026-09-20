# Raspberry Pi Deployment

Deploy this repository with a dedicated service account, a repository-local virtual environment, writable `data/database` and `data/recordings` directories, and a system service invoking `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000`. The local service must start without internet, map, routing or browser availability.

Before real radar mode, verify the actual serial device, permissions, purchased LD2450 documentation and reviewed binary parser. The V2-approved physical serial settings are 256000 baud, 8 data bits, no parity and 1 stop bit. This document does not specify connector orientation or voltage.

