"""
Cloud Storage Helper Module
Uploads permission letters to Cloudinary (Free Cloud Storage)
Falls back to local file storage if Cloudinary credentials are not set.
"""

import os
import time
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
if CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)


def upload_permission_letter(file_obj):
    """
    Upload an approval permission letter.
    If Cloudinary credentials exist in .env, uploads to Cloudinary.
    Otherwise, saves locally to static/uploads/approved_letters/.
    
    Returns:
        public_file_url (str)
    """
    if not file_obj or not file_obj.filename:
        return None
        
    filename = secure_filename(file_obj.filename)
    unique_name = f"{int(time.time())}_{filename}"
    
    # Attempt Cloudinary Upload if configured
    if CLOUDINARY_URL or (os.getenv('CLOUDINARY_CLOUD_NAME') and os.getenv('CLOUDINARY_API_KEY')):
        try:
            result = cloudinary.uploader.upload(
                file_obj,
                folder="approved_letters",
                public_id=unique_name.rsplit('.', 1)[0],
                resource_type="auto"
            )
            print(f"☁️ Cloudinary upload successful: {result.get('secure_url')}")
            return result.get('secure_url')
        except Exception as e:
            print(f"⚠️ Cloudinary upload failed: {e}. Falling back to local storage.")
            file_obj.seek(0)
            
    # Local File Upload Fallback
    local_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'approved_letters')
    os.makedirs(local_dir, exist_ok=True)
    
    file_path = os.path.join(local_dir, unique_name)
    file_obj.save(file_path)
    print(f"💾 Saved locally to: {file_path}")
    
    return f"/static/uploads/approved_letters/{unique_name}"
