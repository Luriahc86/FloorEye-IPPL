@echo off
REM Database Setup & Migration Script for FloorEye
REM This script creates the database from scratch or migrates existing one

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   FloorEye Database Setup & Migration
echo ============================================================
echo.

REM Check if mysql is available
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: MySQL is not installed or not in PATH
    echo Please install MySQL from Laragon or add it to system PATH
    pause
    exit /b 1
)

echo [1/3] Database Status Check...

REM Check if database exists
mysql -u root -e "USE floor_eye;" >nul 2>&1

if errorlevel 1 (
    echo.
    echo Database 'floor_eye' does not exist. Creating new database...
    echo.
    
    REM Create database from fresh schema
    echo [2/3] Creating database from schema...
    mysql -u root < store\tabel.sql
    
    if errorlevel 1 (
        echo ERROR: Failed to create database
        pause
        exit /b 1
    )
    
    echo.
    echo [3/3] Database created successfully!
    echo.
    echo ✅ Fresh database setup complete.
    echo.
) else (
    echo.
    echo Database 'floor_eye' already exists.
    echo.
    
    REM Check if image_data column exists
    mysql -u root floor_eye -e "DESCRIBE floor_events;" | findstr "image_data" >nul 2>&1
    
    if errorlevel 1 (
        echo image_data column not found. Running migration...
        echo.
        echo [2/3] Backing up database...
        
        REM Create backup with timestamp
        for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
        for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
        set timestamp=!mydate!_!mytime!
        
        mysqldump -u root floor_eye > floor_eye_backup_!timestamp!.sql
        
        if errorlevel 1 (
            echo WARNING: Backup may have failed
        ) else (
            echo ✅ Backup created: floor_eye_backup_!timestamp!.sql
        )
        
        echo.
        echo [3/3] Running migration...
        mysql -u root floor_eye < store\migrate_to_db_images.sql
        
        if errorlevel 1 (
            echo ERROR: Migration failed
            echo To restore, run: mysql -u root floor_eye < floor_eye_backup_!timestamp!.sql
            pause
            exit /b 1
        )
        
        echo ✅ Migration completed successfully!
        echo.
    ) else (
        echo ✅ Database already has image_data column. Skipping migration.
        echo.
    )
)

REM Verify database
echo Verifying database...
mysql -u root floor_eye -e "SELECT COUNT(*) as total_events FROM floor_events;" 2>nul

echo.
echo ============================================================
echo   Database Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Start backend: python -m uvicorn app:app --reload
echo   2. Start frontend: npm run dev
echo   3. Open http://127.0.0.1:5173
echo.
pause
