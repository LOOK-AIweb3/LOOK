// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title AdvancedContract
 * @dev Demonstrates advanced Solidity programming patterns including:
 * - Role-based access control
 * - Pausable operations
 * - Time-locked functions
 * - Event tracking
 * - Governance features
 */
contract AdvancedContract is Pausable, AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    // Time-lock duration for sensitive operations
    uint256 public constant TIMELOCK_DURATION = 2 days;
    uint256 public nextOperationTime;

    // Struct to demonstrate complex data handling
    struct Operation {
        bytes32 operationHash;
        address executor;
        uint256 timestamp;
        bool completed;
    }

    // Mapping to track operations
    mapping(bytes32 => Operation) public operations;

    // Events for operation tracking
    event OperationScheduled(bytes32 indexed operationHash, address indexed executor, uint256 timestamp);
    event OperationExecuted(bytes32 indexed operationHash, address indexed executor, uint256 timestamp);
    event GovernanceProposalCreated(uint256 indexed proposalId, address creator, string description);
    event GovernanceVoteCast(uint256 indexed proposalId, address voter, bool support);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);

        nextOperationTime = block.timestamp;
    }

    /**
     * @dev Pause all contract operations
     * Requirements:
     * - Caller must have ADMIN_ROLE
     */
    function pause() public onlyRole(ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Resume all contract operations
     * Requirements:
     * - Caller must have ADMIN_ROLE
     */
    function unpause() public onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Schedule a new operation
     * @param operationData The data of the operation to be scheduled
     */
    function scheduleOperation(bytes memory operationData) public onlyRole(OPERATOR_ROLE) whenNotPaused {
        bytes32 operationHash = keccak256(abi.encodePacked(operationData, block.timestamp));
        require(operations[operationHash].executor == address(0), "Operation already scheduled");

        operations[operationHash] = Operation({
            operationHash: operationHash,
            executor: msg.sender,
            timestamp: block.timestamp + TIMELOCK_DURATION,
            completed: false
        });

        emit OperationScheduled(operationHash, msg.sender, block.timestamp);
    }

    /**
     * @dev Execute a scheduled operation
     * @param operationHash The hash of the operation to execute
     */
    function executeOperation(bytes32 operationHash) public onlyRole(OPERATOR_ROLE) whenNotPaused {
        Operation storage operation = operations[operationHash];
        require(operation.executor != address(0), "Operation does not exist");
        require(!operation.completed, "Operation already completed");
        require(block.timestamp >= operation.timestamp, "Operation is time-locked");

        operation.completed = true;
        emit OperationExecuted(operationHash, msg.sender, block.timestamp);
    }

    /**
     * @dev Create a new governance proposal
     * @param description Description of the proposal
     */
    function createProposal(string memory description) public onlyRole(GOVERNANCE_ROLE) returns (uint256) {
        uint256 proposalId = uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender, description)));
        emit GovernanceProposalCreated(proposalId, msg.sender, description);
        return proposalId;
    }

    /**
     * @dev Cast a vote on a governance proposal
     * @param proposalId ID of the proposal
     * @param support Whether to support the proposal
     */
    function castVote(uint256 proposalId, bool support) public whenNotPaused {
        require(hasRole(GOVERNANCE_ROLE, msg.sender), "Must have governance role to vote");
        emit GovernanceVoteCast(proposalId, msg.sender, support);
    }

    /**
     * @dev Hook that is called before any operation
     */
    function _beforeOperation(
        address operator,
        bytes32 operationHash
    ) internal virtual whenNotPaused {
        require(hasRole(OPERATOR_ROLE, operator), "Caller must be an operator");
        require(block.timestamp >= nextOperationTime, "Operation too soon");
        nextOperationTime = block.timestamp + 1 hours;
    }
}