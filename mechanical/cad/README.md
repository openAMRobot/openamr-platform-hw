# CAD folder documentation

## Overview

This repository contains a variety of CAD drawings and 3D models in multiple formats. The files are organized into the following folders:

## Folder descriptions

### `Full_assembly_STEP`

This folder includes STEP file MMP.00.00.00.000_full_assembly.STEP that represent the complete design or construction tree.

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
Comprehensive list of all assemblies and their corresponding files in the [BOM repository](https://github.com/openAMRobot/OpenAMR/tree/main/docs/hardware/BOM). It also includes details on sheet metal parts, fasteners, technological operations, and origin components.

**Note:** All components are highly interconnected and their functionality is dependent on one another.

## Contributing

If you wish to contribute to the project:

Support open-source robotics, ROS2 development, AI robotics education, Dual-arm mobile robot research.

## 💜 Support OpenAMRobot

Support open-source robotics, ROS 2 development, AI robotics education, and dual-arm mobile robot research.

### ⚡ Back the build - one-time, no strings

| Tier | What it says about you | Link |
|---|---|---|
| ⚡ **First Mover - €5** | You got here first, and you didn't overthink it. Your name goes on the backers wall - permanently - as one of the people who moved before it was obvious. Five euros, one good instinct. | <a href="https://buy.stripe.com/eVqcN5b99eeAaSd7WPgUM06" target="_blank" rel="noopener noreferrer">💳&nbsp;Back&nbsp;it&nbsp;→</a> |
| 🎯 **Sharpshooter - €25** | You spotted it early and called it. Name on the wall + a shareable "OpenAMRobot Backer" badge - proof you saw it coming while everyone else was still scrolling. | <a href="https://buy.stripe.com/4gMdR9ell1rO2lH90TgUM07" target="_blank" rel="noopener noreferrer">💳&nbsp;Back&nbsp;it&nbsp;→</a> |
| 🕶️ **Insider - €50** | You want in behind the curtain. Everything above + the backer-only build log and early files - every breakthrough, every faceplant, unfiltered. You see it before the internet does. | <a href="https://buy.stripe.com/eVq14nfpp4E0gcx2CvgUM08" target="_blank" rel="noopener noreferrer">💳&nbsp;Back&nbsp;it&nbsp;→</a> |
| 🔩 **Immortal - €100** | Your name goes on the actual robot. Physically. Forever. A machine will roll around carrying your name long after any of us remember why - and you'll have the photo to prove you were there. | <a href="https://buy.stripe.com/00w00jdhhb2o4tPfphgUM09" target="_blank" rel="noopener noreferrer">💳&nbsp;Back&nbsp;it&nbsp;→</a> |
| 🏆 **Founding Backer - €250** | Not a supporter - a co-author. Everything above + a personal thank-you in a build video. When this becomes something, you were one of the people who decided it would. | <a href="https://buy.stripe.com/28EeVdcdddawaSdeldgUM0a" target="_blank" rel="noopener noreferrer">💳&nbsp;Back&nbsp;it&nbsp;→</a> |

### 🔁 Monthly subscriptions - build it with us, every month

| Tier | What you get | Link |
|---|---|---|
| 😇 **Benefactor - €5/mo** | This month, officially not wasted. €5 to help build an open robot for everyone - cheaper than the coffee you'll forget you bought. Your name goes on the wall. History will remember you - well, me for sure. 🤖 | <a href="https://buy.stripe.com/9B6cN5dhh9Yk7G1cd5gUM05" target="_blank" rel="noopener noreferrer">💳&nbsp;Subscribe&nbsp;→</a> |
| ❤️ **Community - €19/mo** | You're in. Community access, project & roadmap updates, basic documentation, and community Q&A. (Private consultation not included.) | <a href="https://buy.stripe.com/6oUcN55OPc6s3pL4KDgUM00" target="_blank" rel="noopener noreferrer">💳&nbsp;Subscribe&nbsp;→</a> |
| 🔧 **Builder - €79/mo** | For the ones who actually build. Everything in Community + builder docs, monthly group Q&A, selected tutorials, early design updates, and discounts on digital packs. (Private consultation not included.) | <a href="https://buy.stripe.com/14A28r0uvdaw9O9eldgUM01" target="_blank" rel="noopener noreferrer">💳&nbsp;Subscribe&nbsp;→</a> |
| 🚀 **Pro Support - €299/mo** | Expert support for advanced builders, early founders, and small labs. Includes 1 private consulting call per month and up to 3 hours/month of technical guidance. | <a href="https://buy.stripe.com/dRm4gz4KLdaw6BX4KDgUM02" target="_blank" rel="noopener noreferrer">💳&nbsp;Subscribe&nbsp;→</a> |
| 🏢 **Startup Support - €750/mo** | For robotics startups and teams heading toward a prototype. Includes 2 private consulting calls per month, roadmap support, GitHub/documentation review, supplier review, and up to 6 hours/month. | <a href="https://buy.stripe.com/7sY8wPfpp8Ugf8t90TgUM03" target="_blank" rel="noopener noreferrer">💳&nbsp;Subscribe&nbsp;→</a> |
| 🔬 **Lab Support - €1,500/mo** | For universities, corporate labs, and training centers. Includes 4 private sessions per month, lab implementation support, architecture reviews, training-roadmap support, and up to 10 hours/month. | <a href="https://buy.stripe.com/eVq14ndhh2vSaSda4XgUM04" target="_blank" rel="noopener noreferrer">💳&nbsp;Subscribe&nbsp;→</a> |

**❤️ GitHub Sponsors:** <a href="https://github.com/sponsors/openAMRobot" target="_blank" rel="noopener noreferrer"> 🐙 &nbsp;github.com/sponsors/openAMRobot&nbsp;→</a>

*Every contribution - €5 or €1,500 - literally builds this robot. No billion-dollar lab required. **You're not donating. You're building it.** 🤖*

- **Issue reporting:** use the [ISSUE_TEMPLATE.md](https://github.com/openAMRobot/.github/blob/main/ISSUE_TEMPLATE.md) for reporting issues.
- **Submitting pull requests:** use the [PULL_REQUEST_TEMPLATE.md](https://github.com/openAMRobot/.github/blob/main/PULL_REQUEST_TEMPLATE.md) for submitting improvements or changes.
- **Contributing guidelines:** please read the [CONTRIBUTING.md](https://github.com/openAMRobot/OpenAMR/blob/main/CONTRIBUTING.md) for detailed contribution guidelines.

For further assistance, please refer to the repository’s main documentation or contact the repository maintainers.
