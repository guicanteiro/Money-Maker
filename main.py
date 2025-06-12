from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageOps
from io import BytesIO
import base64
import os

app = Flask(__name__)

@app.route('/montar', methods=['POST'])
def montar_imagem():
    try:
        images = request.json.get("images", [])
        if not images:
            return jsonify({"error": "No images provided."}), 400

        final_width = 1080
        final_height = 1920
        num_imgs = len(images)
        if num_imgs == 0:
            return jsonify({"error": "Empty image list"}), 400

        img_height = final_height // num_imgs
        final_img = Image.new("RGB", (final_width, final_height), (0, 0, 0))

        for i, item in enumerate(images[:3]):  # Máximo 3 imagens
            try:
                data_uri = item.get('data')
                if not data_uri or "base64," not in data_uri:
                    raise ValueError("Data URI inválido")

                b64data = data_uri.split(",")[1]
                img_bytes = BytesIO(base64.b64decode(b64data))
                img = Image.open(img_bytes).convert("RGB")
                img = ImageOps.fit(img, (final_width, img_height), Image.ANTIALIAS)

            except Exception as e:
                print(f"[ERRO] Imagem {i+1} falhou: {e}")
                img = Image.new("RGB", (final_width, img_height), (80, 80, 80))  # fallback cinza escuro

            final_img.paste(img, (0, i * img_height))

        path = "/tmp/montagem_final.jpg"
        final_img.save(path)
        return send_file(path, mimetype="image/jpeg")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
