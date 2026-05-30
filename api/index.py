from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import io
import base64

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_degrees(value):
    """Konversi koordinat GPS dari format EXIF ke derajat desimal"""
    try:
        d, m, s = value
        degrees = d[0] / d[1]
        minutes = m[0] / m[1]
        seconds = s[0] / s[1]
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    except:
        return 0

def get_exif_data(image_bytes):
    """Ekstrak semua data EXIF dari gambar"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = image._getexif()
        
        if not exif_data:
            return None
            
        exif_dict = {}
        
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            
            # Handle datetime
            if tag == 'DateTime' and value:
                try:
                    dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                    exif_dict['Waktu Pengambilan'] = dt.strftime('%d %B %Y, %H:%M:%S')
                    exif_dict['Tanggal Original'] = dt.strftime('%Y-%m-%d')
                    exif_dict['Waktu Original'] = dt.strftime('%H:%M:%S')
                except:
                    exif_dict['Waktu Pengambilan'] = value
            
            # Handle model kamera/HP
            elif tag == 'Model':
                exif_dict['Perangkat'] = value.strip()
            
            # Handle merek kamera/HP
            elif tag == 'Make':
                exif_dict['Merek'] = value.strip()
            
            # Handle informasi lensa
            elif tag == 'LensModel':
                exif_dict['Lensa'] = value
            
            # Handle ISO
            elif tag == 'ISOSpeedRatings':
                exif_dict['ISO'] = value
            
            # Handle exposure time
            elif tag == 'ExposureTime':
                if isinstance(value, tuple):
                    exif_dict['Kecepatan Rana'] = f"{value[0]}/{value[1]} detik"
                else:
                    exif_dict['Kecepatan Rana'] = f"{value} detik"
            
            # Handle aperture
            elif tag == 'FNumber':
                if isinstance(value, tuple):
                    exif_dict['Bukaan'] = f"f/{value[0]/value[1]:.1f}"
                else:
                    exif_dict['Bukaan'] = f"f/{value}"
            
            # Handle focal length
            elif tag == 'FocalLength':
                if isinstance(value, tuple):
                    exif_dict['Focal Length'] = f"{value[0]/value[1]} mm"
                else:
                    exif_dict['Focal Length'] = f"{value} mm"
            
            # Handle flash
            elif tag == 'Flash':
                flash_dict = {
                    0x0: 'Flash tidak menyala',
                    0x1: 'Flash menyala',
                    0x5: 'Flash menyala, deteksi red-eye',
                    0x7: 'Flash menyala, deteksi red-eye, mode lampu',
                    0x9: 'Flash menyala, mode wajib',
                    0xd: 'Flash menyala, mode wajib, deteksi red-eye',
                    0x10: 'Flash tidak menyala, mode wajib',
                    0x18: 'Flash tidak menyala, mode otomatis',
                    0x20: 'Flash menyala, mode red-eye'
                }
                exif_dict['Flash'] = flash_dict.get(value, f'Unknown ({value})')
            
            # Handle white balance
            elif tag == 'WhiteBalance':
                exif_dict['White Balance'] = 'Auto' if value == 0 else 'Manual'
            
            # Handle orientation
            elif tag == 'Orientation':
                orientation_dict = {
                    1: 'Normal',
                    2: 'Mirror horizontal',
                    3: 'Rotate 180°',
                    4: 'Mirror vertical',
                    5: 'Mirror horizontal lalu rotasi 270° CW',
                    6: 'Rotate 90° CW',
                    7: 'Mirror horizontal lalu rotasi 90° CW',
                    8: 'Rotate 270° CW'
                }
                exif_dict['Orientasi'] = orientation_dict.get(value, f'Unknown ({value})')
            
            # Handle GPS
            elif tag == 'GPSInfo':
                gps_dict = {}
                for gps_tag in value:
                    gps_key = GPSTAGS.get(gps_tag, gps_tag)
                    gps_dict[gps_key] = value[gps_tag]
                
                if 'GPSLatitude' in gps_dict and 'GPSLongitude' in gps_dict:
                    lat = convert_to_degrees(gps_dict['GPSLatitude'])
                    lon = convert_to_degrees(gps_dict['GPSLongitude'])
                    
                    if gps_dict.get('GPSLatitudeRef') == 'S':
                        lat = -lat
                    if gps_dict.get('GPSLongitudeRef') == 'W':
                        lon = -lon
                    
                    exif_dict['Latitude'] = lat
                    exif_dict['Longitude'] = lon
                    exif_dict['Koordinat'] = f"{lat:.6f}, {lon:.6f}"
                    
                    # Google Maps link
                    exif_dict['Google Maps'] = f"https://maps.google.com/?q={lat},{lon}"
            
            # Handle software
            elif tag == 'Software':
                exif_dict['Software'] = value
            
            # Handle copyright
            elif tag == 'Copyright':
                exif_dict['Hak Cipta'] = value
        
        return exif_dict
    except Exception as e:
        print(f"Error reading EXIF: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diupload'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'error': 'File tidak dipilih'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan: PNG, JPG, JPEG, WEBP'}), 400
    
    try:
        # Baca file ke memory
        filename = secure_filename(file.filename)
        image_bytes = file.read()
        
        # Ekstrak EXIF
        exif_data = get_exif_data(image_bytes)
        
        # Dapatkan informasi file dasar
        file_size = len(image_bytes)
        
        # Baca dimensi gambar
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        format_img = image.format
        
        # Siapkan response
        response_data = {
            'filename': filename,
            'size': f"{file_size / 1024:.2f} KB",
            'dimensions': f"{width} x {height} px",
            'format': format_img,
            'exif': exif_data if exif_data else {}
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'Error memproses file: {str(e)}'}), 500

# Untuk Vercel
app.debug = False

# Handler untuk Vercel
def handler(request, context):
    return app(request.environ, lambda x, y: None)
