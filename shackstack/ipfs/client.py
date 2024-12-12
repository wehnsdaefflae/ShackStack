import ipfshttpclient
from typing import Union, Dict, Any
import json
import asyncio
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def async_wrap(func):
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return run


class IPFSClient:
    def __init__(self, host: str = '/ip4/127.0.0.1/tcp/5001'):
        """Initialize IPFS client with host address."""
        self.client = ipfshttpclient.connect(host)
        logger.info(f"Connected to IPFS node at {host}")

    async def add_json(self, data: Union[Dict[str, Any], str]) -> str:
        """
        Add JSON data to IPFS.

        Args:
            data: Dictionary or JSON string to store

        Returns:
            IPFS CID (Content Identifier)
        """
        if isinstance(data, dict):
            data = json.dumps(data)

        @async_wrap
        def _add(data):
            return self.client.add_json(data)

        try:
            cid = await _add(data)
            logger.info(f"Added data to IPFS with CID: {cid}")
            return cid
        except Exception as e:
            logger.error(f"Failed to add data to IPFS: {str(e)}")
            raise

    async def get_json(self, cid: str) -> Union[Dict[str, Any], str]:
        """
        Retrieve JSON data from IPFS.

        Args:
            cid: IPFS Content Identifier

        Returns:
            Retrieved data as dictionary or string
        """

        @async_wrap
        def _get(cid):
            return self.client.get_json(cid)

        try:
            data = await _get(cid)
            logger.info(f"Retrieved data from IPFS with CID: {cid}")
            return data
        except Exception as e:
            logger.error(f"Failed to get data from IPFS: {str(e)}")
            raise

    async def pin_add(self, cid: str) -> None:
        """
        Pin content to ensure it's kept in the local node.

        Args:
            cid: IPFS Content Identifier
        """

        @async_wrap
        def _pin(cid):
            return self.client.pin.add(cid)

        try:
            await _pin(cid)
            logger.info(f"Pinned content with CID: {cid}")
        except Exception as e:
            logger.error(f"Failed to pin content: {str(e)}")
            raise

    def close(self):
        """Close the IPFS client connection."""
        try:
            self.client.close()
            logger.info("Closed IPFS client connection")
        except Exception as e:
            logger.error(f"Error closing IPFS client: {str(e)}")
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()