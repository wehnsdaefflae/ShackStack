import json
import os
from web3 import Web3
from web3.contract import Contract


def get_contract_abi() -> dict:
    """Load contract ABI from JSON file."""
    abi_path = os.path.join(
        os.path.dirname(__file__),
        'artifacts',
        'ResourceMapping.json'
    )

    with open(abi_path) as f:
        contract_json = json.load(f)
    return contract_json['abi']


def get_contract_address() -> str:
    """Get deployed contract address from environment variable."""
    return os.getenv('RESOURCE_CONTRACT_ADDRESS')


def get_resource_contract(w3: Web3) -> Contract:
    """
    Get Web3 contract instance for ResourceMapping.

    Args:
        w3: Web3 instance

    Returns:
        Contract instance
    """
    abi = get_contract_abi()
    address = get_contract_address()

    if not address:
        raise ValueError(
            "Contract address not found. "
            "Set RESOURCE_CONTRACT_ADDRESS environment variable."
        )

    return w3.eth.contract(
        address=Web3.to_checksum_address(address),
        abi=abi
    )