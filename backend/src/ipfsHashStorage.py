import os
import json
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
import time

# Load environment variables from .env file
load_dotenv()

def connect_to_quicknode(url):
    """
    Establishes a connection to QuickNode.

    Args:
        url (str): QuickNode API URL.

    Returns:
        web3 (Web3): Web3 object connected to QuickNode.
    """
    web3 = Web3(Web3.HTTPProvider(url))
    try:
        web3.eth.get_block('latest')
        print("Successfully connected to QuickNode.")
        return web3
    except Exception as e:
        raise Exception("Failed to connect to QuickNode: " + str(e))

def create_contract(web3, contract_address, contract_abi):
    """
    Creates a contract object.

    Args:
        web3 (Web3): Web3 object connected to QuickNode.
        contract_address (str): Deployed contract address.
        contract_abi (list): Contract ABI.

    Returns:
        contract (Contract): Contract object.
    """
    return web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)

def set_ipfs_hash(web3, contract, account_address, private_key, ipfs_hash):
    """
    Sets the IPFS hash in the contract.

    Args:
        web3 (Web3): Web3 object.
        contract (Contract): Contract object.
        account_address (str): Account address.
        private_key (str): Account private key.
        ipfs_hash (str): IPFS hash to store.

    Returns:
        txn_hash (str): Transaction hash.
    """
    nonce = web3.eth.get_transaction_count(account_address, 'pending')
    gas_price = web3.eth.gas_price  # Dynamic gas price based on network

    transaction = contract.functions.setIPFSHash(ipfs_hash).build_transaction({
        'chainId': 11155111,  # Sepolia Chain ID (use appropriate chainId for your network)
        'gas': 2000000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    # Sign the transaction
    signed_txn = Account.sign_transaction(transaction, private_key)

    # Send the transaction
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f'Transaction sent! Hash: {txn_hash.hex()}')

    # Wait for transaction to be mined
    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(f'Transaction mined! Block hash: {txn_receipt.blockHash.hex()}')
    return txn_hash.hex()

def get_ipfs_hash(contract, id):
    """
    Retrieves the IPFS hash for the given ID.

    Args:
        contract (Contract): Contract object.
        id (int): The ID of the IPFS hash to retrieve.

    Returns:
        str: The IPFS hash associated with the ID.
    """
    assert web3.is_connected()
    print("Web3 connected:", web3.is_connected())
    retries = 5
    while retries > 0:
        try:
            ipfs_hash = contract.functions.getIPFSHash(id).call()
            return ipfs_hash
        except Exception as e:
            print(f"Error calling getIPFSHash: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            retries -= 1
    raise Exception("Failed to retrieve IPFS hash after multiple retries.")

if __name__ == "__main__":
    quicknode_url = 'https://falling-cold-hill.ethereum-sepolia.quiknode.pro/bdf16ba5a5f2397e35047a0bbc33d51c95907d2e/'  # Replace with your QuickNode URL
    contract_address = os.getenv("CONTRACT_ADDRESS")
    private_key = os.getenv("METAMASK_PRIVATE_KEY")
    account_address = os.getenv("METAMASK_ACCOUNT_ADDRESS")
    contract_abi = [
        {
            "inputs": [
                {
                    "internalType": "string",
                    "name": "_ipfsHash",
                    "type": "string"
                }
            ],
            "name": "setIPFSHash",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "currentId",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "id",
                    "type": "uint256"
                }
            ],
            "name": "getIPFSHash",
            "outputs": [
                {
                    "internalType": "string",
                    "name": "",
                    "type": "string"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "name": "ipfsHashes",
            "outputs": [
                {
                    "internalType": "string",
                    "name": "",
                    "type": "string"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]

    # Connect to the network
    web3 = connect_to_quicknode(quicknode_url)
    contract = create_contract(web3, contract_address, contract_abi)

    # Example IPFS hash
    ipfs_hash = "QmQkx1tEbmhuy4WSFLpEbgTx8Bjd2XivWADEpczgzcSKem"
    # Set the IPFS hash
    # txn_hash = set_ipfs_hash(web3, contract, account_address, private_key, ipfs_hash)
    
    # Retrieve the IPFS hash for a specific ID (e.g., 0)
    retrieved_hash = get_ipfs_hash(contract, 1)
    print(f'Retrieved IPFS Hash: {retrieved_hash}')
