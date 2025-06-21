import os
import sys
import copy
import argparse
import subprocess
from tqdm import tqdm
import pandas as pd


def compute_throughput(elapsed_time, data_size):
    return float(data_size[0]) * float(data_size[1]) * float(data_size[2]) * 4 / 1024.0/ 1024.0/ 1024.0 / (elapsed_time * 1e-9)


def update_command(cmp, data_path, data_size, error_bound="1e-2", bit_rate="2", cuszx_block_size=64, nsys_result_path="./nsys_result"):
    work_path = os.getenv('WORK_PATH')
    print(cmp, data_size[0], data_size[1], data_size[2] )
    try:
        nbEle = int(data_size[0]) * int(data_size[1]) * int(data_size[2])
    except:
        assert 0
    print(nbEle)
    # nsys
    if cmp == "cuszhi":
        cmd = [
                ["nsys", "profile",  "--stats=true", "-o", nsys_result_path, "cuszhi", 
                    "-t", "f32",
                    "-m", "r2r",
                    "-i", data_path,
                    "-e", error_bound,
                    "-l", f"{data_size[0]}x{data_size[1]}x{data_size[2]}",
                    "-z", 
                    "-a", "2",
                    "-s", "cr",
                    "--predictor", "spline3",
                    "--report", "time,cr"
                    ],
                ["nsys", "profile",  "--stats=true", "-o", nsys_result_path, "cuszhi", 
                    "-i", data_path+".cusza",
                    "-x",
                    "--report", "time",
                    "--compare", data_path,
                    ],
                ["compareData",
                    "-f",  data_path, data_path+'.cuszx',],
                ["rm",
                    data_path + '.cusza', data_path+'.cuszx']
                ]
    cmd_nvcomp = [
        "nsys", "profile",  "--stats=true", "-o", nsys_result_path, "benchmark_bitcomp_chunked",
        "-f", data_path, "-a", "0"
    ]
    cmd_bitcomp = [
        "nsys", "profile",  "--stats=true", "-o", nsys_result_path, "bitcomp_example",
        "-r", data_path,
    ]
    
    return cmd, cmd_nvcomp, cmd_bitcomp


def run_cuSZ(command, bitcomp_cmd_nv, bitcomp_cmd, file_path):
    result = subprocess.run(command[0], capture_output=True, text=True)
    decomp_result = subprocess.run(command[1], capture_output=True, text=True)
    qcat_result = subprocess.run(command[2], capture_output=True, text=True)

    with open(file_path, 'w') as file:
        file.write("-cusz_compress-\n" + result.stdout + result.stderr + "-cusz_compress-\n" + 
                   "-cusz_decompress-\n" + decomp_result.stdout + decomp_result.stderr + "-cusz_decompress-\n" + 
                   "-compareData-\n" + qcat_result.stdout + qcat_result.stderr + '-compareData-\n')
    result = subprocess.run(command[-1], capture_output=True, text=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help="(MANDATORY) input data folder", type=str)
    parser.add_argument('--output', '-o', help="(MANDATORY) output folder for logs", type=str)
    parser.add_argument('--dim', '-d', help="data dimension", type=int,default=3)
    parser.add_argument('--dims', '-m', help="(MANDATORY) data dimension", type=str,nargs="+")
    parser.add_argument('--eb', '-e', help="specify a list of error bounds", type=str,nargs="*")
    parser.add_argument('--br', '-b', help="specify a list of bit rates", type=str,nargs="*")
    parser.add_argument('--nsys', '-n', help="specify nsys profile result dir", type=str, default="./nsys_results/")
    args = parser.parse_args()
    
    datafolder   = args.input
    outputfolder = args.output
    data_size    = args.dims
    eb_list      = args.eb
    br_list      = args.br
    nsys_result_path         = args.nsys

    if any(e is None for e in [args.input, args.output, args.dims]):
        print()
        print("need to specify MANDATORY arguments")
        print()
        parser.print_help()
        sys.exit(1)
    
    
    method_list = ['cuszhi']
    error_bound_list = ['1e-2', '5e-3', '1e-3','5e-4', '1e-4', '5e-5', '1e-5']
    bit_rate_list = ['0.5', '1', '2', '4', '6', '8', '12', '16']
    run_func_dict = {"cuszhi":run_cuSZ,}
    
    cmp_list = method_list
    eb_list  = error_bound_list if eb_list is None else eb_list
    br_list  = bit_rate_list    if br_list is None else br_list
    
    
    datafiles=os.listdir(datafolder)
    datafiles=[file for file in datafiles if (file.split(".")[-1]=="dat" or file.split(".")[-1]=="f32" or file.split(".")[-1]=="bin") and "log" not in file]
    
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)
    
    if not os.path.exists(nsys_result_path):
        os.makedirs(nsys_result_path)
        
    echo_cmd = lambda cmd: print("    ", " ".join(cmd))
    
    for cmp in cmp_list:    
        for file in tqdm(datafiles):
            for eb in eb_list:
                data_path = os.path.join(datafolder, file)
                file_path = os.path.join(outputfolder, file)
                cmd, cmd_nvcomp, cmd_bitcomp = update_command(cmp, data_path, data_size, error_bound=eb, nsys_result_path=nsys_result_path)
                for i in cmd: 
                    echo_cmd(i)
                run_func_dict[cmp](cmd, cmd_nvcomp, cmd_bitcomp, file_path + "_eb=" + eb + "_" + cmp)