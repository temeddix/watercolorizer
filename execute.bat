chcp 65001
@echo off
call %USERPROFILE%/miniconda3/condabin/conda.bat activate watercolorize
python ./core.py
pause