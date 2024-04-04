from pytube import YouTube

# Función para descargar el video
def descargar_video(url):
    try:
        # Crear un objeto de YouTube
        yt = YouTube(url)
        # Obtener el stream de mayor resolución
        video = yt.streams.get_highest_resolution()
        # Descargar el video
        video.download()
        print(f"Video '{yt.title}' descargado exitosamente.")
    except Exception as e:
        print(f"Error al descargar el video: {e}")

if __name__ == "__main__":
    # Solicitar al usuario que ingrese la URL del video
    video_url = input("Ingrese la URL del video de YouTube que desea descargar: ")
    descargar_video(video_url)
