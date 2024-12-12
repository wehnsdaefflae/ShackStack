import json
import os
from web3 import Web3
from eth_account import Account
import solcx

# Install specific solc version
SOLC_VERSION = '0.8.17'
solcx.install_solc(SOLC_VERSION)


def compile_contract():
    """Compile the ResourceMapping contract."""
    contract_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'contracts',
        'ResourceMapping.sol'
    )

    # Compile contract
    compiled_sol = solcx.compile_files(
        [contract_path],
        output_values=['abi', 'bin'],
        solc_version=SOLC_VERSION
    )

    contract_id = f"{contract_path}:ResourceMapping"
    contract_interface = compiled_sol[contract_id]

    # Save ABI
    artifacts_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        'shackstack',
        'contracts',
        'artifacts'
    )
    os.makedirs(artifacts_dir, exist_ok=True)

    with open(os.path.join(artifacts_dir, 'ResourceMapping.json'), 'w') as f:
        json.dump(
            {
                'abi': contract_interface['abi'],
                'bytecode': contract_interface['bin']
            },
            f,
            indent=2
        )

    return contract_interface


def deploy_contract(w3: Web3, contract_interface: dict):
    """Deploy the contract to the blockchain."""
    # Get deployment account
    private_key = os.getenv('DEPLOYER_PRIVATE_KEY')
    if not private_key:
        raise ValueError(
            "Deployer private key not found. "
            "Set DEPLOYER_PRIVATE_KEY environment variable."
        )

    account = Account.from_key(private_key)

    # Create contract instance
    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )

    # Build transaction
    transaction = contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
    })

    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(
        transaction,
        private_key=private_key
    )
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress


def main():
    """Main deployment function."""
    # Connect to local node
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

    if not w3.is_connected():
        raise ConnectionError("Could not connect to Ethereum node")

    print("Connected to Ethereum node")

    # Compile contract
    print("Compiling contract...")
    contract_interface = compile_contract()

    # Deploy contract
    print("Deploying contract...")
    contract_address = deploy_contract(w3, contract_interface)

    print(f"Contract deployed at: {contract_address}")

    # Save address to .env file
    with open('.env', 'a') as f:
        f.write(f"\nRESOURCE_CONTRACT_ADDRESS={contract_address}")


if __name__ == '__main__':
    main()