#!/usr/bin/env python3
"""
Download script untuk model LLM yang akan digunakan oleh aplikasi analisis risiko.
Model akan disimpan secara lokal sehingga aplikasi dapat dijalankan secara offline.
"""

import os
import logging
import argparse
from pathlib import Path

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_transformers_model():
    """Download dan cache model TinyLlama dari HuggingFace"""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        logger.info("Mendownload model TinyLlama dari HuggingFace...")
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        # Download dan cache tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info("Tokenizer berhasil didownload dan di-cache")
        
        # Download dan cache model
        model = AutoModelForCausalLM.from_pretrained(model_name)
        logger.info("Model berhasil didownload dan di-cache")
        
        return True
    except ImportError:
        logger.error("Library transformers tidak terinstall. Jalankan 'pip install transformers torch'")
        return False
    except Exception as e:
        logger.error(f"Error saat mendownload model: {e}")
        return False

def download_spacy_model():
    """Download model spaCy"""
    try:
        import spacy
        import sys
        
        # Coba download model bahasa Indonesia jika tersedia
        logger.info("Mencoba download model spaCy bahasa Indonesia...")
        try:
            spacy.cli.download("id_core_news_lg")
            logger.info("Model spaCy bahasa Indonesia berhasil didownload")
            return True
        except Exception as e:
            logger.warning(f"Tidak bisa download model bahasa Indonesia: {e}")
            
        # Fallback ke model bahasa Inggris
        logger.info("Mencoba download model spaCy bahasa Inggris...")
        
        # Coba download model besar terlebih dahulu
        try:
            spacy.cli.download("en_core_web_lg")
            logger.info("Model spaCy bahasa Inggris (large) berhasil didownload")
            return True
        except Exception as e:
            logger.warning(f"Tidak bisa download model besar: {e}")
        
        # Fallback ke model kecil
        try:
            spacy.cli.download("en_core_web_sm")
            logger.info("Model spaCy bahasa Inggris (small) berhasil didownload")
            return True
        except Exception as e:
            logger.error(f"Tidak bisa download model spaCy: {e}")
            return False
    except ImportError:
        logger.error("Library spaCy tidak terinstall. Jalankan 'pip install spacy'")
        return False

def download_gguf_model(gguf_url=None):
    """Download model GGUF dari URL yang diberikan"""
    # Jika tidak ada URL, hanya tampilkan petunjuk
    if not gguf_url:
        logger.info("""
        Untuk penggunaan model GGUF (llama-cpp-python):
        1. Download model GGUF dari Hugging Face, misal: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
        2. Letakkan file .gguf di folder models/ (misal: models/llama-2-7b-chat.Q4_K_M.gguf)
        3. Aplikasi akan otomatis menggunakan model tersebut jika tersedia
        """)
        return False
        
    try:
        import requests
        from tqdm import tqdm
        
        # Pastikan folder models ada
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # Ekstrak nama file dari URL
        filename = gguf_url.split("/")[-1]
        output_path = models_dir / filename
        
        # Jika file sudah ada, skip download
        if output_path.exists():
            logger.info(f"File {filename} sudah ada di {output_path}")
            return True
            
        # Download file dengan progress bar
        logger.info(f"Mendownload {filename} dari {gguf_url}...")
        
        response = requests.get(gguf_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
                
        logger.info(f"Model GGUF berhasil didownload ke {output_path}")
        return True
    except ImportError:
        logger.error("Library requests atau tqdm tidak terinstall. Jalankan 'pip install requests tqdm'")
        return False
    except Exception as e:
        logger.error(f"Error saat mendownload model GGUF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download model untuk aplikasi analisis risiko")
    parser.add_argument("--transformers", action="store_true", help="Download model TinyLlama dari HuggingFace")
    parser.add_argument("--spacy", action="store_true", help="Download model spaCy")
    parser.add_argument("--gguf", type=str, help="URL untuk download model GGUF (opsional)")
    parser.add_argument("--all", action="store_true", help="Download semua model yang tersedia")
    
    args = parser.parse_args()
    
    # Jika tidak ada argumen, download semua
    if not (args.transformers or args.spacy or args.gguf or args.all):
        args.all = True
        
    if args.all or args.transformers:
        download_transformers_model()
        
    if args.all or args.spacy:
        download_spacy_model()
        
    if args.gguf:
        download_gguf_model(args.gguf)
    elif args.all:
        download_gguf_model()  # Hanya tampilkan petunjuk
        
    logger.info("Proses download selesai")

if __name__ == "__main__":
    main() 