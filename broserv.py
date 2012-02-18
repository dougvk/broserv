import os
from datetime import datetime as dt
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from subprocess import Popen, PIPE
from operator import itemgetter
from urllib2 import quote

app = Flask(__name__)
app.config.from_envvar('BROSERV_SETTINGS')

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/search/', methods=['GET'])
def search():
    return render_template('search.html')

@app.route('/torrent/<path:path>/', methods=['GET'])
def seed_file(path):
    true_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
    directory = os.path.dirname(true_path)
    timestamp = dt.now().strftime('%Y-%m-%d-')
    torrent_path = "%s/%s%s.torrent" % (directory, timestamp, os.path.basename(true_path))
    command = "ctorrent -t -u \"%s\" -s %s %s" % (app.config['BROSERV'], term_escape(torrent_path), term_escape(true_path))
    filename = os.path.basename(torrent_path)
    p = Popen(command, stdout=PIPE, shell=True)
    p.communicate()
    return send_from_directory(directory, filename, cache_timeout=1, as_attachment=True, mimetype='application/x-bittorrent')

@app.route('/list/', methods=['GET'])
def root_list():
    return list('')

@app.route('/list/<path:path>/', methods=['GET'])
def list(path):
    final_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
    terminal_path = term_escape(final_path)
    files = Popen("find %s -maxdepth 1 -type f | grep -v \'.torrent$\'" % terminal_path, stdout=PIPE, shell=True)
    directories = Popen("find %s -maxdepth 1 -type d | grep -v \'.torrent$\'" % terminal_path, stdout=PIPE, shell=True)
    files_list = [('..','directory')]
    files_list.extend(get_listing(final_path, files.stdout.read(), "file"))
    files_list.extend(get_listing(final_path, directories.stdout.read(), "directory"))
    return render_template('list_files.html', rel_path=request.path, listing=files_list, path=path)

@app.route('/upload/', methods=['POST'])
def root_upload():
    return upload_file('')

@app.route('/upload/<path:path>/', methods=['POST'])
def upload_file(path):
    if request.method == 'POST':
        the_file = request.files['file']
        if the_file:
            filename = secure_filename(the_file.filename)
            the_file.save(os.path.join(app.config['UPLOAD_FOLDER'], path, filename))
            if path == '':
                return redirect(url_for('root_list'))
            else:
                return redirect(url_for('list', path=path))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_listing(path, stdout, file_type):
    newline_split = stdout.split('\n')
    listing = []
    for item in newline_split:
        item = item[len(path)+1:]
        if item is not "" and item[0] is not ".":
            listing.append((item, file_type))
    return sorted(listing, key=itemgetter(1))

def term_escape(path):
    path = path.replace(" ", "\ ")
    path = path.replace(",", "\,")
    path = path.replace("[", "\[")
    path = path.replace("]", "\]")
    path = path.replace(")", "\)")
    path = path.replace("(", "\(")
    return path

@app.template_filter('urlencode')
def do_urlencode(value):
    return quote(value)

if __name__ == '__main__':
    app.debug = True
    app.run()
