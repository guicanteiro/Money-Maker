
from flask import Flask, request, send_file
from PIL import Image, ImageOps
import requests
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/montar', methods=['POST'])
def montar_imagem():
    try:
        urls = request.json.get("image_urls", [])
        if not urls:
            return {"error": "No image URLs provided."}, 400

        final_width = 1080
        final_height = 1920
        num_imgs = len(urls)

        if num_imgs == 1:
            response = requests.get(urls[0])
            img = Image.open(BytesIO(response.content)).convert("RGB")
            img = ImageOps.fit(img, (final_width, final_height), Image.ANTIALIAS)
            final_img = img

        else:
            img_height = final_height // num_imgs
            final_img = Image.new("RGB", (final_width, final_height), (0, 0, 0))
            for i, url in enumerate(urls[:3]):  # máximo de 3 imagens
                response = requests.get(url)
                img = Image.open(BytesIO(response.content)).convert("RGB")
                img = ImageOps.fit(img, (final_width, img_height), Image.ANTIALIAS)
                final_img.paste(img, (0, i * img_height))

        output_path = "/tmp/montagem_final.jpg"
        final_img.save(output_path)

        return send_file(output_path, mimetype="image/jpeg")

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
