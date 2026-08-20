// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract EvidenceRegistry {

    struct Evidence {
        string evidenceId;
        string caseId;
        string evidenceHash;
        string investigatorId;
        uint256 timestamp;
        bool registered;
    }

    mapping(string => Evidence) private evidenceRecords;

    event EvidenceRegistered(
        string evidenceId,
        string caseId,
        string evidenceHash,
        string investigatorId,
        uint256 timestamp
    );

    function registerEvidence(
        string memory _evidenceId,
        string memory _caseId,
        string memory _evidenceHash,
        string memory _investigatorId
    ) public {

        require(
            !evidenceRecords[_evidenceId].registered,
            "Evidence already registered"
        );

        evidenceRecords[_evidenceId] = Evidence({
            evidenceId: _evidenceId,
            caseId: _caseId,
            evidenceHash: _evidenceHash,
            investigatorId: _investigatorId,
            timestamp: block.timestamp,
            registered: true
        });

        emit EvidenceRegistered(
            _evidenceId,
            _caseId,
            _evidenceHash,
            _investigatorId,
            block.timestamp
        );
    }

    function getEvidence(
        string memory _evidenceId
    )
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            uint256,
            bool
        )
    {
        Evidence memory evidence = evidenceRecords[_evidenceId];

        return (
            evidence.evidenceId,
            evidence.caseId,
            evidence.evidenceHash,
            evidence.investigatorId,
            evidence.timestamp,
            evidence.registered
        );
    }
}