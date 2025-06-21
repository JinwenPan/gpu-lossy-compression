# gpu-lossy-compression

This project is developed based on [cusz-I](https://github.com/JLiu-1/cusz-I), with additional features and improvements.

## Prerequisites

Before building the project, ensure the following software is installed:

- **GCC**: Recommended version ≥ 9.3  
- **CUDA**: Compatible with your GPU architecture; recommended version ≥ 12.4  
- **CMake**: Recommended version ≥ 3.18  

## Build Instructions

Follow the steps below to build the project:

```
git clone --recursive https://github.com/JinwenPan/gpu-lossy-compression.git szgpu
cd szgpu/cuszhi
mkdir build
cd build
cmake .. -D PSZ_BACKEND=cuda -D PSZ_BUILD_EXAMPLES=off -D CMAKE_CUDA_ARCHITECTURES="80" -D CMAKE_BUILD_TYPE=Release
cmake --build . -- -j
```

**Note**: Change ```CMAKE_CUDA_ARCHITECTURES``` according to your hardware. For example, NVIDIA A100 should be "80", NVIDIA RTX 4090/6000 Ada should be "89", and NVIDIA H100 should be "90".

## Execution Guide

The program consists of two main parts: **Compression** and **Decompression**.

### Compression

```
./cuszhi --report time,cr -z -t f32 -m r2r --dim3 [DimX]x[DimY]x[DimZ] -e [REL_ERROR_BOUND] --predictor spline3 -i [input.data] -s [cr/tp]
```

**Notes**:
- `input.data` is a binary input file to be compressed.
- `-t`: data type of the input file. Only `f32` (float32) is supported for the time being.
- `--dim3 [DimX]x[DimY]x[DimZ]`: dimensions of the input grid data. `DimX` is the number of elements in the fastest (continuous)dimension, while `DimZ` is the slowest.
- `-e [REL_ERROR_BOUND]`: range-based relative error bound corresponding the mode `r2r`.
- `--predictor spline3`: predictor. A weaker `lorenzo` predictor is also supported.
- `-s`: `cr` (Huffman-integrated lossless pipeline, slower but higher compression ratio) or `tp` (Huffman-free lossless pipeline, lower compression ratio but fast).
- Add `-a rd-first` if you need better rate-distortion rather than a maximized compression ratio under a fixed error bound.  

---

### Decompression

```
./cuszhi --report time -x -i [input.data.cusza] --compare input.data
```

**Notes**:
- `input.data.cusza` is the compressed file to be decompressed.
- `--compare input.data` is optional. It compares the decompressed data with the original data.

---
