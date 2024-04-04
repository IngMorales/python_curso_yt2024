from flask import Flask, request, render_template_string, send_file
import os
import requests
import tempfile
from pytube import YouTube

app = Flask(__name__)

# Asegúrate de reemplazar esto con una variable de entorno o alguna forma segura de manejar la clave API
YOUTUBE_API_KEY = "AIzaSyCEUgtHL2lVSEA2jpuIYE9AL9aEnmnvxE0"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"

HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Descargador de Videos de YouTube</title>
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://use.fontawesome.com/releases/v5.15.3/css/all.css" rel="stylesheet">
  <!-- Estilos aquí -->
</head>
<body>
<div class="container mt-5">
  <h1 class="text-center mb-4">Descargador de Videos de YouTube <i class="fas fa-video"></i></h1>
  <div class="search-box">
    <input type="text" class="form-control" placeholder="Ingrese la URL del video de YouTube" id="url" required>
    <button class="btn btn-outline-secondary" onclick="submitUrl()"><i class="fas fa-search"></i></button>
  </div>
  {% if video_info %}
  <div class="text-center">
    <img src="{{ video_info.thumbnail_url }}" class="video-thumbnail">
    <h2 class="mt-3">{{ video_info.title }}</h2>
  </div>
  <div>
    {% for stream in streams %}
    <div class="stream-card">
      <div class="stream-info">
        <div>{{ stream.resolution }}</div>
        <div>{{ stream.filesize // 1024 // 1024 }} MB</div>
        <form method="post">
          <input type="hidden" name="itag" value="{{ stream.itag }}">
          <input type="hidden" name="url" value="{{ video_info.url }}">
          <button class="btn btn-primary" type="submit"><i class="fas fa-download"></i> Descargar</button>
        </form>
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}
</div>
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.9.2/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
<script>
  function submitUrl() {
    const url = document.getElementById('url').value;
    const form = document.createElement('form');
    form.method = 'post';
    form.style.display = 'none';
    const urlInput = document.createElement('input');
    urlInput.type = 'hidden';
    urlInput.name = 'url';
    urlInput.value = url;
    form.appendChild(urlInput);
    document.body.appendChild(form);
    form.submit();
  }
</script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        itag = request.form.get('itag')
        video_info = None
        streams = []

        if url:
            video_id = url.split('v=')[1]
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': YOUTUBE_API_KEY
            }
            response = requests.get(YOUTUBE_API_URL, params=params).json()
            items = response.get('items', [])
            
            if not items:
                # Manejar el caso de no encontrar datos del video
                pass
            else:
                video_detail = items[0]
                video_info = {
                    'thumbnail_url': video_detail['snippet']['thumbnails']['high']['url'],
                    'title': video_detail['snippet']['title'],
                    'url': url
                }
                # Implementar la lógica para obtener las resoluciones y tamaños de archivos usando pytube o alguna otra biblioteca si es necesario

        return render_template_string(HTML_TEMPLATE, url=url, video_info=video_info, streams=streams)
    else:
        return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
