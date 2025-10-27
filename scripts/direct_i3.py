import re
import gradio as gr
from modules import script_callbacks, images
from PIL import Image
import json


def parse_png_info(info_text):
    """PNG info文字列から主要項目を抽出"""
    if isinstance(info_text, tuple):
        info_text = info_text[0]

    text = info_text.replace("\r", "")
    parts = text.split("Negative prompt:")

    prompt = parts[0].strip()
    neg_prompt, rest = "", ""

    if len(parts) > 1:
        neg_and_rest = parts[1].split("Steps:")
        neg_prompt = neg_and_rest[0].strip()
        rest = "Steps:" + neg_and_rest[1] if len(neg_and_rest) > 1 else ""

    kv = dict(re.findall(r"(\w[\w ]*?):\s*([^,]+)", rest))

    result = {
        "prompt": prompt,
        "negative": neg_prompt,
        "steps": kv.get("Steps", ""),
        "sampler": kv.get("Sampler", ""),
        "cfg": kv.get("CFG scale", ""),
        "seed": kv.get("Seed", ""),
        "size": kv.get("Size", ""),
        "schedule": kv.get("Schedule type", ""),
    }
    return result


def extract_and_apply(img_path):
    """画像のメタ情報を抽出して返す"""
    if not img_path:
        return {}

    try:
        with Image.open(img_path) as im:
            info = images.read_info_from_image(im) or "(no metadata)"
    except Exception as e:
        return {"error": f"Failed to read info: {e}"}

    return parse_png_info(info)


def on_after_component(component, **_kwargs):
    """txt2imgタブにUIを追加"""
    if getattr(component, "elem_id", "") == "txt2img_script_container":
        with gr.Accordion(
            "Direct Img Info Input", open=False, elem_id="direct_i3_accordion"
        ):
            cache_state = gr.State([])
            index_state = gr.State(0)

            img = gr.Image(label="Drop image", type="filepath", elem_id="direct_i3_img")
            path_box = gr.Textbox(
                label="Image Path", interactive=False, elem_id="direct_i3_path_box"
            )
            info_box = gr.Textbox(
                label="Metadata (parsed)",
                lines=6,
                interactive=False,
                elem_id="direct_i3_info_box",
            )

            with gr.Row():
                prev_btn = gr.Button("←", elem_id="direct_i3_prev_btn")
                reapply_btn = gr.Button("Reapply", elem_id="direct_i3_reapply_btn")
                next_btn = gr.Button("→", elem_id="direct_i3_next_btn")

            # --- D&D時の処理 ---
            def on_image_dropped(img_path, cache, index):
                parsed = extract_and_apply(img_path)
                cache = cache or []
                cache.append(parsed)
                index = len(cache) - 1
                return cache, index, img_path, json.dumps(parsed, ensure_ascii=False)

            # 💡 修正: _js に JavaScript の実行コードを直接記述
            # arguments[3] は info_box の値（JSON文字列）
            js_on_upload = f"""
                (cache, index, path_box) => {{
                    // 数秒実行を遅延させる（GradioがDOMを更新するのを待つ）
                    setTimeout(() => {{ 
                        try {{
                            const info_box_parent = document.getElementById("direct_i3_info_box");
                            let info_box_value = "";

                            if (info_box_parent) {{
                                // 子要素の <textarea> を探す
                                const textarea = info_box_parent.querySelector('textarea');
                                
                                if (textarea) {{
                                    // <textarea>要素から value を取得
                                    info_box_value = textarea.value;
                                }}
                            }}

                            console.log("[Direct-i3] extract_and_apply result:", info_box_value);
                            
                            // 値が空でなければパースと適用
                            if (info_box_value) {{
                                const info = JSON.parse(info_box_value);
                                applyImageInfo(info);
                            }}
                        }} catch (e) {{
                            console.error("[Direct-i3] Failed to parse JSON on upload:", e);
                        }}
                    }}, 2000); // 待機

                    return [cache, index, path_box];
                }}
            """
            # Gradio 3.x以降では、引数を明示的に書いた方が安定します。
            img.upload(
                fn=on_image_dropped,
                inputs=[img, cache_state, index_state],
                outputs=[cache_state, index_state, path_box, info_box],
                _js=js_on_upload,
            )

            # --- Reapplyボタンの処理 ---
            # 💡 修正: info_box も outputs に含め、on_reapply 関数を定義
            def on_reapply(cache, index):
                if not cache or index >= len(cache):
                    return cache, json.dumps({}, ensure_ascii=False)

                info_dict = cache[index]
                return cache, json.dumps(info_dict, ensure_ascii=False)  # 戻り値は2つ

            # 💡 修正: _js に JavaScript の実行コードを直接記述
            # arguments[1] は info_box の値（JSON文字列）
            js_on_reapply = """
            (cache, info_box) => {{
                // Gradio が info_box を更新するのを待つ
                setTimeout(() => {{
                    try {{
                        const info_box_parent = document.getElementById("direct_i3_info_box");
                        let info_box_value = "";

                        if (info_box_parent) {{
                            // 子要素の <textarea> を探す
                            const textarea = info_box_parent.querySelector('textarea');
                            if (textarea) {{
                                // <textarea>要素から value を取得
                                info_box_value = textarea.value;
                            }}
                        }}

                        console.log("[Direct-i3] reapply extract result:", info_box_value);

                        // 値が空でなければパースと適用
                        if (info_box_value) {{
                            const info = JSON.parse(info_box_value);
                            applyImageInfo(info);
                        }}
                    }} catch (e) {{
                        console.error("[Direct-i3] Failed to parse JSON on reapply:", e);
                    }}
                }}, 1500); // ボタン押下はuploadより遅延を短めにしてもOK（1〜1.5秒程度）

                // Pythonの引数をそのまま返す（これを忘れると ValueError になる）
                return [cache, info_box];
            }}
            """

            reapply_btn.click(
                fn=on_reapply,
                inputs=[cache_state, index_state],
                outputs=[cache_state, info_box],
                _js=js_on_reapply,
            )

        print("[Direct-i3] UI injected and ready!")  #


script_callbacks.on_after_component(on_after_component)
