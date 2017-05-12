#!/usr/bin/python3

import argparse
import subprocess as sp
from os import makedirs
from os.path import join, isfile, getsize


def parse_arguments():
    parser = argparse.ArgumentParser(description='performs multiple scans using TreeD and processes the scans to filter out junk data and place them at the coordinate systems origin')
    parser.add_argument('-r', '--rotation_scans', type=int, help='the number of scans to take in rotation axis')
    parser.add_argument('-c', '--curve_angles', nargs='+', type=int, help='a list of the curve angles to scan the object from, for example: --curve_angles 0 20 40')
    parser.add_argument('-w', '--view', action='store_true', help='open pcl_viewer to show the filtered point clouds when all scans are done')
    parser.add_argument('--cutoff_height', type=int, help='the cutoff height to be used by the filter when removing the stick, default=10')
    parser.add_argument('-f', '--filter_only', action='store_true', help='only filter the specified point clouds and don\'t make new scans')
    args = parser.parse_args()

    rotation_angle = 360
    if args.rotation_scans:
        rotation_angle = int(360 / args.rotation_scans)
        if not rotation_angle:
            rotation_angle = 1

    curve_angles = [0]
    if args.curve_angles:
        curve_angles = args.curve_angles
        
    return rotation_angle, curve_angles, args.view, args.cutoff_height, args.filter_only

def run_command(command, time_out=None):
    try:
        process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = process.communicate(timeout=time_out)
        return process.returncode, out, err

    except sp.TimeoutExpired as e:
        process.kill()

        print('Command: ' + ' '.join(e.cmd))
        print('timed out in ' + str(e.timeout) + ' seconds')
        if e.cmd and e.cmd[0] == 'treed':
            print('Restart the hardware and then re-run the treed_wrapper with the same arguments.')
        return 1, None, None

    except OSError as e:
        if e.errno == 2 and command[0] == 'filter':
            print('filter executable not found. Make sure it is in the users PATH variable (~/bin for example).')
        else:
            raise
        return 2, None, None

def run_treed_scan(filename, rotation, curve):
    """
    Runs a scan using TreeD with the specified rotation and curve.
    Returns True if the scan was successful and False otherwise.
    """
    rotation_command = ['treed', 'set', '--table-rotation', str(rotation)]
    curve_command = ['treed', 'set', '--table-curve', str(curve)]
    scan_command = ['treed', 'scan', '-o', filename]

    expected_scan_output = 'Starting scan\nFile saved to %s\n' % filename

    run_command(rotation_command)
    run_command(curve_command)
    exit_code, out, err = run_command(scan_command, 120)

    # Check if scan failed or saved file is invalid
    if exit_code:
        raise ValueError('Wrong exit code from call to TreeD', exit_code)
    elif not out:
        raise ValueError('No output to stdout from treed')
    elif out.decode('ascii') != expected_scan_output:
        raise ValueError('Unexpected output from TreeD', out.decode('ascii'), expected_scan_output)
    elif not isfile(filename):
        raise FileNotFoundError('TreeD did not produce an output file', filename)
    elif not getsize(filename):
        raise ValueError('TreeD produced an empty output file', filename)
        
def run_filter(filename, rotation, curve, cutoff=None):
    """
    Runs the filter on the point cloud in filename. Assumes that the filter is on
    the users path. Applies rotation and curve on the filtered point cloud to
    roughly align it.
    """
    filter_command = ['filter', '-r', str(rotation), '-c', str(curve), filename]
    if cutoff:
        filter_command += ['--cutoff_height', str(cutoff)]
    exit_code, out, err = run_command(filter_command)


if __name__ == '__main__':
    rotation_angle, curve_angles, show_viewer, cutoff, filter_only = parse_arguments()    
    rotations = [int(x) for x in range(360) if x % rotation_angle == 0]

    filtered_files = []

    # Make sure the scans subdir exists
    makedirs('scans', exist_ok=True)

    for curve in curve_angles:
        for rotation in rotations:
            # Genereate the file paths for the scan and for the filter
            filename = join('scans/', 'cur%srot%s.pcd' % (str(curve).zfill(2), str(rotation).zfill(3)))
            filtered_filename = 'cur%srot%s_filtered.pcd' % (str(curve).zfill(2), str(rotation).zfill(3))

            filtered_files += [filtered_filename]


            if filter_only:
                print("Filtering " + filename)
                run_filter(filename, rotation, curve, cutoff)

            elif not isfile(filtered_filename):
                # Scan if filtered file doesn't exist
                print("Scanning to " + filename)

                # Run a scan with TreeD at the rotation and curve
                # Will raise an exception if TreeD fails, this is not handled intentionally so
                # the user can see the exception and see what went wrong
                run_treed_scan(filename, rotation, curve)

                # If TreeD succeeded, run the filter on the scaned cloud
                run_filter(filename, rotation, curve, cutoff)

            else:
                print("Skipping " + filename)

    if show_viewer:
        viewer_command = ['pcl_viewer'] + filtered_files
        run_command(viewer_command)
