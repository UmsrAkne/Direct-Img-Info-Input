# extensions/direct-img-info/scripts/direct_img_info.py
import gradio as gr
from modules import script_callbacks, images
from PIL import Image

def on_image_dropped(img_path, cache, index):
    """新しい画像がD&Dされたとき"""
    if not img_path:
        return cache, index, "", None, ""

    try:
        with Image.open(img_path) as im:
            info = images.read_info_from_image(im) or "(no metadata)"
    except Exception as e:
        info = f"(error reading metadata: {e})"

    cache = cache or []
    cache.append({"path": img_path, "info": info})
    index = len(cache) - 1
    current = cache[index]

    return cache, index, current["path"], current["path"], current["info"]

def on_navigate(cache, index, direction):
    """← / → クリックでキャッシュ移動"""
    if not cache:
        return index, "", None, ""
    index = (index + direction) % len(cache)
    current = cache[index]
    return index, current["path"], current["path"], current["info"]

def on_after_component(component, **_kwargs):
    """txt2imgパネル内に挿入"""
    if getattr(component, "elem_id", "") == "txt2img_script_container":
        with gr.Accordion("Direct Img Info Input", open=False):
            # 状態変数を定義（初期値：空リストと0）
            cache_state = gr.State([])
            index_state = gr.State(0)

            img = gr.Image(label="Drop image", type="filepath")
            path_box = gr.Textbox(label="Image Path", interactive=False)
            info_box = gr.Textbox(label="Metadata", lines=4, interactive=False)

            with gr.Row():
                prev_btn = gr.Button("←")
                reapply_btn = gr.Button("Reapply")
                next_btn = gr.Button("→")

            # 画像をドロップしたらキャッシュに追加
            img.upload(
                fn=on_image_dropped,
                inputs=[img, cache_state, index_state],
                outputs=[cache_state, index_state, path_box, img, info_box]
            )

            # ←ボタン
            prev_btn.click(
                fn=lambda cache, index: on_navigate(cache, index, -1),
                inputs=[cache_state, index_state],
                outputs=[index_state, path_box, img, info_box]
            )

            # →ボタン
            next_btn.click(
                fn=lambda cache, index: on_navigate(cache, index, +1),
                inputs=[cache_state, index_state],
                outputs=[index_state, path_box, img, info_box]
            )

        print("[DirectImgInfo] UI injected into txt2img panel.")

script_callbacks.on_after_component(on_after_component)