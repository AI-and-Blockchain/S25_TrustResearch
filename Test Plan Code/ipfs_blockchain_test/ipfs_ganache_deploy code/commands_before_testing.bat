@echo off

REM Start IPFS daemon in a new PowerShell window
start powershell -NoExit -Command "ipfs daemon"

REM Start Ganache CLI in another PowerShell window
start powershell -NoExit -Command "ganache-cli --port 7545 --deterministic"

REM Wait for 4 seconds before starting Truffle
timeout /t 4 /nobreak >nul

REM Start Truffle migrate in a third PowerShell window
start powershell -NoExit -Command "cd Codes/blockchain; truffle migrate --reset"
