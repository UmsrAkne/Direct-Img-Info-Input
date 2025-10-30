onUiLoaded(() => {
    console.log("[Direct-i3] JS loaded.");
});

function direct_i3_on_upload(cache, index, path_box) {
    // wait for Gradio to update the DOM
    setTimeout(() => {
        try {
            const info_box_parent = document.getElementById("direct_i3_info_box");
            let info_box_value = "";

            if (info_box_parent) {
                const textarea = info_box_parent.querySelector("textarea");
                if (textarea) {
                    info_box_value = textarea.value;
                }
            }

            console.log("[Direct-i3] extract_and_apply result:", info_box_value);

            if (info_box_value) {
                const info = JSON.parse(info_box_value);
                applyImageInfo(info);
            }
        } catch (e) {
            console.error("[Direct-i3] Failed to parse JSON on upload:", e);
        }
    }, 2000);

    return [cache, index, path_box];
}

function direct_i3_on_click(cache, info_box) {
    // wait for Gradio to update the DOM
    setTimeout(() => {
        try {
            const info_box_parent = document.getElementById("direct_i3_info_box");
            let info_box_value = "";

            if (info_box_parent) {

                // find the child <textarea> element
                const textarea = info_box_parent.querySelector('textarea');
                if (textarea) {
                    // get value from <textarea> element
                    info_box_value = textarea.value;
                }
            }

            console.log("[Direct-i3] reapply extract result:", info_box_value);

            if (info_box_value) {
                const info = JSON.parse(info_box_value);
                applyImageInfo(info);
            }
        } catch (e) {
            console.error("[Direct-i3] Failed to parse JSON on reapply:", e);
        }
    }, 1500);

    // return the same arguments back to Python to avoid ValueError
    return [cache, info_box];
}

// apply extracted image info to txt2img fields
function applyImageInfo(info) {
    if (!info || typeof info !== "object") return;
    const gr = gradioApp();

    const setVal = (sel, val) => {
        const el = gr.querySelector(sel);
        if (el) {
            el.value = val;
            el.dispatchEvent(new Event("input"));
        }
    };

    console.log("[Direct-i3] Applying image info:", info);

    setVal("#txt2img_prompt textarea", info.prompt || "");
    setVal("#txt2img_neg_prompt textarea", info.negative || "");
    setVal("#txt2img_steps input", info.steps || "");
    setVal("#txt2img_cfg_scale input", info.cfg || "");
    setVal("#txt2img_seed input", info.seed || "");

    if (info.size && info.size.includes("x")) {
        const [w, h] = info.size.split("x");
        setVal("#txt2img_width input", w.trim());
        setVal("#txt2img_height input", h.trim());
    }
}