from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, verification_token, frontend_url='http://localhost:5173'):
    """
    Send verification email to user
    
    Args:
        user: Django User instance
        verification_token: UUID token for verification
        frontend_url: Frontend base URL for verification link
    """
    verification_link = f"{frontend_url}/verify-email?token={verification_token}"
    
    subject = 'Verifica tu cuenta - Robot Delivery Control'
    
    # HTML email content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h1 style="color: #667eea;">¡Bienvenido a Robot Delivery Control!</h1>
                <p>Hola <strong>{user.username}</strong>,</p>
                <p>Gracias por registrarte. Para completar tu registro y activar tu cuenta, por favor verifica tu dirección de correo electrónico.</p>
                <p>Haz clic en el siguiente botón para verificar tu cuenta:</p>
                <div style="text-align: center;">
                    <a href="{verification_link}" class="button">Verificar mi cuenta</a>
                </div>
                <p>O copia y pega este enlace en tu navegador:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_link}</p>
                <p><strong>Este enlace expira en 24 horas.</strong></p>
                <p>Si no creaste esta cuenta, puedes ignorar este correo de forma segura.</p>
            </div>
            <div class="footer">
                <p>Robot Delivery Control System</p>
                <p>Este es un correo automático, por favor no respondas.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version (fallback)
    plain_message = f"""
    ¡Bienvenido a Robot Delivery Control!
    
    Hola {user.username},
    
    Gracias por registrarte. Para completar tu registro y activar tu cuenta, por favor verifica tu dirección de correo electrónico.
    
    Copia y pega este enlace en tu navegador para verificar tu cuenta:
    {verification_link}
    
    Este enlace expira en 24 horas.
    
    Si no creaste esta cuenta, puedes ignorar este correo de forma segura.
    
    ---
    Robot Delivery Control System
    Este es un correo automático, por favor no respondas.
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_verification_success_email(user):
    """Send confirmation email after successful verification"""
    subject = 'Cuenta verificada exitosamente - Robot Delivery Control'
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .success {{
                color: #28a745;
                font-size: 48px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <div class="success">✓</div>
                <h1 style="color: #28a745; text-align: center;">¡Cuenta verificada!</h1>
                <p>Hola <strong>{user.username}</strong>,</p>
                <p>Tu cuenta ha sido verificada exitosamente. Ahora puedes iniciar sesión y usar todas las funcionalidades de Robot Delivery Control.</p>
                <p style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:5173" style="display: inline-block; padding: 12px 30px; background-color: #667eea; color: white; text-decoration: none; border-radius: 5px;">Ir al sistema</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = f"""
    ¡Cuenta verificada!
    
    Hola {user.username},
    
    Tu cuenta ha sido verificada exitosamente. Ahora puedes iniciar sesión y usar todas las funcionalidades de Robot Delivery Control.
    
    ---
    Robot Delivery Control System
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False
