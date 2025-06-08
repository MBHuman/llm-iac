Сборка llama-cpp

```
cmake -S . -B build \
    -DLLAMA_HIPBLAS=1 \
    -DCMAKE_HIP_COMPILER="$(hipconfig -l)/clang" \
    -DGGML_HIP_ROCWMMA_FATTN=ON \
    -DGGML_HIP=ON && cmake --build build --parallel
```

```
cmake -S . -B build && cmake --build build --parallel
```

Run:

```
./llama-server \
  --port 8101 \
  --host 0.0.0.0 \
  -m ~/models/Mistral-7B-Instruct-v0.3-Q8_0.gguf \
  -ngl 50 \
  -cd 0 \
  -c 4096
```

symlink