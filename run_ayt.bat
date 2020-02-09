@ECHO OFF 
cd %~dp0
CALL venv\Scripts\activate
@ECHO ON
ayt.py Battlewake Seas Pirate King --verbose
@ECHO OFF 
CALL deactivate
@ECHO ON
pause