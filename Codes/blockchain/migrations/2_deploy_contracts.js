const fs = require('fs');
const path = require('path');
const FileStorage = artifacts.require("FileStorage");
const ReviewFeedbackTracker = artifacts.require("ReviewFeedbackTracker");

module.exports = async function (deployer) {
  await deployer.deploy(FileStorage);
  const fileStorage = await FileStorage.deployed();

  await deployer.deploy(ReviewFeedbackTracker);
  const feedbackTracker = await ReviewFeedbackTracker.deployed();

  // Save FileStorage metadata
  const fileStorageData = {
    contractName: "FileStorage",
    abi: fileStorage.abi,
    address: fileStorage.address
  };
  fs.writeFileSync(
    path.resolve(__dirname, "../../backend/contract_data.json"),
    JSON.stringify(fileStorageData, null, 2)
  );

  // Save ReviewFeedbackTracker metadata
  const feedbackData = {
    contractName: "ReviewFeedbackTracker",
    abi: feedbackTracker.abi,
    address: feedbackTracker.address
  };
  fs.writeFileSync(
    path.resolve(__dirname, "../../backend/feedback_contract_data.json"),
    JSON.stringify(feedbackData, null, 2)
  );
};
