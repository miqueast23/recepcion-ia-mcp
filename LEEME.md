# MCP · Video promocional Recepción IA

## 1. Requisitos (Windows)
- Python 3.10 o superior
- ffmpeg:  winget install Gyan.FFmpeg
- Cuenta en https://fal.ai con saldo y una API key

## 2. Instalar
    cd C:\mcp-video-recepcion-ia
    pip install -r requirements.txt

## 3. Conectar a Claude Desktop
Abrir %APPDATA%\Claude\claude_desktop_config.json y agregar:

    {
      "mcpServers": {
        "video-recepcion-ia": {
          "command": "python",
          "args": ["C:\\mcp-video-recepcion-ia\\server.py"],
          "env": {
            "FAL_KEY": "SU_CLAVE_DE_FAL",
            "FAL_MODEL": "fal-ai/veo3"
          }
        }
      }
    }

Reiniciar Claude Desktop.

## 4. Usar
Pedirle a Claude: "Genera las 4 escenas del video de Recepción IA y únelas".
Herramientas: ver_guion, generar_escena, estado_escena, unir_video.
Los videos quedan en Documentos\..\Videos\RecepcionIA.

## Notas
- FAL_MODEL se puede cambiar por otro modelo de video de fal.ai (por ejemplo uno más económico).
  Revise en fal.ai los parámetros del modelo elegido.
- Cada escena consume saldo de fal.ai según el modelo y la duración.
