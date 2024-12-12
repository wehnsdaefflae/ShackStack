from functools import lru_cache
from typing import Generator
import os

from shackstack.core.resource_manager import ResourceManager

@lru_cache()
def get_settings():
    """Get application settings."""
    return {
        'web3_provider': os.getenv('WEB3_PROVIDER_URI', 'http://localhost:8545'),
        'ipfs_host': os.getenv('IPFS_HOST', '/ip4/127.0.0.1/tcp/5001'),
        'encryption_key': os.getenv('ENCRYPTION_KEY', None)
    }

def get_resource_manager() -> Generator[ResourceManager, None, None]:
    """FastAPI dependency for ResourceManager."""
    settings = get_settings()
    manager = ResourceManager(
        web3_provider=settings['web3_provider'],
        ipfs_host=settings['ipfs_host'],
        encryption_key=settings['encryption_key']
    )
    try:
        yield manager
    finally:
        manager.close()