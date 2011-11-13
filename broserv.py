import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from subprocess import Popen, PIPE

UPLOAD_FOLDER = 'popcorn/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/list/', methods=['GET'])
def root_list():
    return list('')

@app.route('/upload/', methods=['GET','POST'])
def root_upload():
    return upload_file('')

@app.route('/upload/<path>/', methods=['GET','POST'])
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
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''

@app.route('/list/<path>/', methods=['GET'])
def list(path):
    final_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], path)
    files = Popen("ls -la %s" % final_path, stdout=PIPE, shell=True)
    listing = create_ls_listing(files.stdout.read())
    return render_template('list_files.html', rel_path=request.path, listing=listing)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

def create_ls_listing(stdout):
    print stdout
    newline_split = stdout.split('\n')[1:-1]
    print newline_split
    listing = []
    for (index, item) in enumerate(newline_split):
        print item
        if item[0] == 'd':
            listing.append((item.split()[-1], 'directory'))
        if item[0] == '-':
            listing.append((item.split()[-1], 'file'))
    return listing

if __name__ == '__main__':
    app.debug = True
    app.run()
