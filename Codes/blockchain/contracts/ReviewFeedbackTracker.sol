// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReviewFeedbackTracker {
    struct Feedback {
        string ipfsHash;
        string fileName;
        address reviewer;
        uint timestamp;
    }

    Feedback[] public feedbacks;

    event FeedbackSubmitted(address indexed reviewer, string ipfsHash, string fileName, uint timestamp);

    function submitFeedback(string memory _ipfsHash, string memory _fileName) public {
        feedbacks.push(Feedback(_ipfsHash, _fileName, msg.sender, block.timestamp));
        emit FeedbackSubmitted(msg.sender, _ipfsHash, _fileName, block.timestamp);
    }

    function getAllFeedbacks() public view returns (Feedback[] memory) {
        return feedbacks;
    }
}
