# Change Log
 
## [0.1.0] - 2025-12-12
 
 
### Added
- Demo script for editing h5 files with profiles
- Watershed demo script that optimizes a watershed agains an exogenous price 
 
### Changed
- Minor changes in the dashboard to accommodate changes made in the dataset and the new watershed demo 
- Improved docstrings
 
### Fixed
- Minor fixes and cleanup in code 


## [0.1.1] - 2025-12-23
 
### Added
- Progress indicator for dataset download.
 
### Fixed
- 429 Client Error http response when downloading dataset from https://zenodo.org - [Issue #3](https://github.com/NVE/fram-demo/issues/3)
- Dataset validation with pandera fails because of incompatible numpy version in *fram-data* - [Issue #4](https://github.com/NVE/fram-demo/issues/4)