from flask import Flask, request, render_template_string, send_file, redirect, url_for, session
import os
import tempfile
from pytube import YouTube

app = Flask(__name__)
app.secret_key = 'AIzaSyCEUgtHL2lVSEA2jpuIYE9AL9aEnmnvxE0'  # Cambia esto por una clave secreta real

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
    .container { max-width: 800px; }
    .video-thumbnail {
      max-width: 80%;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,.1);
    }
    .search-box { display: flex; margin-bottom: 2rem; }
    .search-box input { flex-grow: 1; border-top-right-radius: 0; border-bottom-right-radius: 0; }
    .search-box button { border-top-left-radius: 0; border-bottom-left-radius: 0; }
    .stream-card {
      background: #fff;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,.1);
      margin-bottom: 15px;
    }
    .stream-card:hover {
      box-shadow: 0 4px 20px rgba(0,0,0,.2);
    }
    .stream-info { display: flex; justify-content: space-between; align-items: center; }
    .stream-info .btn { box-shadow: 0 2px 5px rgba(0,0,0,.1); }
    .btn-primary {
      background-color: #007bff;
      border-color: #007bff;
    }
    .btn-primary:hover {
      background-color: #0069d9;
      border-color: #0062cc;
    }
    .fa-search { color: #495057; }
  </style>
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
        
        if url:
            yt = YouTube(url)
            if itag:
                # Procesar la descarga del stream seleccionado
                stream = yt.streams.get_by_itag(itag)
                temp_dir = tempfile.mkdtemp()
                filename = stream.default_filename
                stream.download(output_path=temp_dir, filename=filename)
                path = os.path.join(temp_dir, filename)
                return send_file(path, as_attachment=True, download_name=filename)
            
            # Almacenar información de video y streams en la sesión
            session['video_info'] = {'thumbnail_url': yt.thumbnail_url, 'title': yt.title, 'url': url}
            session['streams'] = [{
                'itag': s.itag,
                'resolution': s.resolution,
                'filesize': s.filesize
            } for s in yt.streams.filter(file_extension='mp4').filter(only_video=True).order_by('resolution').desc()]
            return redirect(url_for('home'))
    else:
        # Intentar recuperar la información de la sesión
        video_info = session.pop('video_info', None)
        streams = session.pop('streams', None)
        return render_template_string(HTML_TEMPLATE, video_info=video_info, streams=streams)

if __name__ == "__main__":
    app.run(debug=True)
