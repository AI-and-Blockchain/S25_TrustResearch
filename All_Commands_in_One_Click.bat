@echo off

echo Starting IPFS Daemon...
start powershell -NoExit -Command "ipfs daemon"
timeout /t 1 > nul

echo Starting Ganache CLI...
start powershell -NoExit -Command "ganache-cli --port 7545 --deterministic"
timeout /t 4 > nul  REM Wait 4 seconds before Truffle

echo Running Truffle Migrations...
start powershell -NoExit -Command "cd Codes/blockchain; truffle migrate --reset"
timeout /t 1 > nul

echo Starting Backend Server...
start powershell -NoExit -Command "cd Codes/backend; python server.py"
timeout /t 1 > nul

echo Starting Journal Receiver...
start powershell -NoExit -Command "cd Codes/journal_receiver; python journal_receiver.py"
timeout /t 1 > nul

echo Starting Frontend - Author...
start powershell -NoExit -Command "cd Codes/frontend/author; npm start"
timeout /t 1 > nul

echo Starting Frontend - Reviewer...
start powershell -NoExit -Command "cd Codes/frontend/reviewer; npm start"
timeout /t 1 > nul

echo All processes started.
pause
