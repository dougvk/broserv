import os
from datetime import datetime as dt
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from subprocess import Popen, PIPE

UPLOAD_FOLDER = 'popcorn/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['USE_X_SENDFILE'] = True

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/search/', methods=['GET'])
def search():
    return render_template('search.html')

@app.route('/torrent/<path:path>/', methods=['GET'])
def seed_file(path):
    true_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], path)
    directory = os.path.dirname(true_path)
    timestamp = dt.now().strftime('%Y-%m-%d-')
    torrent_path = "%s/%s%s.torrent" % (directory, timestamp, os.path.basename(true_path))
    command = "ctorrent -t -u \"http://test.example.com\" -s %s %s" % (torrent_path, true_path)
    filename = os.path.basename(torrent_path)
    p = Popen(command, stdout=PIPE, shell=True)
    p.communicate()
    return send_from_directory(directory, filename, cache_timeout=1, as_attachment=True, mimetype='application/x-bittorrent')

@app.route('/list/', methods=['GET'])
def root_list():
    return list('')

@app.route('/list/<path:path>/', methods=['GET'])
def list(path):
    final_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], path)
    files = Popen("ls -la %s | grep -v \'.torrent$\'" % final_path, stdout=PIPE, shell=True)
    listing = create_ls_listing(files.stdout.read())
    return render_template('list_files.html', rel_path=request.path, listing=listing, path=path)

@app.route('/upload/', methods=['POST'])
def root_upload():
    return upload_file('')

@app.route('/upload/<path:path>/', methods=['POST'])
def upload_file(path):
    if request.method == 'POST':
        the_file = request.files['file']
        if the_file:
            filename = secure_filename(the_file.filename)
            the_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], path, filename))
            if path == '':
                return redirect(url_for('root_list'))
            else:
                return redirect(url_for('list', path=path))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

def create_ls_listing(stdout):
    newline_split = stdout.split('\n')[1:-1]
    listing = []
    for item in newline_split:
            listing.append((item.split()[-1], 'directory'))
        if item[0] == '-':
            listing.append((item.split()[-1], 'file'))
    return listing

if __name__ == '__main__':
    app.debug = True
    app.run()
