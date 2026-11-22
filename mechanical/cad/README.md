# CAD folder documentation

## Overview

This repository contains a variety of CAD drawings and 3D models in multiple formats. The files are organized into the following folders:

## Folder descriptions

### `Full_assembly_STEP`

This folder includes the full assembly as a zipped STEP file, `MMP.00.00.00.000_full_assembly.STEP.zip` (the STEP is 139 MB, over GitHub's 100 MB file limit; unzip it before opening). It represents the complete design or construction tree.

- **STEP files:** these files are compatible with various CAD programs, including SolidWorks, Catia, and AutoCAD. They adhere to the STEP (Standard for the Exchange of Product Data) format, which uses ASCII text to describe three-dimensional objects and models according to the ISO 10303 specification.

- **Usage:** use these files to restore and view full designs or construction assemblies in your preferred CAD software.

### Full SolidWorks 2017 project (Release asset)

The complete native project package (`MMP.00.00.00.000_Multipurpose_mobile_platform.zip`, ~50 MB —
all components, fasteners, and models for SolidWorks 2017+) is **not stored in the repo** (it is over
GitHub's 50 MB file threshold and bloats every clone). It is distributed as a **GitHub Release asset**:

➡️ **[Releases](https://github.com/openAMRobot/openamr-platform-hw/releases)** → download
`MMP.00.00.00.000_Multipurpose_mobile_platform.zip`.

**💡MMP — Multipurpose Mobile Platform.** After downloading, extract the zip into a folder named
`MMP.00.00.00.000_Multipurpose_mobile_platform` and open the file with all zeros in the name,
`MMP.00.00.00.000`, to load the full project. The neutral **STEP full assembly** (in
`Full_assembly_STEP/`) is committed in the repo and opens in any CAD tool if you don't need the
native SolidWorks source.

### `production_files`

This folder provides production-ready files in various formats that can be used to order parts without requiring specialized software.

- **File formats:** PDF, DXF, SLDDRW, and SLDPRT.

- **Usage:** these files contain detailed drawings and specifications sufficient for ordering parts directly from production facilities.

## File handling instructions

## Accessing and using projects

- **Full project:** download the SolidWorks 2017 project from the
  [Releases](https://github.com/openAMRobot/openamr-platform-hw/releases) (see above), then open the
  file named `MMP.00.00.00.000` in SolidWorks.

- **Editing and improvements:** after opening the project, you can rename assemblies, edit, or improve the models. We encourage you to suggest improvements or report issues to the project.

## ⚠️Important notice for the sheet metal parts

Sheet metal parts are subject to production variations. The current designs are based on the following coefficients and radii:

- **Coefficient (K):** 0.47
- **Sheet metal specifications:**
  - **0.8 mm Sheet:** Radius (R) = 1.2
  - **1.2 mm Sheet:** Radius (R) = 1.5
  - **2.0 mm Sheet:** Radius (R) = 2.4

### Post-production

- Parts may be painted after bending.
- Riveting nuts can be installed before painting if the threaded part is protected from the coating.
- Screws installed without lock washers should be secured with a thread lock (e.g., Loxeal 55-03).

### 📜Bill of Materials (BOM) and list of assemblies, drawings, original parts 
Comprehensive list of all assemblies and their corresponding files in the [BOM folder](../../manufacturing/bom/). It also includes details on sheet metal parts, fasteners, technological operations, and origin components.

**Note:** All components are highly interconnected and their functionality is dependent on one another.

## Contributing

If you wish to contribute to the project:

Support open-source robotics, ROS2 development, AI robotics education, Dual-arm mobile robot research.

## 💜 Support OpenAMRobot

Support open-source robotics, ROS 2 development, AI robotics education, and dual-arm mobile robot research.

### ⚡ Back the build

To back the build or subscribe monthly, use the sponsor page below.

**❤️ GitHub Sponsors:** <a href="https://github.com/sponsors/openAMRobot" target="_blank" rel="noopener noreferrer"> 🐙 &nbsp;github.com/sponsors/openAMRobot&nbsp;→</a>

*Every contribution literally builds this robot. No billion-dollar lab required. **You're not donating. You're building it.** 🤖*

- **Issue reporting:** use the [ISSUE_TEMPLATE.md](https://github.com/openAMRobot/.github/blob/main/ISSUE_TEMPLATE.md) for reporting issues.
- **Submitting pull requests:** use the [PULL_REQUEST_TEMPLATE.md](https://github.com/openAMRobot/.github/blob/main/PULL_REQUEST_TEMPLATE.md) for submitting improvements or changes.
- **Contributing guidelines:** please read the [CONTRIBUTING.md](https://github.com/openAMRobot/OpenAMR/blob/main/CONTRIBUTING.md) for detailed contribution guidelines.

For further assistance, please refer to the repository’s main documentation or contact the repository maintainers.
