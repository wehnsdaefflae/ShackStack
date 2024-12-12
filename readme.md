# ShackStack Proof of Concept

ShackStack is a decentralized infrastructure for secure community resource coordination. This proof of concept demonstrates the core functionality of decentralized space mapping using IPFS and basic smart contracts.

## Features

- Decentralized resource mapping using IPFS
- Basic end-to-end encryption for sensitive data
- Smart contracts for resource management (testnet only)
- Async API with FastAPI

## Technical Stack

- Python 3.11+
- IPFS (via py-ipfs-http-client) for decentralized storage
- Web3.py for Ethereum integration
- FastAPI for backend API
- Vue.js for frontend
- PyNaCl for encryption
- Docker & Kubernetes for deployment

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/shackstack-poc
cd shackstack-poc

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start local IPFS node
ipfs daemon

# Deploy smart contracts (requires local Ethereum node)
python scripts/deploy.py

# Start development server
uvicorn shackstack.main:app --reload
```

## Project Structure

```
├── shackstack/
│   ├── api/                # FastAPI routes
│   ├── core/               # Core business logic
│   ├── ipfs/              # IPFS integration
│   ├── crypto/            # Encryption utilities
│   └── contracts/         # Smart contract integration
├── contracts/             # Solidity contracts
├── alembic/              # Database migrations
├── tests/                # Test suite
└── scripts/              # Deployment scripts
```

## Smart Contracts

The current implementation includes a basic resource management contract:

```solidity
// Simplified example
contract ResourceMapping {
    struct Resource {
        bytes32 ipfsHash;
        address owner;
        bool isAvailable;
    }
    
    mapping(bytes32 => Resource) public resources;
    
    function addResource(bytes32 _ipfsHash) public {
        resources[_ipfsHash] = Resource(_ipfsHash, msg.sender, true);
    }
}
```

## IPFS Integration

Resources are stored on IPFS with basic encryption:

```python
from shackstack.crypto import encrypt
from shackstack.ipfs import ipfs_client

async def store_resource(resource: dict) -> str:
    """Store encrypted resource on IPFS."""
    encrypted = encrypt(json.dumps(resource))
    cid = await ipfs_client.add(encrypted)
    return str(cid)
```

## API Examples

```python
from fastapi import FastAPI, HTTPException
from shackstack.core import ResourceManager

app = FastAPI()
resource_manager = ResourceManager()

@app.post("/resources/")
async def create_resource(resource: ResourceCreate):
    try:
        cid = await resource_manager.store_resource(resource)
        return {"cid": cid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Development Status

This proof of concept demonstrates:
- ✅ Basic IPFS resource mapping
- ✅ Smart contract integration
- ✅ Basic encryption
- ✅ Async API endpoints

Planned for the future:
- 🚧 End-to-end encryption
- 🚧 Zero-knowledge identity management
- 🚧 Matrix protocol integration
- 🚧 Community features

## Requirements

```txt
fastapi>=0.75.0
pynacl>=1.5.0
web3>=6.0.0
py-ipfs-http-client>=0.8.0
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
uvicorn>=0.17.0
```

## Security Notice

This is a proof of concept. Do not use in production. The current implementation includes basic encryption but is not yet suitable for sensitive data.

## Contributing

TODO

## License

MIT

## Contact

For questions about the proof of concept, please open an issue on GitHub.
