from typing import Dict, Any, List, Optional
from web3 import Web3
from eth_typing import Address
import json

from shackstack.ipfs.client import IPFSClient
from shackstack.crypto.utils import CryptoManager
from shackstack.contracts import get_resource_contract


class ResourceManager:
    def __init__(
            self,
            web3_provider: str = "http://localhost:8545",
            ipfs_host: str = '/ip4/127.0.0.1/tcp/5001',
            encryption_key: Optional[str] = None
    ):
        """
        Initialize ResourceManager with Web3, IPFS, and encryption setup.

        Args:
            web3_provider: Web3 provider URL
            ipfs_host: IPFS node address
            encryption_key: Optional base64 encoded encryption key
        """
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract = get_resource_contract(self.w3)

        # Initialize IPFS client
        self.ipfs_client = IPFSClient(ipfs_host)

        # Initialize encryption
        self.crypto = CryptoManager.from_key_b64(encryption_key) if encryption_key else CryptoManager()

    async def store_resource(
            self,
            resource_data: Dict[str, Any],
            owner_address: Address,
            encrypt: bool = True
    ) -> str:
        """
        Store resource data on IPFS and register on blockchain.

        Args:
            resource_data: Resource data to store
            owner_address: Ethereum address of resource owner
            encrypt: Whether to encrypt the data

        Returns:
            IPFS CID of stored resource
        """
        # Encrypt if requested
        if encrypt:
            resource_data = self.crypto.encrypt(resource_data)

        # Store on IPFS
        cid = await self.ipfs_client.add_json(resource_data)

        # Register on blockchain
        ipfs_hash = Web3.keccak(text=cid)
        metadata = json.dumps({"encrypted": encrypt})

        tx_hash = self.contract.functions.addResource(
            ipfs_hash,
            metadata
        ).transact({'from': owner_address})

        # Wait for transaction
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return cid

    async def get_resource(
            self,
            cid: str,
            decrypt: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve resource data from IPFS.

        Args:
            cid: IPFS Content Identifier
            decrypt: Whether to decrypt the data

        Returns:
            Resource data
        """
        # Get from IPFS
        data = await self.ipfs_client.get_json(cid)

        # Decrypt if needed
        if decrypt:
            try:
                data = self.crypto.decrypt(data)
            except ValueError:
                # If decryption fails, return raw data
                pass

        return data

    async def update_resource_status(
            self,
            cid: str,
            is_available: bool,
            owner_address: Address
    ) -> None:
        """
        Update resource availability status.

        Args:
            cid: IPFS Content Identifier
            is_available: New availability status
            owner_address: Ethereum address of resource owner
        """
        ipfs_hash = Web3.keccak(text=cid)

        tx_hash = self.contract.functions.updateResourceStatus(
            ipfs_hash,
            is_available
        ).transact({'from': owner_address})

        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all resources.

        Returns:
            List of resource data
        """
        count = self.contract.functions.getResourceCount().call()
        resources = []

        for i in range(count):
            ipfs_hash = self.contract.functions.getResourceAtIndex(i).call()
            resource_data = self.contract.functions.getResource(ipfs_hash).call()

            resources.append({
                'ipfs_hash': ipfs_hash.hex(),
                'owner': resource_data[0],
                'is_available': resource_data[1],
                'timestamp': resource_data[2],
                'metadata': json.loads(resource_data[3])
            })

        return resources

    async def get_resource_status(self, cid: str) -> Dict[str, Any]:
        """
        Get resource status from blockchain.

        Args:
            cid: IPFS Content Identifier

        Returns:
            Resource status data
        """
        ipfs_hash = Web3.keccak(text=cid)
        resource_data = self.contract.functions.getResource(ipfs_hash).call()

        return {
            'owner': resource_data[0],
            'is_available': resource_data[1],
            'timestamp': resource_data[2],
            'metadata': json.loads(resource_data[3])
        }

    def close(self):
        """Close connections."""
        self.ipfs_client.close()