# treed_wrapper
A wrapper for making multiple scans using [TreeD](https://gitlab.ida.liu.se/tddd96-grupp9 "TreeD GitLab") and then filtering the scans using the [filter](https://github.com/PUM-9/filter "3DCopy filter Github"). This makes sure the point clouds are ready to use with the main [3DCopy Software](https://github.com/PUM-9/3DCopy "3DCopy Github").

## Usage
To use the program, put `src/treed_wrapper.py` somewhere in the users `PATH` and then run

```
treed_wrapper.py
```

Passing the `-h` flag prints a usage in the terminal:

```
usage: treed_wrapper.py [-h] [-r ROTATION_SCANS]
                        [-c CURVE_ANGLES [CURVE_ANGLES ...]] [-w]
                        [--cutoff_height CUTOFF_HEIGHT] [-f]

performs multiple scans using TreeD and processes the scans to filter out junk
data and place them at the coordinate systems origin

optional arguments:
  -h, --help            show this help message and exit
  -r ROTATION_SCANS, --rotation_scans ROTATION_SCANS
                        the number of scans to take in rotation axis
  -c CURVE_ANGLES [CURVE_ANGLES ...], --curve_angles CURVE_ANGLES [CURVE_ANGLES ...]
                        a list of the curve angles to scan the object from,
                        for example: --curve_angles 0 20 40
  -w, --view            open pcl_viewer to show the filtered point clouds when
                        all scans are done
  --cutoff_height CUTOFF_HEIGHT
                        the cutoff height to be used by the filter when
                        removing the stick, default=10
  -f, --filter_only     only filter the specified point clouds and don't make
                        new scans
```

## Installation
Simply put `src/treed_wrapper.py` somewhere in the users `PATH`. Uses Python 3.

## License
This program is licensed under the GNU Lesser General Public License 3.
