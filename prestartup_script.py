import threading
import subprocess
import sys
import os
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("App", f'{os.path.dirname(__file__)}/app.py')
App = importlib.util.module_from_spec(spec)
sys.modules["App"] = App
spec.loader.exec_module(App)

subprocess.call([sys.executable, f'{os.path.dirname(__file__)}/installer.py'])

def l():
    print('Starting Gradio WebUI')
    return App.App().launch(share=True,show_tips=True,debug=True,server_port=7680)

threading.Thread(target=l,daemon=True).start()