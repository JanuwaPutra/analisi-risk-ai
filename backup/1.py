from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, send_file
import pandas as pd
import numpy as np
import docx
import requests
import json
from fuzzywuzzy import fuzz
import os
import logging
import datetime
import time
import queue
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'analisis_risiko_key'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure JSON cache folder
CACHE_FOLDER = 'cache'
if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)

# Sample data path
SAMPLE_DATA_PATH = os.path.join(CACHE_FOLDER, 'sample_data.json')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global progress tracking
progress_queue = queue.Queue()
progress_data = {
    'total': 0,
    'current': 0,
    'status': 'Idle',
    'message': '',
    'last_analyzed': ''
}

# Tambahkan fungsi now() untuk template
@app.template_filter('now')
def now():
    return datetime.datetime.now()

# Initialize analysis cache
analysis_cache = {}

def read_excel_data(file_path=None):
    """Read data from Excel file"""
    if not file_path or not os.path.exists(file_path):
        return []
    
    try:
        df = pd.read_excel(file_path)
        # Bersihkan data dari baris dengan nilai NaN di kolom nama
        df = df.dropna(subset=['nama'])
        # Konversi kolom nama ke string
        df['nama'] = df['nama'].astype(str)
        # Kolom nama menggunakan huruf kecil di file Excel
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return []

def read_word_paragraphs(file_path=None):
    """Read paragraphs from Word file"""
    if not file_path or not os.path.exists(file_path):
        return []
    
    try:
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return paragraphs
    except Exception as e:
        logger.error(f"Error reading Word file: {e}")
        return []

def extract_json_from_text(text):
    """Extract JSON object from text that might contain markdown or other content"""
    # Try to find JSON object using regex
    import re
    json_pattern = r'({[^{}]*(?:{[^{}]*})*[^{}]*})'
    matches = re.findall(json_pattern, text)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # If regex fails, try markdown code block extraction
    if '```' in text:
        try:
            code_blocks = text.split('```')
            for i in range(1, len(code_blocks), 2):
                block = code_blocks[i]
                if block.startswith('json'):
                    block = block[4:].strip()  # Remove 'json' and whitespace
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass
    
    # Return default if nothing works
    return {
        "ringkasan": "Failed to extract JSON", 
        "skor_risiko": 0, 
        "persentase_kerawanan": "0%", 
        "kategori": "RENDAH", 
        "faktor_risiko": ["Error parsing"], 
        "rekomendasi": "Coba lagi", 
        "urgensi": "MONITORING",
        "nama": "",
        "jabatan": "N/A"
    }

def load_sample_data():
    """Load sample data from JSON file"""
    try:
        if os.path.exists(SAMPLE_DATA_PATH):
            with open(SAMPLE_DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        return []

def save_sample_data(data, add_date=False):
    """Save data to sample_data.json file with duplicate removal and date tagging"""
    try:
        # Get current date and time
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Remove duplicates based on nama and paragraf
        seen = set()
        unique_data = []
        
        for item in data:
            # Create a key from nama and first 50 chars of paragraf
            key = (item.get('nama', ''), item.get('paragraf', '')[:50])
            if key not in seen:
                # Add tanggal_tambah field to new entries if it doesn't exist
                if 'tanggal_tambah' not in item and add_date:
                    item['tanggal_tambah'] = current_date
                seen.add(key)
                unique_data.append(item)
        
        # Sort data by date (newest first)
        unique_data.sort(key=lambda x: x.get('tanggal_tambah', '1970-01-01 00:00:00'), reverse=True)
        
        # Save to file
        with open(SAMPLE_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=2)
        
        return unique_data
    except Exception as e:
        logger.error(f"Error saving sample data: {e}")
        return data

def analyze_paragraph(paragraph, person_name):
    """Send paragraph to Llama 4 Maverick via OpenRouter API for analysis"""
    # Check cache first
    cache_key = paragraph[:100]  # Use first 100 chars as key
    if cache_key in analysis_cache:
        # Update progress
        progress_data['message'] = f"Using cached analysis for paragraph"
        progress_data['last_analyzed'] = paragraph[:50] + "..." if len(paragraph) > 50 else paragraph
        progress_data['current'] += 1
        progress_queue.put(dict(progress_data))
        
        return analysis_cache[cache_key]
    
    try:
        # Update progress
        progress_data['message'] = f"Analyzing paragraph with API"
        progress_data['last_analyzed'] = paragraph[:50] + "..." if len(paragraph) > 50 else paragraph
        progress_data['current'] += 1
        progress_queue.put(dict(progress_data))
        
        logger.info(f"Pre-analyzing paragraph {progress_data['current']}/{progress_data['total']}")
        
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "meta-llama/llama-4-maverick",
            "messages": [
                {
                    "role": "system",
                    "content": "Kamu adalah analis intelijen keamanan senior yang fokus pada Potential Risk Intelligence. Tugasmu adalah mengevaluasi tingkat risiko berdasarkan konten berita. Balas HANYA dengan JSON, tanpa penjelasan tambahan."
                },
                {
                    "role": "user",
                    "content": f"Analisis kutipan berita berikut dan berikan penilaian risiko kerawanan/kerusuhan. Balas HANYA dalam format JSON tanpa kalimat pembuka atau penutup:\n{{\n \"ringkasan\": \"Ringkasan singkat berita\",\n \"skor_risiko\": 75,\n \"persentase_kerawanan\": \"75%\",\n \"kategori\": \"TINGGI\",\n \"faktor_risiko\": [\"Faktor 1\", \"Faktor 2\"],\n \"rekomendasi\": \"Rekomendasi tindakan mitigasi\",\n \"urgensi\": \"SEGERA\"\n}}\n\nKategori harus salah satu dari: RENDAH (0-30%), SEDANG (31-60%), TINGGI (61-85%), KRITIS (86-100%)\nUrgensi harus salah satu dari: MONITORING, PERHATIAN, SEGERA, DARURAT\n\nKutipan:\n{paragraph}"
                }
            ],
            "temperature": 0.1,  # Lower temperature for more consistent JSON formatting
            "max_tokens": 300    # Limit response size for faster processing
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15  # Shorter timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Try to extract JSON from the response
            analysis = extract_json_from_text(content)
            
            # Initialize nama and jabatan fields
            analysis['nama'] = ''
            analysis['jabatan'] = 'N/A'
            
            # Make sure faktor_risiko is a list
            if 'faktor_risiko' in analysis and isinstance(analysis['faktor_risiko'], str):
                analysis['faktor_risiko'] = [analysis['faktor_risiko']]
            
            # Cache the result in memory
            analysis_cache[cache_key] = analysis
            
            return analysis
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            default_response = {
                "ringkasan": "API request failed", 
                "skor_risiko": 0, 
                "persentase_kerawanan": "0%", 
                "kategori": "RENDAH", 
                "faktor_risiko": ["Error API"], 
                "rekomendasi": "Coba lagi nanti", 
                "urgensi": "MONITORING",
                "nama": "",
                "jabatan": "N/A"
            }
            analysis_cache[cache_key] = default_response
            return default_response
    except requests.exceptions.Timeout:
        logger.error(f"API request timed out for paragraph: {paragraph[:50]}...")
        default_response = {
            "ringkasan": "API request timed out", 
            "skor_risiko": 0, 
            "persentase_kerawanan": "0%", 
            "kategori": "RENDAH", 
            "faktor_risiko": ["Timeout"], 
            "rekomendasi": "Coba lagi nanti", 
            "urgensi": "MONITORING",
            "nama": "",
            "jabatan": "N/A"
        }
        analysis_cache[cache_key] = default_response
        return default_response
    except Exception as e:
        logger.error(f"Error in API request: {e}")
        default_response = {
            "ringkasan": f"Error: {str(e)}", 
            "skor_risiko": 0, 
            "persentase_kerawanan": "0%", 
            "kategori": "RENDAH", 
            "faktor_risiko": ["Error"], 
            "rekomendasi": "Periksa koneksi", 
            "urgensi": "MONITORING",
            "nama": "",
            "jabatan": "N/A"
        }
        analysis_cache[cache_key] = default_response
        return default_response

def match_person_to_paragraph(person, paragraph):
    """Use fuzzy matching to determine if a person is mentioned in a paragraph"""
    # Menggunakan kolom 'nama' dengan huruf kecil sesuai data Excel
    name = person.get('nama', '')
    
    # Handle null/None/NaN values
    if pd.isna(name) or name is None or name == '':
        return False
    
    # Convert name to string in case it's numeric
    name = str(name)
    
    # Convert both to lowercase for better matching
    name_lower = name.lower()
    paragraph_lower = paragraph.lower()
    
    # Direct substring match - hanya cocokkan nama yang persis sama
    if name_lower in paragraph_lower:
        # Pastikan ini adalah nama yang berdiri sendiri, bukan bagian dari kata lain
        # Misalnya, jika nama "Ani", jangan cocokkan dengan kata "mANIpulasi"
        for word in paragraph_lower.split():
            if name_lower == word:
                return True
            # Jika nama terdiri dari beberapa kata, cek frasa
            if len(name_lower.split()) > 1 and name_lower in paragraph_lower:
                return True
    
    # Fuzzy matching hanya untuk nama yang terdiri dari minimal 2 kata
    # (Nama lengkap, bukan hanya jabatan atau nama pendek)
    if len(name_lower.split()) >= 2:
        words = paragraph_lower.split()
        for i in range(len(words)):
            for j in range(i+1, min(i+6, len(words)+1)):  # Cek sampai 5 kata
                phrase = ' '.join(words[i:j])
                score = fuzz.ratio(name_lower, phrase)
                if score > 85:  # Naikkan threshold untuk mengurangi false positive
                    return True
    
    return False

@app.route('/progress')
def progress():
    """Server-sent events endpoint for progress updates"""
    def generate():
        while True:
            try:
                # Get progress data from the queue with a timeout
                data = progress_queue.get(timeout=1.0)
                yield f"data: {json.dumps(data)}\n\n"
            except queue.Empty:
                # Send a heartbeat every second if no updates
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            time.sleep(0.5)  # Throttle updates to avoid overwhelming the client
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default filter values
    kategori_filter = request.form.get('kategori', 'all')
    
    # Initialize paths for uploaded files
    tokoh_file_path = None
    berita_file_path = None
    results = []
    stats = {
        'total_berita': 0,
        'total_tokoh': 0,
        'kategori_count': {
            'RENDAH': 0,
            'SEDANG': 0,
            'TINGGI': 0,
            'KRITIS': 0,
            'RENDAH_pct': 0,
            'SEDANG_pct': 0,
            'TINGGI_pct': 0,
            'KRITIS_pct': 0
        },
        'urgensi_count': {
            'MONITORING': 0,
            'PERHATIAN': 0,
            'SEGERA': 0,
            'DARURAT': 0
        },
        'avg_skor': 0
    }
    
    # Check if form was submitted with files
    if request.method == 'POST' and 'tokoh_file' in request.files and 'berita_file' in request.files:
        tokoh_file = request.files['tokoh_file']
        berita_file = request.files['berita_file']
        
        if tokoh_file.filename != '' and berita_file.filename != '':
            # Save uploaded files
            tokoh_filename = secure_filename(tokoh_file.filename)
            berita_filename = secure_filename(berita_file.filename)
            
            tokoh_file_path = os.path.join(app.config['UPLOAD_FOLDER'], tokoh_filename)
            berita_file_path = os.path.join(app.config['UPLOAD_FOLDER'], berita_filename)
            
            tokoh_file.save(tokoh_file_path)
            berita_file.save(berita_file_path)
            
            flash('Files uploaded successfully!', 'success')
            
            # Read data from uploaded files
            tokoh_data = read_excel_data(tokoh_file_path)
            paragraphs = read_word_paragraphs(berita_file_path)
            
            # Reset progress data
            progress_data['current'] = 0
            progress_data['total'] = len(set(paragraphs))
            progress_data['status'] = 'Analyzing'
            progress_data['message'] = 'Starting analysis...'
            progress_data['last_analyzed'] = ''
            progress_queue.put(dict(progress_data))
            
            # Pre-analyze unique paragraphs to avoid duplicate API calls
            paragraph_analyses = {}
            unique_paragraphs = list(set(paragraphs))  # Remove duplicates
            
            # Store processed keys to prevent duplicates
            processed_keys = set()
            
            # Match people to paragraphs using analyzed data
            for paragraph in unique_paragraphs:
                # Get analysis for this paragraph or analyze it if not done yet
                cache_key = paragraph[:100]
                if cache_key not in processed_keys:
                    if cache_key in analysis_cache:
                        paragraph_analyses[paragraph] = analysis_cache[cache_key]
                    else:
                        analysis = analyze_paragraph(paragraph, "")
                        paragraph_analyses[paragraph] = analysis
                        # Cache is updated inside analyze_paragraph
                    
                    processed_keys.add(cache_key)
                
                # Find matching people
                matched_people = []
                for person in tokoh_data:
                    if match_person_to_paragraph(person, paragraph):
                        matched_people.append(person)
                
                # Create result for each matched person
                for person in matched_people:
                    analysis = paragraph_analyses[paragraph]
                    
                    # Pastikan nama dalam person ada di Excel
                    if 'nama' in person and person.get('nama', ''):
                        # Jabatan hanya diambil dari Excel, jangan gunakan data lain
                        jabatan = person.get('jabatan', '')
                        
                        # Buat result dengan data yang benar
                        result = {
                            'nama': person.get('nama', ''),
                            'jabatan': jabatan,  # Gunakan jabatan dari Excel, kosong jika tidak ada
                            'paragraf': paragraph,
                            'ringkasan': analysis.get('ringkasan', 'N/A'),
                            'skor_risiko': analysis.get('skor_risiko', 0),
                            'persentase_kerawanan': analysis.get('persentase_kerawanan', '0%'),
                            'kategori': analysis.get('kategori', 'RENDAH'),
                            'faktor_risiko': analysis.get('faktor_risiko', []),
                            'rekomendasi': analysis.get('rekomendasi', 'N/A'),
                            'urgensi': analysis.get('urgensi', 'MONITORING')
                        }
                        
                        # If faktor_risiko is a list, join it for display
                        if isinstance(result['faktor_risiko'], list):
                            result['faktor_risiko'] = ', '.join(result['faktor_risiko'])
                        
                        results.append(result)
            
            # Update progress on completion
            progress_data['status'] = 'Complete'
            progress_data['message'] = 'Analysis complete!'
            progress_queue.put(dict(progress_data))
            
            # Load existing data and combine with new results
            existing_data = load_sample_data()
            combined_results = existing_data + results
            
            # Apply filters to combined results
            filtered_results = combined_results
            if kategori_filter != 'all':
                filtered_results = [r for r in filtered_results if r['kategori'] == kategori_filter]
            
            # Calculate statistics from combined results
            all_paragraphs = list(set([r.get('paragraf', '') for r in combined_results]))
            stats = {
                'total_berita': len(all_paragraphs),
                'total_tokoh': len(set([r['nama'] for r in combined_results])),
                'kategori_count': {
                    'RENDAH': len([r for r in combined_results if r['kategori'] == 'RENDAH']),
                    'SEDANG': len([r for r in combined_results if r['kategori'] == 'SEDANG']),
                    'TINGGI': len([r for r in combined_results if r['kategori'] == 'TINGGI']),
                    'KRITIS': len([r for r in combined_results if r['kategori'] == 'KRITIS'])
                },
                'urgensi_count': {
                    'MONITORING': len([r for r in combined_results if r['urgensi'] == 'MONITORING']),
                    'PERHATIAN': len([r for r in combined_results if r['urgensi'] == 'PERHATIAN']),
                    'SEGERA': len([r for r in combined_results if r['urgensi'] == 'SEGERA']),
                    'DARURAT': len([r for r in combined_results if r['urgensi'] == 'DARURAT'])
                },
                'avg_skor': sum([r.get('skor_risiko', 0) for r in combined_results]) / len(combined_results) if combined_results else 0
            }
            
            # Calculate percentages for each category
            total = sum(stats['kategori_count'].values())
            if total > 0:
                for key in list(stats['kategori_count'].keys()):
                    stats['kategori_count'][f'{key}_pct'] = round((stats['kategori_count'][key] / total) * 100, 1)
            
            # Store the combined results in the session for export
            session['results'] = combined_results
            
            # Save results to sample_data.json file
            try:
                # Save combined results to sample_data.json with duplicate removal and date tagging
                save_sample_data(combined_results, add_date=True)
                
                flash('Analysis results saved to JSON file', 'success')
            except Exception as e:
                logger.error(f"Error saving to JSON file: {e}")
                flash(f'Error saving to JSON file: {str(e)}', 'danger')
        else:
            flash('Please select both files', 'danger')
    else:
        # When no files are uploaded (GET request or empty POST), load sample data
        results = load_sample_data()
        
        # Apply filter if needed
        filtered_results = results
        if kategori_filter != 'all' and results:
            filtered_results = [r for r in results if r['kategori'] == kategori_filter]
            
        if results:
            # Calculate statistics from sample data
            unique_paragraphs = list(set([r.get('paragraf', '') for r in results]))
            stats = {
                'total_berita': len(unique_paragraphs),
                'total_tokoh': len(set([r['nama'] for r in results])),
                'kategori_count': {
                    'RENDAH': len([r for r in results if r['kategori'] == 'RENDAH']),
                    'SEDANG': len([r for r in results if r['kategori'] == 'SEDANG']),
                    'TINGGI': len([r for r in results if r['kategori'] == 'TINGGI']),
                    'KRITIS': len([r for r in results if r['kategori'] == 'KRITIS'])
                },
                'urgensi_count': {
                    'MONITORING': len([r for r in results if r['urgensi'] == 'MONITORING']),
                    'PERHATIAN': len([r for r in results if r['urgensi'] == 'PERHATIAN']),
                    'SEGERA': len([r for r in results if r['urgensi'] == 'SEGERA']),
                    'DARURAT': len([r for r in results if r['urgensi'] == 'DARURAT'])
                },
                'avg_skor': sum([r.get('skor_risiko', 0) for r in results]) / len(results) if results else 0
            }
            
            # Calculate percentages for each category
            total = sum(stats['kategori_count'].values())
            if total > 0:
                for key in list(stats['kategori_count'].keys()):
                    stats['kategori_count'][f'{key}_pct'] = round((stats['kategori_count'][key] / total) * 100, 1)
            
            # Store the results in the session for export
            session['results'] = results
            
            flash('Loaded sample data for preview', 'info')
        else:
            # If no data is found, initialize filtered_results as an empty list
            filtered_results = []
    
    # Generate current time
    current_time = datetime.datetime.now().strftime('%d %B %Y %H:%M')
    
    # Use filtered_results for display (which is either combined_results or filtered by kategori)
    return render_template('index.html', 
                          results=filtered_results,
                          selected_kategori=kategori_filter,
                          stats=stats,
                          current_time=current_time)

@app.route('/export_results')
def export_results():
    """Export the current analysis results to a JSON file"""
    try:
        # Get data directly from sample_data.json file
        results = load_sample_data()
        
        if not results:
            # Fallback to session if file is empty
            if 'results' not in session or not session['results']:
                flash('No results to export', 'warning')
                return redirect(url_for('index'))
            results = session['results']
        
        # Create a timestamp for the filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f'results_export_{timestamp}.json'
        export_path = os.path.join(CACHE_FOLDER, export_filename)
        
        # Save the results to a JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Return the file for download
        return send_file(export_path,
                       mimetype='application/json',
                       as_attachment=True,
                       download_name=export_filename)
    except Exception as e:
        flash(f'Error exporting results: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)