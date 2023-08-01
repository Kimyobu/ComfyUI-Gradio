import gradio as gr
import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import random
from PIL import Image
import io
import os
from folder_paths import get_folder_paths,supported_ckpt_extensions
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

def get_models():
    models = []
    for x in os.listdir(get_folder_paths('checkpoints')[0]):
        for e in supported_ckpt_extensions:
            if x.endswith(e):
                models.append(x)
                continue
    if len(models) == 0:
        models.append('')
    return models

prompt_text = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 1,
            "latent_image": [
                "5",
                0
            ],
            "model": [
                "4",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 0,
            "steps": 20
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": get_models()[0]
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 1,
            "height": 512,
            "width": 512
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": ""
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": ""
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
                "8",
                0
            ]
        }
    }
}

colors = gr.themes.colors
theme = gr.themes.Base(primary_hue=colors.orange,secondary_hue=colors.rose,neutral_hue=colors.slate)

darkmode = """function () {
  gradioURL = window.location.href
  if (!gradioURL.endsWith('?__theme=dark')) {
    window.location.replace(gradioURL + '?__theme=dark');
  } else window.location.replace('/')
}"""

def gen(model,po,ne,wid,hei):
    prompt = prompt_text
    prompt['4']['inputs']['ckpt_name'] = model
    prompt['6']['inputs']['text'] = po
    prompt['7']['inputs']['text'] = ne
    prompt['5']['inputs']['width'] = wid
    prompt['5']['inputs']['height'] = hei
    prompt['3']['inputs']['seed'] = random.randint(0, 99999999)

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)

    #Commented out code to display the output images:
    image_list = []
    for node_id in images:
        for image_data in images[node_id]:
            image_list.append(Image.open(io.BytesIO(image_data)))
    return image_list

def re_model():
    return gr.update(choices=get_models())

with gr.Blocks(theme=theme) as ui:
    gr.Text(value=get_models())
    dark = gr.Button('Switch Theme Mode')
    model = gr.Dropdown(choices=get_models(),value=get_models()[0])
    refresh_model = gr.Button('🔃', size='sm',min_width=15)
    with gr.Tab(label='txt2img'):
        with gr.Row():
            positive = gr.TextArea(label='Positive Prompt',placeholder='Write Your prompt here...')
        with gr.Row():
            negative = gr.TextArea(label='Negative Prompt',placeholder='Write Your prompt here...')
        with gr.Box():
            w = gr.Slider(minimum=1,maximum=4000,value=512,step=16,label='Width',interactive=True)
            h = gr.Slider(minimum=1,maximum=4000,value=512,step=16,label='Height',interactive=True)
        with gr.Row():
            gen_button = gr.Button('Generate', variant='primary')
        with gr.Box():
            gallery = gr.Gallery(label='Generated Images')

    refresh_model.click(re_model,outputs=[model])
    gen_button.click(gen,inputs=[model,positive,negative,w,h],outputs=[gallery],show_progress='full')
    dark.click(None,_js=darkmode)

def App():
    return ui