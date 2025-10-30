# Direct Img Info Input

A Stable Diffusion web ui extension for automatic metadata extraction from dropped images.

## Features

- Adds a new section labeled **"Direct Img Info Input"** to the `txt2img` tab.
- Accepts image drag-and-drop directly into the UI.
- If the dropped image contains extractable metadata (e.g. PNG info), it will automatically populate the corresponding fields in the web UI.
- Previously dropped images are cached, allowing you to navigate between them and reapply their metadata using navigation buttons.

## Notes

- Due to implementation constraints, there may be a short delay (approximately 2 seconds) between dropping an image or pressing the **Reapply** button and the fields being updated.

## Tested Environment

- **Stable Diffusion Web UI**: `v1.10.1` (`82a973c0`, 2024-07-27)
- **Browser**: Firefox
- **OS**: Windows 11