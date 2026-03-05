# Motion Capture Retargeting Scripts for Maya

**Author:** Thai Ha Trieu (Hannah Trieu)  
**Type:** Freelancing Projects

## Overview

This repository contains professional MEL (Maya Embedded Language) scripts designed for motion capture retargeting workflows in Autodesk Maya. These scripts automate complex animation retargeting pipelines and provide tools for handling mocap data efficiently.

## Scripts

### 1. neureal_atRetarget.mel
A comprehensive retargeting system with multi-step automation:
- **Raw Animation Processing** - Imports FBX mocap data and prepares skeleton data
- **Step-by-Step Retargeting** - Guided workflow with confirmation checkpoints (Steps 1-3)
- **Skeletal Manipulation** - Automatic hip position adjustment and idle pose generation
- **Advanced IK Setup** - Leg IK with pole vector calculations using Python integration
- **Animation Baking** - Constraint-based animation baking with customizable parameters
- **Scene Management** - File handling, namespace management, and undo optimization

### 2. underknown_rtgMocapUE.mel
A specialized retargeting tool for UE5 character pipelines:
- **FBX Batch Processing** - Recursive directory scanning and multi-file import
- **Skeletal Constraint Application** - Pelvis and orientation constraint handling
- **IK Limb Setup** - Advanced IK solvers for legs and arms with pole vectors
- **Hand Correction** - Hardcoded hand joint positioning for anatomical accuracy
- **Batch Export** - FBX export pipeline with versioning support
- **UI Tool** - Interactive button-based interface for common operations
- **Twist Joint Removal** - Automated cleanup of twist joints from mocap data
- **Timeline Automation** - Frame range detection and playback options setup


## Usage Context

These scripts were created for:
- Professional motion capture retargeting pipelines
- Game engine character preparation (UE5 compatibility)
- Complex animation workflow automation
- Multi-character batch processing systems


**Created for freelancing projects | Professional animation pipeline development**
