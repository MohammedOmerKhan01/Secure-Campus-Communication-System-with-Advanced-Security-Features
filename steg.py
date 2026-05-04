"""
Steganography blueprint
  GET   /steganography        — steg page
  POST  /steg-hide            — hide message in image (local, download only)
  POST  /steg-extract         — extract message from uploaded image
  POST  /steg-send            — hide message in image AND send to another user
  GET   /steg-inbox           — list steg images received by current user
  POST  /steg-mark-read/<id>  — mark a steg message as read
  GET   /download/<filename>  — download a steg image (sender or receiver only)
"""

from flask import Blueprint, request, jsonify, render_template, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, StegMessage
from logger import log_event
from PIL import Image
import os, secrets

steg_bp = Blueprint('steg', __name__)

# Absolute path so it works regardless of working directory
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'bmp'}
DELIMITER   = '###END###'


# ── LSB helpers ───────────────────────────────────────────────────────────────

def _to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

def _from_bin(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if int(c, 2) != 0)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def hide_message_in_image(image_path, message, output_path):
    """Embed message into image pixels using LSB steganography."""
    img    = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())
    bits   = _to_bin(message + DELIMITER)

    if len(bits) > len(pixels) * 3:
        raise ValueError('Message too long for this image. Use a larger image.')

    new_pixels = []
    idx = 0
    for r, g, b in pixels:
        if idx < len(bits): r = (r & 0xFE) | int(bits[idx]); idx += 1
        if idx < len(bits): g = (g & 0xFE) | int(bits[idx]); idx += 1
        if idx < len(bits): b = (b & 0xFE) | int(bits[idx]); idx += 1
        new_pixels.append((r, g, b))

    out = Image.new('RGB', img.size)
    out.putdata(new_pixels)
    out.save(output_path, 'PNG')
    return output_path


def extract_message_from_image(image_path):
    """Read LSB bits from image and reconstruct the hidden message."""
    img    = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())
    bits   = ''.join(str(v & 1) for px in pixels for v in px)
    text   = _from_bin(bits)
    return text.split(DELIMITER)[0] if DELIMITER in text else text[:500]


# ── Page ──────────────────────────────────────────────────────────────────────

@steg_bp.route('/steganography')
@login_required
def steganography_page():
    users = User.query.filter(User.id != current_user.id, User.role != 'admin').all()
    inbox = (StegMessage.query
             .filter_by(receiver_id=current_user.id)
             .order_by(StegMessage.timestamp.desc())
             .limit(30).all())
    unread = sum(1 for m in inbox if not m.is_read)
    return render_template('steganography.html', users=users, inbox=inbox, unread=unread)


# ── Hide locally (download only) ──────────────────────────────────────────────

@steg_bp.route('/steg-hide', methods=['POST'])
@login_required
def steg_hide():
    """Hide message in image — returns download link, does NOT send to anyone."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded.'}), 400

    file    = request.files['image']
    message = request.form.get('message', '').strip()

    if not message:          return jsonify({'error': 'Message is required.'}), 400
    if file.filename == '':  return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use PNG, JPG, or BMP.'}), 400

    try:
        uid        = secrets.token_hex(8)
        input_path = os.path.join(UPLOAD_FOLDER, f'{uid}_{secure_filename(file.filename)}')
        file.save(input_path)

        out_name = f'steg_{uid}.png'
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        hide_message_in_image(input_path, message, out_path)
        os.remove(input_path)

        log_event('STEG_HIDE', current_user.username, f'Local hide → {out_name}')
        return jsonify({'message': 'Message hidden!', 'filename': out_name,
                        'download_url': f'/download/{out_name}'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Steganography failed: {str(e)}'}), 500


# ── Send steg image to another user ──────────────────────────────────────────

@steg_bp.route('/steg-send', methods=['POST'])
@login_required
def steg_send():
    """
    Hide message in image AND deliver it to a recipient over the secure channel.
    Form fields: image (file), message (str), receiver (username), caption (str, optional)
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded.'}), 400

    file     = request.files['image']
    message  = request.form.get('message',  '').strip()
    receiver_username = request.form.get('receiver', '').strip()
    caption  = request.form.get('caption',  '').strip()[:255]

    if not message:          return jsonify({'error': 'Secret message is required.'}), 400
    if not receiver_username: return jsonify({'error': 'Recipient is required.'}), 400
    if file.filename == '':  return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use PNG, JPG, or BMP.'}), 400

    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        return jsonify({'error': 'Recipient not found.'}), 404
    if receiver.id == current_user.id:
        return jsonify({'error': 'Cannot send to yourself.'}), 400

    try:
        uid        = secrets.token_hex(8)
        input_path = os.path.join(UPLOAD_FOLDER, f'{uid}_{secure_filename(file.filename)}')
        file.save(input_path)

        out_name = f'steg_msg_{uid}.png'
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        hide_message_in_image(input_path, message, out_path)
        os.remove(input_path)

        # Store in DB
        steg_msg = StegMessage(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            filename=out_name,
            caption=caption
        )
        db.session.add(steg_msg)
        db.session.commit()

        log_event('STEG_SEND', current_user.username,
                  f'Sent steg image to {receiver.username} (Campus {receiver.campus})')

        return jsonify({
            'message': f'Steg image sent to {receiver.username} (Campus {receiver.campus})!',
            'id': steg_msg.id
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500


# ── Inbox ─────────────────────────────────────────────────────────────────────

@steg_bp.route('/steg-inbox', methods=['GET'])
@login_required
def steg_inbox():
    """Return steg messages received by the current user."""
    msgs = (StegMessage.query
            .filter_by(receiver_id=current_user.id)
            .order_by(StegMessage.timestamp.desc())
            .limit(30).all())
    return jsonify({'inbox': [m.to_dict() for m in msgs]}), 200


# ── Mark read ─────────────────────────────────────────────────────────────────

@steg_bp.route('/steg-mark-read/<int:msg_id>', methods=['POST'])
@login_required
def steg_mark_read(msg_id):
    msg = StegMessage.query.get_or_404(msg_id)
    if msg.receiver_id != current_user.id:
        return jsonify({'error': 'Forbidden.'}), 403
    msg.is_read = True
    db.session.commit()
    return jsonify({'ok': True}), 200


# ── Extract ───────────────────────────────────────────────────────────────────

@steg_bp.route('/steg-extract', methods=['POST'])
@login_required
def steg_extract():
    """Extract hidden message from an uploaded image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded.'}), 400

    file = request.files['image']
    if file.filename == '':  return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type.'}), 400

    try:
        uid       = secrets.token_hex(8)
        tmp_path  = os.path.join(UPLOAD_FOLDER, f'tmp_{uid}_{secure_filename(file.filename)}')
        file.save(tmp_path)
        hidden = extract_message_from_image(tmp_path)
        os.remove(tmp_path)

        log_event('STEG_EXTRACT', current_user.username, 'Extracted from uploaded image')
        return jsonify({'message': 'Extracted!', 'hidden_message': hidden}), 200

    except Exception as e:
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500


# ── Download ──────────────────────────────────────────────────────────────────

@steg_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    """
    Serve a steg image file.
    Only the sender or receiver of a StegMessage may download it.
    Local-hide files (steg_<uid>.png, no DB record) are always downloadable by the creator.
    """
    safe = secure_filename(filename)
    filepath = os.path.join(UPLOAD_FOLDER, safe)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found.'}), 404

    # If it's a sent steg message, enforce access control
    record = StegMessage.query.filter_by(filename=safe).first()
    if record:
        if current_user.id not in (record.sender_id, record.receiver_id):
            return jsonify({'error': 'Access denied.'}), 403
        # Mark as read when receiver downloads
        if current_user.id == record.receiver_id and not record.is_read:
            record.is_read = True
            db.session.commit()

    return send_file(filepath, as_attachment=True)
