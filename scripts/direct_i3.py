import gradio as gr
from modules import script_callbacks

def on_after_component(component, **_kwargs):
    if getattr(component, "elem_id", "") == "txt2img_script_container":
        # txt2img の左側の拡張エリアが生成されたあとにここが呼ばれる
        with gr.Accordion("Direct Img Info Input", open=False):
            img = gr.Image(label="Drop image", type="filepath")
            path_box = gr.Textbox(label="Image Path", interactive=False)
            with gr.Row():
                gr.Button("←")
                gr.Button("Reapply")
                gr.Button("→")
        print("[DirectImgInfo] inserted into txt2img panel!")

# txt2img 部分が生成されたあとにフックする
script_callbacks.on_after_component(on_after_component)
