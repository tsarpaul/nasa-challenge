from hashlib import md5
import os
import requests
import io
import base64
from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
from ldm.generate import Generate

from prompt import getprompt, gettype


steps = 75
ai_path = '/home/ubuntu/InvokeAI'
embedding_paths = {'lava': f'{ai_path}/logs/key2022-10-01T20-57-37_lava/checkpoints/embeddings.pt', 'barren': f'{ai_path}/logs/key2022-10-01T22-26-27_barren/checkpoints/embeddings.pt'} 
#embedding_paths['icy'] = f'{ai_path}/logs/key2022-10-01T18-15-56_my_key/checkpoints/embeddings.pt'

grs = {k: Generate(embedding_path=v, full_precision=True, weights=f'{ai_path}/models/ldm/stable-diffusion-v1/model.ckpt') for k,v in embedding_paths.items()}
[gr.load_model() for gr in grs.values()]

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def run_playgroundai(prompt, world_type, seed):
    init_image = None
    if world_type in ['icy', 'barren', 'rocky', 'lava']:
        img_path = f'./corpus/world-types/{world_type}.jpg'
        with open(img_path, 'rb') as f:
            init_image = f.read()
            init_image = base64.b64encode(init_image)
            init_image = 'data:image/jpeg;base64,' + init_image.decode('utf8')

    burp0_url = "https://playgroundai.com:443/api/models/stability"
    
    burp0_cookies "CHANGE_ME" # this should be a dict with relevant cookies
    burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/json", "Origin": "https://playgroundai.com", "Dnt": "1", "Referer": "https://playgroundai.com/create", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}
    
    burp0_json={"cfg_scale": 7, "init_image": init_image, "isPrivate": False, "mask_strength": 0.7, "modelType": "stable-diffusion", "prompt": prompt, "sampler": 3, "seed": seed, "start_schedule": 0.95, "steps": steps, "width": 768, "height": 768}
    if not init_image:
        del burp0_json['init_image']
        del burp0_json['start_schedule']
    resp = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=burp0_json) 
    
    if resp.status_code != 200:
        print(resp.content)
        raise Exception("bad response")
    
    resp_json = resp.json()
    img_req = requests.get(resp_json['image']['url'])
    if img_req.status_code != 200:
        print(img_req.content)
        raise Exception("bad response")
    img = img_req.content
    return img

def run_local_sd(prompt, model_name, seed):
    gr = grs.get(model_name)
    if gr:
        results = gr.prompt2png(prompt=prompt, outdir='./output', seed=seed, steps=steps)
    else:
        pass

    filename = results[0][0]
    with open(filename, 'rb') as f:
        img = f.read()
    return img

def add_style(prompt):
    tokens = prompt.split(',')
    tokens.insert(1, ' in the style of *')
    prompt = ','.join(tokens)
    return prompt

@app.route("/get-image", methods=['GET'])
@cross_origin()
def get_image():
    planet = request.args.get('myPlanet')
    admin_key = request.args.get('admin-key')

    print("Received: " + planet)

    # Validate admin key
    if admin_key != '7654321':
        return "Unauthorized", 403

    prompt = getprompt(planet)
    world_type = gettype(planet)
    seed = int(str(int(md5(planet.encode('utf8')).hexdigest(), 16))[:9])

    gr = grs.get(world_type)
    print(world_type)
    if gr:
        prompt = add_style(prompt)
        print(prompt)
        img = run_local_sd(prompt, world_type, seed)
    else:
        print(prompt)
        img = run_playgroundai(prompt, world_type, seed) 

    return send_file(
        io.BytesIO(img),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=f'{planet}.jpg')

@app.route("/get-type", methods=['GET'])
@cross_origin()
def get_type():
    planet = request.args.get('myPlanet')
    admin_key = request.args.get('admin-key')

    print("Received: " + planet)

    # Validate admin key
    if admin_key != '7654321':
        return "Unauthorized", 403

    prompt = getprompt(planet)
    world_type = gettype(planet)

    return {'type': world_type}


if __name__ == "__main__":
    app.run('cert.pem', 'key.pem')

