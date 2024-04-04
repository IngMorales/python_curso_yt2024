from flask import Flask, request, render_template_string, send_file
from pytube import YouTube
import os
import tempfile

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Descargador de Videos de YouTube</title>
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" rel="stylesheet">
</head>
<body>
<div class="container mt-5">
  <h1>Descargar Videos de YouTube <i class="fas fa-video"></i></h1>
  <form method="post" class="input-group mb-3">
    <input type="text" class="form-control" placeholder="Ingrese la URL del video de YouTube" name="url" required>
    <div class="input-group-append">
      <button class="btn btn-outline-secondary" type="submit" name="action" value="search">Buscar Video</button>
    </div>
  </form>
  {% if streams %}
    <h2>Seleccione la resolución para descargar el video</h2>
    <form method="post">
      <input type="hidden" name="url" value="{{url}}">
      {% for stream in streams %}
        <div class="card" style="margin-bottom: 10px;">
          <div class="card-body">
            <h5 class="card-title">{{ stream.resolution }} - Aprox. {{ stream.filesize // 1024 // 1024 }}MB</h5>
            <button class="btn btn-primary" type="submit" name="itag" value="{{ stream.itag }}">Descargar</button>
          </div>
        </div>
      {% endfor %}
    </form>
  {% endif %}
</div>
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    url = request.form.get('url')
    action = request.form.get('action')
    itag = request.form.get('itag')
    streams = []

    if url:
        yt = YouTube(url)
        if action == 'search':
            streams = yt.streams.filter(progressive=True).order_by('resolution')
        elif itag:
            stream = yt.streams.get_by_itag(itag)
            temp_dir = tempfile.mkdtemp()
            filename = stream.default_filename
            stream.download(output_path=temp_dir, filename=filename)
            path = os.path.join(temp_dir, filename)
            return send_file(path, as_attachment=True, download_name=filename)

    return render_template_string(HTML_TEMPLATE, url=url, streams=streams)

if __name__ == "__main__":
    app.run(debug=True)
