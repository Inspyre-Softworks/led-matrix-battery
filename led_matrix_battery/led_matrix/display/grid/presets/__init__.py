"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    led_matrix_battery/led_matrix/display/grid/presets/__init__.py
 

Description:
    

"""
from pathlib import Path
from led_matrix_battery.led_matrix.constants import PRESETS_DIR
from led_matrix_battery.led_matrix.display.grid.presets.manifest import GridPresetManifest


PRESETS_MANIFEST = GridPresetManifest(PRESETS_DIR / 'manifest.json')



def validate_preset_files(preset_dir_path: Path = None, manifest: GridPresetManifest = None):
    preset_dir_path = preset_dir_path or PRESETS_DIR
    manifest = manifest or

