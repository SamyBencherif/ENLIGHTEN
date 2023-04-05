@echo off

REM This is an automated script to bootstrap a previously checked-out Enlighten
REM source code distribution and prepare it for development (default) or create
REM an installer.

set "rebuild_env=0"
set "clear_pyinst_appdata=0"
set "configure_conda=0"
set "install_python_deps=0"
set "update_conda=0"
set "log_conf_pkg=0"
set "regenerate_qt=0"
set "pyinstaller=0"
set "innosetup=0"

if "%1" == "activate" (
    echo %date% %time% configuring for activation
    goto args_parsed
)

if "%1" == "pyinstaller" (
    echo %date% %time% configuring for pyinstallation
    set "regenerate_qt=1"
    set "pyinstaller=1"
    echo %date% %time% jumping to label
    goto args_parsed
    echo %date% %time% failed to jump
)

if "%1" == "innosetup" (
    echo %date% %time% configuring for innosettingup
    set "innosetup=1"
    goto args_parsed
)

if "%1" == "rebuildall" (
    echo %date% %time% configuring for rebuildingall
    set "rebuild_env=1"
    set "clear_pyinst_appdata=1"
    set "configure_conda=1"
    set "install_python_deps=1"
    set "update_conda=1"
    set "log_conf_pkg=1"
    goto args_parsed
)

REM DEFINE CUSTOM ACTION HERE
if "%1" == "custom" (
    echo %date% %time% configuring for custom shenanigans
    set "rebuild_env=0"
    set "clear_pyinst_appdata=0"
    set "configure_conda=0"
    set "install_python_deps=0"
    set "update_conda=0"
    set "log_conf_pkg=0"
    set "regenerate_qt=0"
    set "pyinstaller=0"
    set "innosetup=0"
    goto args_parsed
)

echo === USAGE ===
echo $ scripts\bootstrap activate
echo Do not perform any major actions. Prepare environment variables and conda for using Enlighten.
echo.
echo $ scripts\bootstrap pyinstaller
echo regenerate Qt views and run pyinstaller (to create standalone exe)
echo.
echo $ scripts\bootstrap innosetup
echo run innosetup (to create windows installer)
echo.
echo $ scripts\bootstrap rebuildall
echo This will take a while. Remove and recreate the conda environment and reinstall all dependencies from the internet.
echo.
echo $ scripts\bootstrap custom
echo If you need a very particular action sequence (for example run pyinstaller without regenerating Qt views), edit this file, search for DEFINE CUSTOM ACTION HERE, and change flags as desired.
goto:eof

:args_parsed

if not exist scripts\bootstrap.bat (
    echo Please run script as scripts\bootstrap.bat
    goto script_failure
) else (
    echo Running from %cd%
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting environment variables
echo %date% %time% ======================================================
REM capture start time
set TIME_START=%time%
set PYTHONPATH=..\Wasatch.PY;pluginExamples;.;enlighten\assets\uic_qrc
if exist "C:\Program Files (x86)" (
    set "PROGRAM_FILES_X86=C:\Program Files (x86)"
) else (
    set "PROGRAM_FILES_X86=C:\Program Files"
)
echo using PROGRAM_FILES_X86 = %PROGRAM_FILES_X86%

echo.
echo %date% %time% ======================================================
echo %date% %time% Checking dependencies
echo %date% %time% ======================================================
echo.
set MINICONDA=%USERPROFILE%\Miniconda3
if not exist %MINICONDA% (
    echo %MINICONDA% not found.
    goto script_failure
)

if not exist "%PROGRAM_FILES_X86%\Inno Setup 6" (
    echo Warning: Inno Setup 6 not installed
    goto script_failure
)

if not exist "..\Wasatch.PY" (
    echo Warning: Wasatch.PY not found
    goto script_failure
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Extracting Enlighten version
echo %date% %time% ======================================================
echo.
grep '^VERSION' enlighten/common.py | grep -E -o '([0-9]\.?)+' > version.txt
set /p ENLIGHTEN_VERSION=<version.txt
echo ENLIGHTEN_VERSION = %ENLIGHTEN_VERSION%

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting path
echo %date% %time% ======================================================
echo.
set PATH=%MINICONDA%;%MINICONDA%\Scripts;%MINICONDA%\Library\bin;%PROGRAM_FILES_X86%\Inno Setup 6;%PATH%
echo Path = %PATH%

echo.
echo %date% %time% ======================================================
echo %date% %time% Confirm Python version
echo %date% %time% ======================================================
echo.
which python
python --version
if %errorlevel% neq 0 goto script_failure

if "%clear_pyinst_appdata%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Delete pyinstaller appdata OPTIONAL
    echo %date% %time% ======================================================
    echo.
    echo removing %USERPROFILE%\AppData\Roaming\pyinstaller
    rd /s /q %USERPROFILE%\AppData\Roaming\pyinstaller
) else (
    echo NOT CLEARING PYINST APPDATA because clear_pyinst_appdata = %clear_pyinst_appdata%
)

if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Delete conda environment OPTIONAL
    echo %date% %time% ======================================================
    echo.
    echo removing %MINICONDA%\envs\conda_enlighten3
    rd /s /q %MINICONDA%\envs\conda_enlighten3
) else (
    echo NOT DELETING CONDA ENV because rebuild_env = %rebuild_env%
)

if "%configure_conda%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Configure Conda
    echo %date% %time% ======================================================
    echo.
    conda config --set always_yes yes --set changeps1 no
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT CONFIGURING CONDA because configure_conda = %configure_conda%
)

if "%update_conda%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Update Conda OPTIONAL
    echo %date% %time% ======================================================
    echo.
    conda update -q conda
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT UPDATING CONDA because update_conda = %update_conda%
)

if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Remove old Conda environment OPTIONAL
    echo %date% %time% ======================================================
    echo.
    conda env remove -n conda_enlighten3
    if %errorlevel% neq 0 goto script_failure
) else (
    echo "NOT REMOVING OLD CONDA ENV because rebuild_env = %rebuild_env%
)

if "%log_conf_pkg%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Logging Conda configuration
    echo %date% %time% ======================================================
    echo.
    conda info -a
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT LOGGING CONDA CONFIG because log_conf_pkg = %log_conf_pkg%
)

if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Creating Conda Environment OPTIONAL
    echo %date% %time% ======================================================
    echo.
    del /f /q environment.yml
    copy environments\conda-win10.yml environment.yml
    conda env create -n conda_enlighten3
) else (
    echo NOT CREATING CONDA ENV because rebuild_env = %rebuild_env%
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Activating environment
echo %date% %time% ======================================================
echo.
REM Use "source" from bash, "call" from batch and neither from Cmd
call activate conda_enlighten3
if %errorlevel% neq 0 goto script_failure

echo.
echo %date% %time% ======================================================
echo %date% %time% Reconfirming Python version
echo %date% %time% ======================================================
echo.
which python
REM this version doesn't get logged...why? (maybe goes to stderr?)
python --version
if %errorlevel% neq 0 goto script_failure

REM echo.
REM echo %date% %time% ======================================================
REM echo %date% %time% Upgrading PIP
REM echo %date% %time% ======================================================
REM echo.
REM python -m pip install --upgrade pip

if "%install_python_deps%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Installing Python pip dependencies [conda missing/bad]
    echo %date% %time% ======================================================
    echo.

    python -m pip install -r requirements.txt
    REM Bootstrap bat is meant to make a windows installer
    REM because of this separately install pywin32 since it's only meant for windows
    pip install pywin32
    if %errorlevel% neq 0 goto script_failure

    echo %date% %time% reinstalling and upgrading pyqt5
    python -m pip uninstall pyqt5
    python -m pip install --upgrade pyqt5

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Installing pyinstaller from pip
    echo %date% %time% ======================================================
    echo.
    pip install pyinstaller==4.10
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT INSTALLING PYTHON DEPS because install_python_deps = %install_python_deps%
)

if "%log_conf_pkg%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Logging Conda packages
    echo %date% %time% ======================================================
    echo.
    cmd /c "conda list --explicit"
    if %errorlevel% neq 0 goto script_failure

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Logging Pip packages
    echo %date% %time% ======================================================
    echo.
    pip freeze
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT LOGGING CONDA/PIP because log_conf_pkg = %log_conf_pkg%
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting Python path
echo %date% %time% ======================================================
echo.
set PYTHONPATH=.;%cd%\pluginExamples;%cd%\..\Wasatch.PY;%CONDA_PREFIX%\lib\site-packages
echo PYTHONPATH = %PYTHONPATH%

if "%regenerate_qt%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Regenerating Qt views
    echo %date% %time% ======================================================
    echo.
    sh scripts\rebuild_resources.sh
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT REGENERATING because regenerate_qt = %regenerate_qt%
)

@REM echo.
@REM echo %date% %time% ======================================================
@REM echo %date% %time% Run tests...may take some time
@REM echo %date% %time% ======================================================
@REM echo.
REM
REM MZ: disabling this for now
REM
REM py.test tests -x
REM if %errorlevel% neq 0 goto script_failure

if "%pyinstaller%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Purging old build artifacts
    echo %date% %time% ======================================================
    echo.
    rmdir /Q /S scripts\built-dist\Enlighten
    rmdir /Q /S scripts\work-path\Enlighten

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Running PyInstaller OPTIONAL
    echo %date% %time% ======================================================
    echo.

    rem address bug in current pyinstaller?
    rem copy enlighten\assets\uic_qrc\images\EnlightenIcon.ico .
    rem set SPECPATH=%cd%/scripts

    REM remove --windowed to debug the compiled .exe and see Python invocation
    REM error messages
    REM
    REM --windowed ^

    REM pyinstaller --distpath="scripts/built-dist" --workpath="scripts/work-path" --noconfirm --clean scripts/enlighten.spec

    echo %date% %time% actually running pyinstaller
    pyinstaller ^
        --distpath="scripts/built-dist" ^
        --workpath="scripts/work-path" ^
        --noconfirm ^
        --noconsole ^
        --clean ^
        --paths="../Wasatch.PY" ^
        --hidden-import="scipy._lib.messagestream" ^
        --hidden-import="scipy.special.cython_special" ^
        --hidden-import="tensorflow" ^
        --icon "../enlighten/assets/uic_qrc/images/EnlightenIcon.ico" ^
        --specpath="%cd%/scripts" ^
        scripts/Enlighten.py

    echo %date% %time% post-pyinstaller errorlevel %errorlevel%

    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT RUNNING PYINSTALLER because pyinstaller = %pyinstaller%
)

if "%innosetup%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Running Inno Setup
    echo %date% %time% ======================================================
    echo.
    "%PROGRAM_FILES_X86%\Inno Setup 6\iscc.exe" /DENLIGHTEN_VERSION=%ENLIGHTEN_VERSION% scripts\Application_InnoSetup.iss
    if %errorlevel% neq 0 goto script_failure

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Reviewing installer artifacts [built-dist]
    echo %date% %time% ======================================================
    echo.
    dir scripts\built-dist\Enlighten\*.exe
    if %errorlevel% neq 0 goto script_failure

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Reviewing installer artifacts [windows_installer]
    echo %date% %time% ======================================================
    echo.
    dir scripts\windows_installer\*.exe
    if %errorlevel% neq 0 goto script_failure

    copy scripts\windows_installer\Enlighten-Setup64-%ENLIGHTEN_VERSION%.exe .
    if %errorlevel% neq 0 goto script_failure
) else (
    echo NOT RUNNING INNO SETUP because innosetup = %innosetup%
)

echo.
echo %date% %time% All steps completed successfully.
echo %date% %time% Started at %TIME_START%
goto:eof

:script_failure
echo.
echo Boostrap script failed: errorlevel %errorlevel%
exit /b 1
