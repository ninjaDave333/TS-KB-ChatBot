@echo off
REM Sync production data from server to local data folder
REM ref_data remains as backup/reference

set SERVER=ubuntu@aipg.dudelabz.com
set KEY=D:\Projects\aipg.pem
set REMOTE_PATH=/home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot/data
set LOCAL_PATH=data

echo Fetching production data from server...
echo.

REM Critical files for pattern learning
scp -i "%KEY%" "%SERVER%:%REMOTE_PATH%/production_metrics.json" "%LOCAL_PATH%/"
scp -i "%KEY%" "%SERVER%:%REMOTE_PATH%/traces.jsonl" "%LOCAL_PATH%/" 2>nul
scp -i "%KEY%" "%SERVER%:%REMOTE_PATH%/query_patterns.json" "%LOCAL_PATH%/"

REM Optional: Learning state files
scp -i "%KEY%" "%SERVER%:%REMOTE_PATH%/production_insights.json" "%LOCAL_PATH%/" 2>nul
scp -i "%KEY%" "%SERVER%:%REMOTE_PATH%/self_learning_report.json" "%LOCAL_PATH%/" 2>nul

echo.
echo ✓ Sync complete - production data in data/
echo ✓ Original reference data preserved in ref_data/
echo.
echo Latest files:
dir /b "%LOCAL_PATH%\production_metrics.json" "%LOCAL_PATH%\query_patterns.json" 2>nul
