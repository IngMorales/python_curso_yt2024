from flask import Flask, request, render_template_string, send_file
from pytube import YouTube
import os
import tempfile

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Descargador de Videos de YouTube</title>
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://use.fontawesome.com/releases/v5.15.3/css/all.css" rel="stylesheet">
  <style>
    body { background-color: #f7f8fc; }
    .video-thumbnail { max-width: 320px; border-radius: 5px; }
    .stream-card { border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom: 10px; }
    .stream-card:hover { box-shadow: 0 2px 4px rgba(0,0,0,.2); }
    .stream-info { display: flex; align-items: center; justify-content: space-between; }
    .stream-detail { margin-right: 15px; }
    .fa-video { margin-right: 5px; }
    .fa-download { margin-left: 5px; }
  </style>
</head>
<body>
<div class="container mt-5">
  <h1>Descargador de Videos de YouTube <i class="fas fa-video"></i></h1>
  <form method="post" class="input-group mb-3">
    <input type="text" class="form-control" placeholder="Ingrese la URL del video de YouTube" name="url" required>
    <div class="input-group-append">
      <button class="btn btn-outline-secondary" type="submit"><i class="fas fa-search"></i> Buscar Video</button>
    </div>
  </form>
  {% if video_info %}
    <div class="text-center mb-4">
      <img src="{{ video_info.thumbnail_url }}" class="video-thumbnail">
      <h2 class="mt-2">{{ video_info.title }}</h2>
    </div>
    {% for stream in streams %}
      <div class="stream-card">
        <div class="stream-info">
          <span class="stream-detail"><i class="fas fa-video"></i> {{ stream.resolution }} - Aprox. {{ stream.filesize // 1024 // 1024 }} MB</span>
          <form method="post" class="d-inline">
            <input type="hidden" name="itag" value="{{ stream.itag }}">
            <input type="hidden" name="url" value="{{ video_info.url }}">
            <button class="btn btn-primary" type="submit">Descargar <i class="fas fa-download"></i></button>
          </form>
        </div>
      </div>
    {% endfor %}
  {% endif %}
</div>
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.9.2/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    url = request.form.get('url')
    itag = request.form.get('itag')
    video_info = None
    streams = []

    if url:
        yt = YouTube(url)
        if itag:
            stream = yt.streams.get_by_itag(itag)
            temp_dir = tempfile.mkdtemp()
            filename = stream.default_filename
            stream.download(output_path=temp_dir, filename=filename)
            path = os.path.join(temp_dir, filename)
            return send_file(path, as_attachment=True, download_name=filename)
        else:
            video_info = {'thumbnail_url': yt.thumbnail_url, 'title': yt.title, 'url': url}
            streams = [{
                'itag': s.itag,
                'resolution': s.resolution or "Audio only",
                'filesize': s.filesize,
            } for s in yt.streams.filter(only_audio=False).order_by('resolution')]

    return render_template_string(HTML_TEMPLATE, url=url, video_info=video_info, streams=streams)

if __name__ == "__main__":
    app.run(debug=True)
