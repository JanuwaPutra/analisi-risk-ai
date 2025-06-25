@echo off
REM Script untuk menjalankan aplikasi analisis risiko di Windows

echo ==================================================
echo    Aplikasi Analisis Risiko - Versi Offline LLM   
echo ==================================================

REM Cek apakah Python terinstal
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python tidak ditemukan. Silakan instal Python terlebih dahulu.
    pause
    exit /b 1
)

REM Cek apakah virtual environment sudah dibuat
if not exist "venv" (
    echo Membuat virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Gagal membuat virtual environment. Coba instal venv terlebih dahulu.
        pause
        exit /b 1
    )
)

REM Aktifkan virtual environment
echo Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Instal dependensi jika belum
echo Menginstal dependensi...
pip install -r requirements.txt

REM Cek apakah folder models sudah ada
if not exist "models" (
    mkdir models
)

REM Cek apakah model sudah didownload
set MODEL_FOUND=0
for %%f in (models\*.gguf) do (
    set MODEL_FOUND=1
)

if %MODEL_FOUND% EQU 0 (
    echo Model GGUF belum ditemukan. Lanjutkan dengan model alternatif...
    echo Anda bisa mendownload model GGUF secara manual dan letakkan di folder models\
    echo Contoh: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
    
    REM Cek apakah model transformers sudah didownload
    echo Mencoba inisialisasi model TinyLlama...
    python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0', local_files_only=True)" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Model TinyLlama belum didownload. Menjalankan download_models.py...
        python download_models.py --transformers
    ) else (
        echo Model TinyLlama sudah tersedia secara lokal.
    )
)

REM Cek spaCy model
echo Memeriksa model spaCy...
set SPACY_MODEL_FOUND=0

python -c "import spacy; spacy.load('id_core_news_lg')" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Model spaCy 'id_core_news_lg' sudah terinstal.
    set SPACY_MODEL_FOUND=1
)

if %SPACY_MODEL_FOUND% EQU 0 (
    python -c "import spacy; spacy.load('en_core_web_lg')" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Model spaCy 'en_core_web_lg' sudah terinstal.
        set SPACY_MODEL_FOUND=1
    )
)

if %SPACY_MODEL_FOUND% EQU 0 (
    python -c "import spacy; spacy.load('en_core_web_sm')" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Model spaCy 'en_core_web_sm' sudah terinstal.
        set SPACY_MODEL_FOUND=1
    )
)

if %SPACY_MODEL_FOUND% EQU 0 (
    echo Model spaCy belum didownload. Menjalankan download_models.py...
    python download_models.py --spacy
)

REM Jalankan aplikasi
echo Menjalankan aplikasi...
python app.py

pause 