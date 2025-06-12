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
        img_height = final_height // num_imgs
        final_img = Image.new("RGB", (final_width, final_height), (0, 0, 0))

        for i, url in enumerate(urls[:3]):
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=5)
                res.raise_for_status()

                content_type = res.headers.get("Content-Type", "")
                print(f"[DEBUG] {url} content-type: {content_type}")
                if "image" not in content_type:
                    raise ValueError("URL não retornou uma imagem")

                img = Image.open(BytesIO(res.content)).convert("RGB")
                img = ImageOps.fit(img, (final_width, img_height), Image.ANTIALIAS)

            except Exception as e:
                print(f"[FALHA] Não foi possível carregar imagem {i+1}: {e}")
                img = Image.new("RGB", (final_width, img_height), (50, 50, 50))  # fallback

            final_img.paste(img, (0, i * img_height))

        path = "/tmp/montagem_final.jpg"
        final_img.save(path)
        return send_file(path, mimetype="image/jpeg")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
