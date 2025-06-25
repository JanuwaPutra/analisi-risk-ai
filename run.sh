#!/bin/bash
# Script untuk menjalankan aplikasi analisis risiko

# Menampilkan banner
echo "=================================================="
echo "   Aplikasi Analisis Risiko - Versi Offline LLM   "
echo "=================================================="

# Cek apakah Python terinstal
if ! command -v python3 &> /dev/null; then
    echo "Python 3 tidak ditemukan. Silakan instal Python 3 terlebih dahulu."
    exit 1
fi

# Cek apakah virtual environment sudah dibuat
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Gagal membuat virtual environment. Coba instal python3-venv terlebih dahulu."
        exit 1
    fi
fi

# Aktifkan virtual environment
echo "Mengaktifkan virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

# Instal dependensi jika belum
echo "Menginstal dependensi..."
pip install -r requirements.txt

# Cek apakah folder models sudah ada
if [ ! -d "models" ]; then
    mkdir -p models
fi

# Cek apakah model sudah didownload (cek jika ada file .gguf di folder models)
if ! ls models/*.gguf 1> /dev/null 2>&1; then
    echo "Model GGUF belum ditemukan. Lanjutkan dengan model alternatif..."
    echo "Anda bisa mendownload model GGUF secara manual dan letakkan di folder models/"
    echo "Contoh: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
    
    # Cek apakah model transformers sudah didownload
    echo "Mencoba inisialisasi model TinyLlama..."
    python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0', local_files_only=True)" 2> /dev/null
    if [ $? -ne 0 ]; then
        echo "Model TinyLlama belum didownload. Menjalankan download_models.py..."
        python download_models.py --transformers
    else
        echo "Model TinyLlama sudah tersedia secara lokal."
    fi
fi

# Cek spaCy model
echo "Memeriksa model spaCy..."
SPACY_MODELS=("id_core_news_lg" "en_core_web_lg" "en_core_web_sm")
SPACY_MODEL_FOUND=false

for model in "${SPACY_MODELS[@]}"; do
    python -c "import spacy; spacy.load('$model')" 2> /dev/null
    if [ $? -eq 0 ]; then
        echo "Model spaCy '$model' sudah terinstal."
        SPACY_MODEL_FOUND=true
        break
    fi
done

if [ "$SPACY_MODEL_FOUND" = false ]; then
    echo "Model spaCy belum didownload. Menjalankan download_models.py..."
    python download_models.py --spacy
fi

# Jalankan aplikasi
echo "Menjalankan aplikasi..."
python app.py 