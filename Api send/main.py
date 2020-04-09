from flask import Flask, url_for, request, render_template, send_from_directory
from markupsafe import escape
from werkzeug.utils import secure_filename
import pathlib

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Audio e cheia(key) dupa care se identifica fisierul pe care vrem sa il uploadam
        f = request.files['Audio']
        # uploads e fisierul in care vrem sa descarcam noul fisier,
        # iar secure_... e pentu a pastra denumirea fisierului
        f.save('uploads/' + secure_filename(f.filename))
        return "Succes"
    return "Failure"

@app.route('/download', methods=['GET'])
def download_file():
    if request.method == 'GET':
        #downloads e path-ul de unde isi ia fisierele iar "Bad_W...." e fisierul din folder
        return send_from_directory('downloads', 'Bad_Wolves_-_Zombie_lyrics.mp3', as_attachment=True)
    return "Failure"


if __name__ == '__main__':
    app.run(debug=True)

