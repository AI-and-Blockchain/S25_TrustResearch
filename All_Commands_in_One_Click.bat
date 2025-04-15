@echo off
setlocal

echo Starting IPFS...
start powershell -NoExit -Command "ipfs daemon"
timeout /t 1 > nul

echo Starting Ganache...
start powershell -NoExit -Command "ganache-cli --port 7545 --deterministic"
timeout /t 1 > nul

echo Migrating Truffle contracts...
start powershell -NoExit -Command "cd 'Codes/blockchain'; timeout /t 4; truffle migrate --reset"
timeout /t 1 > nul

echo Starting backend server...
start powershell -NoExit -Command "cd 'Codes/backend'; python server.py"
timeout /t 1 > nul

echo Starting journal receiver...
start powershell -NoExit -Command "cd 'Codes/journal_receiver'; python journal_receiver.py"
timeout /t 1 > nul

echo Starting author frontend...
start powershell -NoExit -Command "cd 'Codes/frontend/author'; npm start"
timeout /t 1 > nul

echo Starting reviewer frontend on port 3001...
start powershell -NoExit -Command "cd 'Codes/frontend/reviewer'; $env:PORT=3001; npm start"

endlocal
exit
