@echo off
echo Starting IPFS daemon...
start cmd /k "ipfs daemon"

echo Starting Ganache...
start cmd /k "ganache-cli --port 7545 --deterministic"

timeout /t 5 > nul

echo Running Truffle migration...
cd Codes\blockchain
call truffle migrate --reset

echo Starting Backend Server...
cd ..\backend
start cmd /k "python server.py"

echo Starting Journal Receiver...
cd ..\journal_receiver
start cmd /k "python journal_receiver.py"

echo Starting Frontend (Author)...
cd ..\frontend\author
start cmd /k "npm start"

echo Starting Frontend (Reviewer) on port 3001...
cd ..\reviewer
start cmd /k "set PORT=3001 && npm start"

echo All commands initiated.
pause
