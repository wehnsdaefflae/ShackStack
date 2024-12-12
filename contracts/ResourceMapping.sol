// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ResourceMapping {
    struct Resource {
        bytes32 ipfsHash;
        address owner;
        bool isAvailable;
        uint256 timestamp;
        string metadata;
    }

    mapping(bytes32 => Resource) public resources;
    bytes32[] public resourceList;

    event ResourceAdded(bytes32 indexed ipfsHash, address indexed owner);
    event ResourceUpdated(bytes32 indexed ipfsHash, bool isAvailable);

    modifier onlyResourceOwner(bytes32 _ipfsHash) {
        require(resources[_ipfsHash].owner == msg.sender, "Not the resource owner");
        _;
    }

    function addResource(bytes32 _ipfsHash, string memory _metadata) public {
        require(resources[_ipfsHash].timestamp == 0, "Resource already exists");

        resources[_ipfsHash] = Resource({
            ipfsHash: _ipfsHash,
            owner: msg.sender,
            isAvailable: true,
            timestamp: block.timestamp,
            metadata: _metadata
        });

        resourceList.push(_ipfsHash);
        emit ResourceAdded(_ipfsHash, msg.sender);
    }

    function updateResourceStatus(bytes32 _ipfsHash, bool _isAvailable)
        public
        onlyResourceOwner(_ipfsHash)
    {
        resources[_ipfsHash].isAvailable = _isAvailable;
        emit ResourceUpdated(_ipfsHash, _isAvailable);
    }

    function getResource(bytes32 _ipfsHash)
        public
        view
        returns (
            address owner,
            bool isAvailable,
            uint256 timestamp,
            string memory metadata
        )
    {
        Resource memory resource = resources[_ipfsHash];
        return (
            resource.owner,
            resource.isAvailable,
            resource.timestamp,
            resource.metadata
        );
    }

    function getResourceCount() public view returns (uint256) {
        return resourceList.length;
    }

    function getResourceAtIndex(uint256 _index) public view returns (bytes32) {
        require(_index < resourceList.length, "Index out of bounds");
        return resourceList[_index];
    }
}