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
                Notification();
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
                Notification();
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

function Notification() {
    // visible toast notification
    const toast = document.createElement("div");
    toast.innerText = "Applied metadta from the image";
    Object.assign(toast.style, {
        position: "fixed",
        top: "20px",
        right: "20px",
        background: "rgba(230, 90, 0, 0.9)",
        color: "white",
        padding: "10px 16px",
        borderRadius: "12px",
        fontSize: "14px",
        zIndex: 9999,
        opacity: "0",
        transition: "opacity 0.3s",
    });
    document.body.appendChild(toast);
    requestAnimationFrame(() => (toast.style.opacity = "1"));
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 2000);

    const root = gradioApp().shadowRoot || gradioApp();
    const box = root.querySelector("#direct_i3_info_box");

    if (!box) {
        console.warn("[Direct-i3] info_box not found for highlight");
        return;
    }

    // glow effect for info_box
    const textarea = box.querySelector("textarea") || box;
    textarea.style.transition = "background-color 0.5s";
    textarea.style.backgroundColor = "rgba(220, 80, 0, 0.6)",
        setTimeout(() => (textarea.style.backgroundColor = ""), 1000);
}