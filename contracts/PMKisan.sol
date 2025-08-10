// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PMKisanRegistry {
    struct Record {
        string databaseCID;
        string explanationCID;
        string decision;
        uint256 participantId;
    }

    mapping(address => Record[]) public records;

    function storeDecision(
        string memory _databaseCID,
        string memory _explanationCID,
        string memory _decision,
        uint256 _participantId
    ) public {
        records[msg.sender].push(
            Record(_databaseCID, _explanationCID, _decision, _participantId)
        );
    }

    function getRecordCount(address user) public view returns (uint256) {
        return records[user].length;
    }

    function getRecord(address user, uint index) public view returns (
        string memory, string memory, string memory, uint256
    ) {
        Record memory r = records[user][index];
        return (r.databaseCID, r.explanationCID, r.decision, r.participantId);
    }
}
