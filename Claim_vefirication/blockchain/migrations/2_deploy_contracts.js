const FileStorage = artifacts.require("FileStorage");
const fs = require("fs");

module.exports = async function (deployer, network, accounts) {
    await deployer.deploy(FileStorage);
    const contractInstance = await FileStorage.deployed();

    const contractData = {
        address: contractInstance.address,
        abi: contractInstance.abi
    };

    fs.writeFileSync("../backend/contract_data.json", JSON.stringify(contractData, null, 2));

    console.log("✅ Contract deployed!");
    console.log("📍 Address:", contractInstance.address);
};
