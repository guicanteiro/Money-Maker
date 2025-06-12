from flask import Flask, request, send_file
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
            return {"error": "No images provided."}, 400

        final_width = 1080
        final_height = 1920
        num_imgs = len(images)
        img_height = final_height // num_imgs
        final_img = Image.new("RGB", (final_width, final_height), (0, 0, 0))

        for i, item in enumerate(images[:3]):  # máximo de 3 imagens
            try:
                b64data = item['data'].split(",")[1]  # remove 'data:image/jpeg;base64,'
                img_bytes = BytesIO(base64.b64decode(b64data))
                img = Image.open(img_bytes).convert("RGB")
                img = ImageOps.fit(img, (final_width, img_height), Image.ANTIALIAS)
            except Exception as e:
                print(f"[FALHA] Erro ao processar imagem {i+1}: {e}")
                img = Image.new("RGB", (final_width, img_height), (50, 50, 50))  # imagem fallback cinza

            final_img.paste(img, (0, i * img_height))

        output_path = "/tmp/montagem_final.jpg"
        final_img.save(output_path)
        return send_file(output_path, mimetype="image/jpeg")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
