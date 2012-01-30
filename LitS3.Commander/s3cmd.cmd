@echo off
setlocal
set IRONPYTHONPATH=%IRONPYTHONPATH%;%LITS3_PATH%;%~dp0Release;%~dp0Debug;%~dp0..\LitS3\bin\Release;%~dp0..\LitS3\bin\Debug
"%~dp0ipy\ipy" "%~dpn0.py" %*
