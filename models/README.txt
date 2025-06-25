# Models Directory

Place your GGUF model files in this directory to enable offline LLM text generation.

## Recommended Models

For best performance with Indonesian language, we recommend using:

1. **Llama-2-7B-Chat-GGUF**
   - Download from: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
   - Recommended variant: llama-2-7b-chat.Q4_K_M.gguf (good balance of quality and size)
   - Rename to: llama-2-7b-chat.Q4_K_M.gguf

2. **Alternative smaller models**:
   - TinyLlama-1.1B-Chat: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
   - Phi-2: https://huggingface.co/TheBloke/phi-2-GGUF

## How It Works

The application will automatically detect and use any GGUF model file placed in this directory. 
If no model is found, it will fallback to downloading a smaller model from Hugging Face 
or use basic text generation if no suitable model can be loaded.

## Memory Requirements

- 7B models: ~4GB RAM minimum
- 1-2B models: ~2GB RAM minimum

If your system has limited memory, choose a smaller model or adjust the n_ctx and n_threads 
parameters in the app.py file. 