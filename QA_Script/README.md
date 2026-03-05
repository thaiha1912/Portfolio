# QA Tool - Character & Prop Rig Validation Suite

## Overview

QA Tool is a comprehensive Maya Python toolkit designed to validate, clean, and optimize character and prop rigs before handoff to the animation department. This suite of scripts automates critical quality assurance checks and performs bulk corrections to ensure rigs meet production standards.

## Author Attribution

**Created by:** Thai Ha Trieu (Hannah Trieu)  
**Position:** 3D Technical Artist  
**Studio:** Vintata Animation Studio  
**Purpose:** Quality assurance and rig cleanup for production pipelines

These scripts were developed to streamline the rigging QA process, ensuring that character and prop rigs are production-ready and free of common issues before being handed off to animators.

## Features

### Core Functionality
- **Reference Management** - Import and manage all scene references, including nested ABC files
- **Namespace Cleanup** - Automatically remove unnecessary namespaces from the scene
- **Control Shape Validation** - Verify control shapes meet production standards
- **Deformer Inspection** - Check existing deformers in the rig
- **Geometry Optimization** - Clean up unnecessary nodes and geometry
- **File Export** - Export cleaned rigs in Maya (.ma) or binary (.mb) format

### Specialized Tools
- **Body Rig Cleanup** - Full cleanup pipeline for character rigs
- **Facial Rig Cleanup** - Specialized validation for facial rigging
- **Matrix Node Management** - Handle matrix constraint nodes
- **Smooth Division Levels** - Optimize geometry subdivision
- **Animation Preparation** - Clear keyframes and prepare for animation

## Installation

### Requirements
- Autodesk Maya 2017 or later
- PySide2 or PyQt5
- ngSkinTools plugin
- matrixNodes plugin (optional, for advanced rigging features)

### Setup

1. **Copy files to Maya scripts directory:**
   ```
   C:\Users\YOUR_NAME\Documents\maya\[VERSION]\scripts\
   ```

2. **Update script paths in QAtool_exec.py (optional):**
   - The scripts use relative imports by default
   - If needed, update the file path in the setup comments at the top of QAtool_exec.py

3. **Add to Maya shelf or userSetup.py:**
   ```python
   import sys
   sys.path.append("C:/Users/YOUR_NAME/Documents/maya/2017/scripts/")
   
   import QAtool_exec as qatool
   qatool.QAtool_UI()
   ```

## Usage

### Launching the Tool
In Maya's Python console or shelf:
```python
import QAtool_exec as qatool
qatool.QAtool_UI()
```

### Workflow

1. **Select Character/Prop Node**
   - Click "Select" button
   - Choose the top-level node of your character or prop rig
   - The tool automatically detects scene type (body/facial)

2. **Choose Export Options**
   - Select file format (.ma or .mb)
   - Specify export directory
   - Check "Open submit file after export" for immediate verification

3. **Run QA Process**
   - **Full Rig Cleanup**: Runs complete validation and cleanup for body rigs
   - **Facial Cleanup**: Specialized cleanup for facial rigs
   - **Step-by-Step**: Run individual cleanup functions from the "Clean up funcs" tab

4. **Verify & Export**
   - Monitor progress in the progress window
   - Review the "Misc Tools" tab for additional utilities
   - Export the cleaned rig for handoff to animation


## Best Practices

1. **Always save before running QA** - Create a backup of your working file
2. **Use Full Rig Cleanup for body rigs** - Ensures comprehensive validation
3. **Use Facial Cleanup for facial rigs** - Applies facial-specific checks
4. **Review step-by-step output** - Monitor console messages during execution
5. **Export formats** - Use .mb for binary scenes, .ma for text-based interchange
6. **Nested references** - Tool automatically handles nested ABC files

## Technical Details

### Python Compatibility
- Python 2.7+ and Python 3.x compatible
- Uses six package for compatibility where needed

### Maya API Usage
- Maya Commands (cmds) for lightweight operations
- PyMEL for object-oriented rig manipulation
- Maya OpenAPI for advanced node operations

### Dependencies
- `maya.cmds` - Maya command system
- `pymel.core` - PyMEL object-oriented API
- `Qt` (PySide2/PyQt5) - GUI framework
- `ngSkinTools` - Advanced skinning support (optional)

## Contributing

This is a production tool developed for animation studio workflows. Modifications should be tested thoroughly before deployment.

## License

Internal use at Vintata Animation Studio. All rights reserved.


