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
    true_path = os.path.join(app.config['MEDIA_FOLDER'], path)
    directory = os.path.dirname(true_path)
    filename = os.path.basename(true_path)
    #print "True Path: %s\nDirectory: %s\nFilename: %s\n" % (true_path, directory, filename)
    torrent_true_path = "%s/%s.torrent" % (directory, filename)
    torrent_directory = os.path.dirname(torrent_true_path)
    torrent_name = os.path.basename(torrent_true_path)
    #print "Torrent True Path: %s\nFilename: %s\n" % (torrent_true_path, torrent_name)
    if not os.path.exists(torrent_true_path):
        command = "ctorrent -t -u \"%s\" -s %s %s" % (app.config['BROSERV'], term_escape(torrent_true_path), term_escape(true_path))
        #print "Command to execute: %s" % (command)
        p = Popen(command, stdout=PIPE, shell=True)
        p.communicate()
    os.system("ctorrent -e 160 -i 192.168.0.128 -p 2222 -d %s" % torrent_true_path)
    return send_from_directory(torrent_directory, torrent_name, cache_timeout=1, as_attachment=True, mimetype='application/x-bittorrent')

@app.route('/list/', methods=['GET'])
def root_list():
    return list('')

@app.route('/list/<path:path>/', methods=['GET'])
def list(path):
    final_path = os.path.join(app.config['MEDIA_FOLDER'], path)
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
            the_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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
        item = item[len(path):]
        if item is not "" and item[0] is not ".":
            if item[0] is '/':
                item = item[1:]
            listing.append((item, file_type))
    return sorted(listing, key=itemgetter(0))

def term_escape(path):
    path = path.replace(" ", "\ ")
    path = path.replace(",", "\,")
    path = path.replace("[", "\[")
    path = path.replace("]", "\]")
    path = path.replace(")", "\)")
    path = path.replace("(", "\(")
    path = path.replace("'", "\\'")
    path = path.replace("\"", "\\\"")
    return path

@app.template_filter('urlencode')
def do_urlencode(value):
    return quote(value)

if __name__ == '__main__':
    app.debug = True
    app.run(host='192.168.0.128')
