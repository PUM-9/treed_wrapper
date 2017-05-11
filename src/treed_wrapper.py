#!/usr/bin/python3

import argparse
import subprocess


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rotation_scans', '-r', type=int, help='the number of scans to take in rotation axis')
    parser.add_argument('--curve_scans', '-c', type=int, help='the number of scans to take in curve axis')
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

    return rotation_angle, curve_angle

def run_command(command, time_out=None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(timeout=time_out)
    return process.returncode, out, err

def run_treed_scan(filename, rotation, curve):
    rotation_command = ['treed', 'set', '--table-rotation', str(rotation)]
    curve_command = ['treed', 'set', '--table-curve', str(curve)]
    scan_command = ['treed', 'scan', '-o', filename]

    expected_scan_output = 'Starting scan\nFile saved to %s\n' % filename

    exit_code, out, err = run_command(rotation_command)
    print(exit_code, out, err)

    exit_code, out, err = run_command(curve_command)
    print(exit_code, out, err)

    exit_code, out, err = run_command(scan_command, 120)
    print(exit_code, out, err)

    if out != expected_scan_output:
        print("ERROR IN SCAN")
        return False
    else:
        print("NICE")
        return True
        
def run_filter(filename, rotation, curve):
    filter_command = ['filter', '-r', str(rotation), '--curve', str(curve), filename]
    
    exit_code, out, err = run_command(filter_command)
    print(exit_code, out, err)


if __name__ == '__main__':
    rotation_angle, curve_angle = parse_arguments()
    
    rotations = [int(x) for x in range(360) if x % rotation_angle == 0]
    curves = [int(x) for x in range(100) if x % curve_angle == 0]

    for curve in curves:
        for rotation in rotations:
            filename = 'cur%srot%s.pcd' % (str(curve).zfill(2), str(rotation).zfill(3))
            filtered_filename = 'cur%srot%s_filtered.pcd' % (str(curve).zfill(2), str(rotation).zfill(3))
            print(filename, filtered_filename)
            
            run_treed_scan(filename, rotation, curve)
            run_filter(filename, rotation, curve)
