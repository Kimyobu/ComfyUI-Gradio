import gradio as gr

colors = gr.themes.colors
theme = gr.themes.Base(primary_hue=colors.orange,secondary_hue=colors.rose,neutral_hue=colors.slate)

darkmode = """function () {
  gradioURL = window.location.hostname
  if (!gradioURL.endsWith('?__theme=dark')) {
    window.location.replace(gradioURL + '?__theme=dark');
  } else window.location.replace(gradioURL)
}"""

def mode():
    return

with gr.Blocks(theme=theme) as ui:
    dark = gr.Button('Switch Theme Mode')
    with gr.Tab(label='txt2img'):
        with gr.Row():
            gr.TextArea(label='Positive Prompt',placeholder='Write Your prompt here...')
        with gr.Row():
            gr.TextArea(label='Negative Prompt',placeholder='Write Your prompt here...')
        with gr.Box(label='Empty Latent'):
            gr.Slider(minimum=1,maximum=4000,value=512,step=16,label='Width',interactive=True)
            gr.Slider(minimum=1,maximum=4000,value=512,step=16,label='Height',interactive=True)
        with gr.Row():
            gr.Button('Generate', variant='primary')
            

    dark.click(None,_js=darkmode)

ui.launch(show_tips=True)