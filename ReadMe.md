# SaaS SDK Build Scripts
  - Prepares following from the driver mdef
    - Configuration.h
    - Configuration.cpp
    - ConfigurationHelpers.cpp
    - DriverWideConfiguration.cpp
    - Static & Skeleton tables' configuration files
    - Directory structure will look like this after completion
      - [OutputDir]
        - Configs
        - Tables
        - SkeletonTables

## Requirements:
  1. [Python](https://www.python.org/downloads/)

## Input:
  1. `MDEFPath`      - Absolute/relative path to Driver MDEF
  2. `OutputDirPath` - Absolute/relative path to output directory

## Usage
```bash
python Fluffy.py MDEFPath OutputDirPath
 ```
  