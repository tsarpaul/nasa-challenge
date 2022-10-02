import base64
import requests

def run_playgroundai(prompt, world_type, seed):
    init_image = None
    if world_type in ['icy', 'barren', 'rocky', 'lava']:
        img_path = f'./corpus/world-types/{world_type}.jpg'
        with open(img_path, 'rb') as f:
            init_image = f.read()
            init_image = base64.b64encode(init_image)
            init_image = 'data:image/jpeg;base64,' + init_image.decode('utf8')

    burp0_url = "https://playgroundai.com:443/api/models/stability"

    burp0_cookies = {"__Host-next-auth.csrf-token": "22cf238c6beb262eaddcad279f505c2deb2f2f79995b6d9da0a1bc5e0e48aa88%7Cf151548e7c87d96b18208f4aa608a5e4c75ca21c360f52dc7299031cf1b1c009", "__Secure-next-auth.callback-url": "https%3A%2F%2Fplaygroundai.com%2Flogin", "__Secure-next-auth.session-token": "2dd47776-b65e-4e13-a9e5-195d270e9adf"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/json", "Origin": "https://playgroundai.com", "Dnt": "1", "Referer": "https://playgroundai.com/create", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}

    burp0_json={"cfg_scale": 7, "init_image": init_image, "isPrivate": False, "mask_strength": 0.7, "modelType": "stable-diffusion", "prompt": "scattered vast icy mountains below massive bright suns, cold, clear sky, empty, vast, lonliness, realism, intricate artwork masterpiece, ominous, intricate, perfect composition, cinematic perfect light, 8k artistic photography, epic, trending on artstation, by artgerm, national geographic and nasa, highly detailed, ultra high quality, realistic", "sampler": 3, "seed": seed, "start_schedule": 0.95, "steps": 50, "width": 768, "height": 768}
    if not init_image:
        del burp0_json['init_image']
        del burp0_json['start_schedule']
    resp = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=burp0_json)
    print(resp.content)

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

img = run_playgroundai('icy world', 'icy', 1101010101)
print(len(img))

