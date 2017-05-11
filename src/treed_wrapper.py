#!/usr/bin/python3

import argparse
import subprocess as sp
from os import makedirs
from os.path import join, isfile


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rotation_scans', '-r', type=int, help='the number of scans to take in rotation axis')
    parser.add_argument('--curve_scans', '-c', type=int, help='the number of scans to take in curve axis')
    parser.add_argument('--view', '-w', action='store_true', help='open pcl_viewer to show the filtered point clouds when all scans are done')
    args = parser.parse_args()

    if args.rotation_scans:
        rotation_angle = 360 / args.rotation_scans
        if not rotation_angle:
            rotation_angle = 1
    else:
        rotation_angle = 360

    if args.curve_scans:
        curve_angle = 100 / args.curve_scans
        if not curve_angle:
            curve_angle = 1
    else:
        curve_angle = 100

    return rotation_angle, curve_angle, args.view

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

    #except OSError as e:
        

def run_treed_scan(filename, rotation, curve):
    """
    Runs a scan using TreeD with the specified rotation and curve.
    Returns True if the scan was successful and False otherwise.
    """
    rotation_command = ['treed', 'set', '--table-rotation', str(rotation)]
    curve_command = ['treed', 'set', '--table-curve', str(curve)]
    scan_command = ['treed', 'scan', '-o', filename]

    expected_scan_output = 'Starting scan\nFile saved to %s\n' % filename

    exit_code, out, err = run_command(rotation_command)
    exit_code, out, err = run_command(curve_command)

    exit_code, out, err = run_command(scan_command, 120)
    print(exit_code, out, err)

    # Check if scan failed
    if exit_code or not out or out.decode('ascii') != expected_scan_output:
        return False

    return True
        
def run_filter(filename, rotation, curve):
    """
    Runs the filter on the point cloud in filename. Assumes that the filter is on
    the users path. Applies rotation and curve on the filtered point cloud to
    roughly align it.
    """
    filter_command = ['filter', '-r', str(rotation), '-c', str(curve), filename]
    
    exit_code, out, err = run_command(filter_command)
    print(exit_code, out, err)


if __name__ == '__main__':
    rotation_angle, curve_angle, show_viewer = parse_arguments()
    
    rotations = [int(x) for x in range(360) if x % rotation_angle == 0]
    curves = [int(x) for x in range(100) if x % curve_angle == 0]

    filtered_files = []

    makedirs('scan', exist_ok=True)

    for curve in curves:
        for rotation in rotations:
            filename = 'cur%srot%s.pcd' % (str(curve).zfill(2), str(rotation).zfill(3))
            filtered_filename = 'cur%srot%s_filtered.pcd' % (str(curve).zfill(2), str(rotation).zfill(3))

            filtered_files += [filtered_filename]

            if not isfile(filtered_filename):
                print("Scanning to " + filename)
                if run_treed_scan(join('scan', filename), rotation, curve):
                    run_filter(join('scan', filename), rotation, curve)

    if show_viewer:
        viewer_command = ['pcl_viewer'] + filtered_files
        run_command(viewer_command)
