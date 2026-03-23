import gradio as gr
from PIL import Image

def convert_to_grayscale(image):
    if image is None:
        raise gr.Error("Please upload an image first.")

    # Convert to PIL image
    img = Image.fromarray(image)

    # Convert to grayscale
    grayscale_img = img.convert("L")

    return grayscale_img, gr.Accordion(open=True)

def extract_image_details(image):
    if image is None:
        raise gr.Error("Please upload an image first.")

    img = Image.fromarray(image)

    width, height = img.size
    mode = img.mode
    format_info = img.format if img.format else "Unknown"

    details = f"""
    - Width: {width}px
    - Height: {height}px
    - Mode: {mode}
    - Format: {format_info}
    """

    return details, gr.Accordion(open=True)

with gr.Blocks() as app:
    with gr.Row():
        gr.Markdown("# 📷 Image Processing App")
        dark_theme = gr.Button("🌑 Dark", size="sm", scale=0)
        light_theme = gr.Button("☀️ Light", size="sm", scale=0)

    gr.Markdown("### Upload an image you would like to process")

    dark_theme.click(
        None,
        None,
        None,
        js="""
        () => {
            const url = new URL(window.location);
            url.searchParams.set('__theme', 'dark');
            window.location = url.toString();
        }
        """
    )

    light_theme.click(
        None,
        None,
        None,
        js="""
        () => {
            const url = new URL(window.location);
            url.searchParams.set('__theme', 'light');
            window.location = url.toString();
        }
        """
    )

    with gr.Row():
        image_input = gr.Image(
            show_label=False,
            type="numpy"
        )

    with gr.Row():
        grayscale_button = gr.Button(
            "Convert to Grayscale", 
            variant="primary"
        )
        details_button = gr.Button("Show Image Details")
        
    with gr.Row():
        with gr.Accordion(open=False, label="Processed Image") as image_accordion:
            image_output = gr.Image(show_label=False)
        with gr.Accordion(open=False, label="Image Details") as details_accordion:
            details_output = gr.Textbox(show_label=False)

    ##########
    # Events #
    ##########
    grayscale_button.click(
        fn=convert_to_grayscale,
        inputs=image_input,
        outputs=[image_output, image_accordion]
    )

    details_button.click(
        fn=extract_image_details,
        inputs=image_input,
        outputs=[details_output, details_accordion]
    )

app.launch(theme=gr.themes.Soft(primary_hue="blue"))