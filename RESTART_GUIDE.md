# Geopark Tuban Management System - Service Restart Guide

## Overview
This guide explains how to restart the Geopark Tuban Management System service.

## Restart Scripts

### 1. restart_en.bat (Recommended - Simple)
- **Language**: English
- **Function**: Basic restart (stop processes and restart service)
- **Usage**: Double-click or run in Command Prompt

### 2. restart_full.bat (Recommended - Advanced)
- **Language**: English
- **Function**: Full restart with status checking
- **Features**:
  - Stops Python processes
  - Checks port release status
  - Starts new service instance
  - Verifies service is running
- **Usage**: Double-click or run in Command Prompt

### 3. restart.bat (Original - Chinese)
- **Language**: Chinese
- **Function**: Basic restart
- **Note**: May have encoding issues on some Windows systems

### 4. restart_service.bat (Original - Chinese)
- **Language**: Chinese
- **Function**: Full restart with status checking
- **Note**: May have encoding issues on some Windows systems

### 5. Python Scripts
- `restart.py` - Full-featured Python restart script
- `restart_simple.py` - Simplified Python restart script
- `test_restart.py` - Script to test restart functionality

## How to Use

### Method 1: Double-click (Recommended)
1. Navigate to the `tuban_system` folder
2. Double-click on `restart_en.bat` or `restart_full.bat`
3. Wait for the script to complete
4. The service will start automatically in a new window

### Method 2: Command Prompt
1. Open Command Prompt
2. Navigate to the `tuban_system` folder:
   ```cmd
   cd