@echo off
python run.py %1
if errorlevel 1 (
    py run.py %1
    if errorlevel 1 (
        echo Python was not found. Please make sure Python is installed and in your PATH.
    )
) 