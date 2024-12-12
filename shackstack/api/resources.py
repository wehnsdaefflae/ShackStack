from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from web3.types import Address
from eth_utils import is_address

from shackstack.core.resource_manager import ResourceManager
from shackstack.api.dependencies import get_resource_manager

router = APIRouter(
    prefix="/resources",
    tags=["resources"]
)


class ResourceCreate(BaseModel):
    data: Dict[str, Any]
    owner_address: str
    encrypt: bool = True


class ResourceUpdate(BaseModel):
    is_available: bool
    owner_address: str


class ResourceResponse(BaseModel):
    cid: str
    status: Dict[str, Any]


@router.post("/", response_model=ResourceResponse)
async def create_resource(
        resource: ResourceCreate,
        resource_manager: ResourceManager = Depends(get_resource_manager)
):
    """Create a new resource."""
    if not is_address(resource.owner_address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")

    try:
        cid = await resource_manager.store_resource(
            resource.data,
            Address(bytes.fromhex(resource.owner_address[2:])),
            resource.encrypt
        )

        status = await resource_manager.get_resource_status(cid)

        return ResourceResponse(cid=cid, status=status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{cid}", response_model=Dict[str, Any])
async def get_resource(
        cid: str,
        decrypt: bool = True,
        resource_manager: ResourceManager = Depends(get_resource_manager)
):
    """Get resource data by CID."""
    try:
        return await resource_manager.get_resource(cid, decrypt)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{cid}/status")
async def update_resource_status(
        cid: str,
        update: ResourceUpdate,
        resource_manager: ResourceManager = Depends(get_resource_manager)
):
    """Update resource availability status."""
    if not is_address(update.owner_address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")

    try:
        await resource_manager.update_resource_status(
            cid,
            update.is_available,
            Address(bytes.fromhex(update.owner_address[2:]))
        )
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
async def list_resources(
        resource_manager: ResourceManager = Depends(get_resource_manager)
):
    """List all resources."""
    try:
        return await resource_manager.list_resources()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))