#!/usr/bin/python

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

def run_treed_scan(filename, rotation, curve):
    rotation_command = ['treed', 'set', '--table-rotation', str(rotation)]
    curve_command = ['treed', 'set', '--table-curve', str(curve)]
    scan_command = ['treed', 'scan', '-o', filename]

    try:
        process = subprocess.Popen(rotation_command, stdout=subprocess.PIPE)
        process.wait(timeout=120)
        print('Exit code: ' + str(process.returncode))
    #except subprocess.TimeoutExpired:
    #    print('Error: TreeD timed out')
    except OSError as e:
        print(e.strerror)
    except:
        print('Unknown error occured when calling TreeD')

def run_filter(filename, rotation, curve):
    filter_command = ['filter', '-r', str(rotation), '--curve', str(curve), filename]

    process = subprocess.Popen(filter_command, stdout=subprocess.PIPE)
    #process.wait()
    print("Exit code: " + str(process.returncode))
            

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
