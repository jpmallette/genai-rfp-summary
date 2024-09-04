from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def upload():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('file')
    for file in files:
        if file.filename == '':
            return redirect(request.url)
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
    # After saving the files, redirect to the summary screen
    return redirect(url_for('summary'))

@app.route('/summary')
def summary():
    return render_template('index.html')

@app.route('/static/images/<filename>')
def get_image(filename):
    return send_from_directory('static/images', filename)

@app.route('/get-image/<filename>')
def get_image_html(filename):
    image_url = url_for('get_image', filename=filename)
    return f'<img src="{image_url}" class="img-fluid">'

if __name__ == '__main__':
    app.run(debug=True)
