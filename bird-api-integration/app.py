import gradio as gr
import httpx
import pandas as pd

api_url = "http://127.0.0.1:8000"
species_get_url = f"{api_url}/species/"

conservation_statuses = [
    "Least Concern",
    "Near Threatened",
    "Vulnerable",
    "Endangered",
    "Critically Endangered",
    "Extinct in the Wild",
    "Extinct"
]

def get_species():
    try:
        response = httpx.get(species_get_url)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        print("Error fetching species:", e)
        return pd.DataFrame()

def load_species(status):
    df = get_species()

    if not df.empty:
        if status != "All":
            df = df[df["conservation_status"] == status]

        df = df[["id", "name", "scientific_name", "family", "conservation_status", "wingspan_cm"]]

        df = df.rename(columns={
            "name": "Name",
            "scientific_name": "Scientific Name",
            "family": "Family",
            "conservation_status": "Conservation Status",
            "wingspan_cm": "Wingspan (cm)"
        })
    return df

def add_species(name, scientific_name, family, conservation_status, wingspan_cm):
    data = {
        "name": name,
        "scientific_name": scientific_name,
        "family": family,
        "conservation_status": conservation_status,
        "wingspan_cm": wingspan_cm
    }

    try:
        response = httpx.post(species_get_url, json=data)
        response.raise_for_status()
    except Exception as e:
        print("Error adding species:", e)
    
    return load_species("All")
    

with gr.Blocks() as assignment:
    with gr.Row():
        gr.Markdown("# 🦅 Birds Viewer")
        dark_theme = gr.Button("🌑 Dark", size="sm", scale=0)
        light_theme = gr.Button("☀️ Light", size="sm", scale=0)

    gr.Markdown(f"### Live data from the Birds API at {api_url}")

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

    ###############
    # Species Tab #
    ###############
    with gr.Tab("Species"):
        with gr.Row():
            filter_status = gr.Dropdown(
                label="Filter by conservation status", 
                choices=["All"] + conservation_statuses,
                value="All",
                interactive=True,
                scale=2
            )

            refresh_button = gr.Button("🔄️ Refresh", scale=1)

        with gr.Row():
            species_table = gr.Dataframe(load_species("All"))
        
        with gr.Accordion("➕ Add new species", open=False):
            with gr.Row():
                name = gr.Textbox(
                    label="Name", 
                    placeholder="e.g. House Sparrow"
                )
                scientific_name = gr.Textbox(
                    label="Scientific Name",
                    placeholder="e.g. Passer domesticus"
                )

            with gr.Row():  
                family = gr.Textbox(
                    label="Family",
                    placeholder="e.g. Passeridae"
                )
                conservation_status = gr.Dropdown(
                    label="Conservation Status",
                    choices=conservation_statuses,
                    value="Least Concern",
                    interactive=True
                )
                wingspan_cm = gr.Slider(
                    label="Wingspan (cm)",
                    minimum=5,
                    maximum=300,
                    step=1,
                    value=5,
                    interactive=True
                )
            
            with gr.Row():
                add_button = gr.Button(
                    "Create species",
                    variant="primary"
                )
    
    ##################
    # Species Events #
    ##################
    refresh_button.click(
        fn=load_species, 
        inputs=filter_status, 
        outputs=species_table
    )

    add_button.click(
        fn=add_species, 
        inputs=[name, scientific_name, family, conservation_status, wingspan_cm], 
        outputs=species_table
    )

    #############
    # Birds Tab #
    #############
    with gr.Tab("Birds"):
        with gr.Row():
            placeholder = gr.Markdown("## Will be implemented soon!")

    #################
    # Sightings Tab #
    #################
    with gr.Tab("Sightings"):
        with gr.Row():
            placeholder = gr.Markdown("## Will be implemented soon!")

assignment.launch(theme=gr.themes.Soft(primary_hue="blue"))