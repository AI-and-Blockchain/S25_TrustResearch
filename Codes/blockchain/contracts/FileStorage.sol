// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileStorage {
    struct FileData {
        string ipfsHash;
        string fileName;
        address uploader;
    }

    mapping(address => FileData[]) public userFiles;

    event FileUploaded(address indexed uploader, string ipfsHash, string fileName);

    function storeFile(string memory _ipfsHash, string memory _fileName) public {
        userFiles[msg.sender].push(FileData(_ipfsHash, _fileName, msg.sender));
        emit FileUploaded(msg.sender, _ipfsHash, _fileName);
    }

    function getFiles(address _user) public view returns (FileData[] memory) {
        return userFiles[_user];
    }
}
