import subprocess as sp
import os, sys
import numpy as np


db: dict = {
    "nyx": {
        "type": "f4",
        "url": "https://g-8d6b0.fd635.8443.data.globus.org/ds131.2/Data-Reduction-Repo/raw-data/EXASKY/NYX/SDRBENCH-EXASKY-NYX-512x512x512.tar.gz",
        "tar_gz": "SDRBENCH-EXASKY-NYX-512x512x512.tar.gz",
        "untar_dir": "SDRBENCH-EXASKY-NYX-512x512x512",
        "file_list": [
            "baryon_density.f32",
            "dark_matter_density.f32",
            "temperature.f32",
            "template_data.txt",
            "velocity_x.f32",
            "velocity_y.f32",
            "velocity_z.f32",
        ],
    },
    "qmc": {
        "type": "f4",
        "url": "https://g-8d6b0.fd635.8443.data.globus.org/ds131.2/Data-Reduction-Repo/raw-data/QMCPack/SDRBENCH-QMCPack.tar.gz",
        "tar_gz": "SDRBENCH-QMCPack.tar.gz",
        "untar_dir": "dataset",
        "supposed_untar_dir": "SDRBENCH-QMCPack",
        "file_list": [
            # "115x69x69x288/einspline_115_69_69_288.f32",
            "288x115x69x69/einspline_288_115_69_69.pre.f32",
            # "einspline_115_69_69_288.f32",
            "einspline_288_115_69_69.pre.f32",
        ],
    },
    "miranda": {
        "type": "f8",
        "url": "https://g-8d6b0.fd635.8443.data.globus.org/ds131.2/Data-Reduction-Repo/raw-data/Miranda/SDRBENCH-Miranda-256x384x384.tar.gz",
        "tar_gz": "SDRBENCH-Miranda-256x384x384.tar.gz",
        "untar_dir": "SDRBENCH-Miranda-256x384x384",
        "file_list": [
            "density.d64",
            "diffusivity.d64",
            "pressure.d64",
            "velocityx.d64",
            "velocityy.d64",
            "velocityz.d64",
            "viscocity.d64",
        ],
        "file_list_converted": [
            "density.f32",
            "diffusivity.f32",
            "pressure.f32",
            "velocityx.f32",
            "velocityy.f32",
            "velocityz.f32",
            "viscocity.f32",
        ],
    },
    "cesm": {
        "type": "f4",
        "url": "https://g-8d6b0.fd635.8443.data.globus.org/ds131.2/Data-Reduction-Repo/raw-data/CESM-ATM/SDRBENCH-CESM-ATM-cleared-1800x3600.tar.gz",
        "tar_gz": "SDRBENCH-CESM-ATM-cleared-1800x3600.tar.gz",
        "untar_dir": "SDRBENCH-CESM-ATM-cleared-1800x3600",
        "file_list": [
            "placeholder.f32",
        ],
    },
}

db_keys = db.keys()

RED = "\033[0;31m"
GRAY = "\033[0;37m"
NOCOLOR = "\033[0m"
BOLDRED = "\033[1;31m"


def validate_url(url: str):
    if not url.startswith("https"):
        raise ValueError("[fn::basename] ILLEGAL URL: not start with `https`")
    if not url.endswith("tar.gz"):
        raise ValueError("[fn::basename] ILLEGAL URL: not end with `tar.gz`")


def download(key: str):
    url = db[key]["url"]
    tar_gz = db[key]["tar_gz"]
    validate_url(url)

    target_tar_gz = os.path.join(datapath, tar_gz)
    if os.path.exists(target_tar_gz):
        print(f"[{key}::wget]\t{target_tar_gz} exists...skip downloading")
        pass
    else:
        print(f"[{key}::wget]\tdownloading {tar_gz}")
        cmd = f"wget {url} -P {datapath}"
        # print(cmd)
        sp.check_call(cmd, shell=True)


def untar(key: str):
    tar_gz = db[key]["tar_gz"]
    untar_dir = db[key]["untar_dir"]

    target_tar_gz = os.path.join(datapath, tar_gz)

    if not os.path.exists(target_tar_gz):
        raise FileNotFoundError(f"[untar {key}]\t{target_tar_gz} (for {key}) does not exists...")
    
    if key == "qmc" and any([os.path.exists(f"{datapath}/{untar_dir}/{i}") for i in db[key]['file_list']]):
        print(f"[{key}::untar]\tneeded files previously untar'ed ({key})...skip")
    elif all([os.path.exists(f"{datapath}/{untar_dir}/{i}") for i in db[key]['file_list']]):
        print(f"[{key}::untar]\tall files previously untar'ed ({key})...skip")
    else:
        cmd = f"tar zxvf {target_tar_gz} --directory {datapath}"
        # print(cmd)
        sp.check_call(cmd, shell=True)


# special fix to QMC: nested dir
def fix_qmc():
    ori_dir = os.path.join(datapath, "dataset") if datapath.startswith("/") else "dataset"
    untar_dir = db["qmc"]["supposed_untar_dir"]
    supposed_dir = os.path.join(datapath, untar_dir)

    # create a symbolic link to "dataset"
    try:
        os.symlink(ori_dir, supposed_dir)
    except FileExistsError:
        os.remove(supposed_dir)
        os.symlink(ori_dir, supposed_dir)
        print("[qmc::fix]\tcreated a symbolic link for QMC dir")
        pass

    # flatten qmc dir
    try:
        os.rename(
            f"{supposed_dir}/288x115x69x69/einspline_288_115_69_69.pre.f32",
            f"{supposed_dir}/einspline_288_115_69_69.pre.f32",
        )
    except FileNotFoundError:
        if os.path.exists(
            f"{supposed_dir}/einspline_288_115_69_69.pre.f32",
        ):
            pass
        else:
            raise FileNotFoundError(
                f"[qmc::fix]\tPlease go to {datapath}, manually run `tar zxvf SDRBENCH-QMCPack.tar.gz`, and come back to this director, and rerun by `python setup-data.py`"
            )


def convert_miranda():
    fdir = db["miranda"]["untar_dir"]
    flist_d64 = db["miranda"]["file_list"]
    flist_f32 = db["miranda"]["file_list_converted"]
    if all([os.path.exists(f"{datapath}/{fdir}/{i}") for i in flist_d64]):
        ## exists .d64
        if not all([os.path.exists(f"{datapath}/{fdir}/{i}") for i in flist_f32]):
            print("[miranda::convert]\tconverting from f8 to f4...")
            for i, (src, dst) in enumerate(zip(flist_d64, flist_f32)):
                src = f"{datapath}/{fdir}/{src}"
                dst = f"{datapath}/{fdir}/{dst}"
                sp.check_call(
                    f"convertDoubleToFloat {src} {dst} >/dev/null", shell=True
                )
            print()
        else:
            print("[miranda::convert]\tall .f32 files ready, skip")
    else:
        print(
            f"[miranda::convert]\tPlease go to {datapath}, manually run `tar zxvf SDRBENCH-Miranda-256x384x384.tar.gz`, and come back to this director, and rerun by `python setup-data-v2.py`"
        )


##################
## run this script
##################

try:
    datapath = os.environ["DATAPATH"]
except KeyError as e:
    print(
        "[setup::data]\tShell variable `DATAPATH` is not set. Please `source setup-all.sh <CUDA VER> <WHERE_TO_PUT_DATA_DIRS>`."
    )
    exit(1)

if not os.path.exists(datapath):
    os.makedirs(datapath)
    print(f"[setup::data]\tcreating DATAPATH -> {datapath}")
else:
    print(f"[setup::data]\tDATAPATH -> {datapath} exists, skip")

# print(datapath)

for k in db_keys:
    download(k)
    untar(k)

fix_qmc()
convert_miranda()
