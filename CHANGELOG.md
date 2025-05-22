# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New modular structure for LED matrix functionality

### Changed
- Reorganized code from `led_matrix_battery.inputmodule.ledmatrix` into multiple specialized modules:
  - `led_matrix_battery.led_matrix.hardware`: Low-level hardware communication functions
  - `led_matrix_battery.led_matrix.patterns`: Pattern-related display functions
  - `led_matrix_battery.led_matrix.text`: Text and symbol rendering functions
  - `led_matrix_battery.led_matrix.media`: Image and video-related functions
- Updated all imports throughout the codebase to use the new module structure
- Improved code organization with better separation of concerns

### Removed
- Dependency on the monolithic `ledmatrix.py` module

### Benefits
- Better code organization with logical separation of functionality
- Improved maintainability through smaller, focused modules
- Clearer API with functions grouped by purpose
- Easier to extend with new features in the future