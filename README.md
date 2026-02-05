# Blockchain Project

## Overview

This project implements a simplified blockchain network using Python and Flask. Each node in the network can register new transactions, mine blocks, synchronize with other nodes, resolve conflicts, and perform periodic backups. It also supports monitoring of network status through custom endpoints.

## Features

* Transaction handling through REST API.
* Mining blocks with proof-of-work.
* Node registration and consensus algorithm for conflict resolution.
* Blockchain synchronization and backup.
* Network health check via PING/PONG mechanism.
* Node system diagnostics endpoint.

## Directory Structure

```
Blockchain_project/
├── Blockchain_app.py          # Main Flask application and API endpoints
├── Blockchain.py              # Blockchain and Block class definitions
├── pruebas_requests.py        # Automated testing script using requests
├── requirements.txt           # Python dependencies
├── respaldo-nodoX.json        # Periodic blockchain backups per node
├── README.md                  # This file
```

## Setup and Installation

1. **Clone the repository**

```bash
git clone https://github.com/Ulisesdz/BlockChain_Project.git
cd Blockchain_project
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run a node (example with port 5000)**

```bash
python Blockchain_app.py -p 5000
```

4. **Run multiple nodes on different ports** to simulate a network.

## API Endpoints

### Transactions

* `POST /transacciones/nueva`

  * Create a new transaction
  * JSON: `{ "origen": "X", "destino": "Y", "cantidad": 10 }`

### Blockchain

* `GET /chain`

  * Retrieve full blockchain
* `GET /minar`

  * Mine a new block if transactions exist

### Node Management

* `POST /nodos/registrar`

  * Register new nodes and propagate blockchain
* `POST /nodos/registro_simple`

  * Receive and synchronize blockchain from a peer

### System & Network

* `GET /system`

  * Get node system details
* `GET /ping`

  * Ping network peers
* `POST /pong`

  * Handle ping and respond with delay

### Backup

* `GET /respaldo`

  * Initiates automatic blockchain backup every 60s (runs in background thread)

## Testing

Run the following to simulate API calls:

```bash
python pruebas_requests.py
```

This script tests transactions, mining, node registration, consensus conflict resolution, and PING/PONG interaction.

## Dependencies

Ensure the following packages are installed:

```
Flask
requests
```

Install via:

```bash
pip install -r requirements.txt
```

## Notes

* All nodes must be run locally on different ports (e.g., 5000, 5001, 5002).
* Blockchain backups are stored as `respaldo-nodo<ip>-<port>.json`.
* Use `curl` or Postman to interact with endpoints manually.

For any inquiries, please do not hesitate in contacting.

