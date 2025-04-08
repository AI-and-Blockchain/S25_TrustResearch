@echo off
echo Starting IPFS Daemon...
start powershell -NoExit -Command "ipfs daemon"

echo Starting Ganache CLI...
start powershell -NoExit -Command "ganache-cli --port 7545 --deterministic"

echo Running Truffle Migrations...
start powershell -NoExit -Command "cd Codes/blockchain; truffle migrate --reset"

echo Starting Backend Server...
start powershell -NoExit -Command "cd Codes/backend; python server.py"

echo Starting Journal Receiver...
start powershell -NoExit -Command "cd Codes/journal_receiver; python journal_receiver.py"

echo Starting Frontend...
start powershell -NoExit -Command "cd Codes/frontend; npm start"

echo All processes started.
pause
