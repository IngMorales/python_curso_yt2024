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
  {% if not resoluciones %}
    <form method="post" class="input-group mb-3">
      <input type="text" class="form-control" placeholder="Ingrese la URL del video de YouTube" name="url" required>
      <div class="input-group-append">
        <button class="btn btn-outline-secondary" type="submit">Obtener Resoluciones</button>
      </div>
    </form>
  {% else %}
    <form method="post" class="input-group mb-3">
      <input type="hidden" name="url" value="{{url}}">
      <select class="form-control" name="resolucion">
        {% for res in resoluciones %}
          <option value="{{res.itag}}">{{res.resolution}}</option>
        {% endfor %}
      </select>
      <div class="input-group-append">
        <button class="btn btn-outline-secondary" type="submit">Descargar</button>
      </div>
    </form>
  {% endif %}
  {% if mensaje %}
    <div class="alert alert-success" role="alert">
      {{ mensaje }}
    </div>
  {% endif %}
</div>
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def descargar_video():
    mensaje = ""
    resoluciones = None
    url = ""

    if request.method == 'POST':
        url = request.form.get('url')
        yt = YouTube(url)
        if 'resolucion' in request.form:
            itag = request.form.get('resolucion')
            video = yt.streams.get_by_itag(itag)
            temp_dir = tempfile.mkdtemp()
            video.download(output_path=temp_dir, filename="video.mp4")
            return send_file(os.path.join(temp_dir, "video.mp4"), as_attachment=True)
        else:
            resoluciones = yt.streams.filter(progressive=True).order_by('resolution').desc()
            return render_template_string(HTML_TEMPLATE, resoluciones=resoluciones, url=url)

    return render_template_string(HTML_TEMPLATE, mensaje=mensaje, resoluciones=resoluciones)

if __name__ == "__main__":
    app.run(debug=True)
