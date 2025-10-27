onUiLoaded(() => {
    console.log("[Direct-i3] JS loaded.");
});

// --------------------------------------------------
// メタ情報を txt2img に反映する処理
// --------------------------------------------------
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