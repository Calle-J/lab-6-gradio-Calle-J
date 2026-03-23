import gradio as gr
import httpx
import pandas as pd

api_url = "http://127.0.0.1:8000"
species_url = f"{api_url}/species/"
birds_url = f"{api_url}/birds/"
sightings_url = f"{api_url}/birdspotting/"

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
        response = httpx.get(species_url)
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
    if not name or not scientific_name or not family or not conservation_status or wingspan_cm is None:
        raise gr.Error("Please fill in all required fields.")

    data = {
        "name": name,
        "scientific_name": scientific_name,
        "family": family,
        "conservation_status": conservation_status,
        "wingspan_cm": wingspan_cm
    }

    try:
        response = httpx.post(species_url, json=data)
        response.raise_for_status()
    except Exception as e:
        print("Error adding species:", e)
    
    return load_species("All")

def get_birds():
    try:
        response = httpx.get(birds_url)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        print("Error fetching birds:", e)
        return pd.DataFrame()

def load_birds():
    df = get_birds()
    df_species = get_species()

    if not df.empty:
        if not df_species.empty:
            species_subset = df_species[["id", "name"]].rename(columns={"id": "sid", "name": "species_name"})
            df = df.merge(species_subset, left_on="species_id", right_on="sid", how="left")
            df = df[["id", "nickname", "ring_code", "age", "species_name"]]
        else:
            df = df[["id", "nickname", "ring_code", "age", "species_id"]]

        df = df.rename(columns={
            "nickname": "Nickname",
            "ring_code": "Ring Code",
            "age": "Age",
            "species_id": "Species",
            "species_name": "Species"
        })
    return df

def add_bird(nickname, ring_code, age, species_name):
    if not nickname or not ring_code or age is None or not species_name:
        raise gr.Error("Please fill in all required fields.")

    species_df = get_species()
    species_id = None

    if not species_df.empty:
        match = species_df[species_df["name"] == species_name]
        if not match.empty:
            species_id = int(match.iloc[0]["id"])

    if species_id is None:
        print(f"Error: Species '{species_name}' not found.")
        return load_birds()

    data = {
        "nickname": nickname,
        "ring_code": ring_code,
        "age": age,
        "species_id": species_id
    }

    try:
        response = httpx.post(birds_url, json=data)
        response.raise_for_status()
    except Exception as e:
        print("Error adding bird:", e)
    
    return load_birds()

def get_species_choices():
    species_df = get_species()
    species_names = species_df["name"].tolist()

    if species_df.empty or "name" not in species_df.columns:
        return []

    return species_names

def refresh_species_choices():
    species_names = get_species_choices()
    return gr.Dropdown(choices=species_names)

def get_sightings():
    try:
        response = httpx.get(sightings_url)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        print("Error fetching sightings:", e)
        return pd.DataFrame()

def load_sightings(observer_name_filter=None):
    df = get_sightings()
    df_birds = get_birds()

    if not df.empty:
        if observer_name_filter:
            df = df[df["observer_name"].str.contains(observer_name_filter, case=False, na=False)]

        if not df_birds.empty:
            birds_subset = df_birds[["id", "nickname"]].rename(columns={"id": "bid", "nickname": "bird_nickname"})
            df = df.merge(birds_subset, left_on="bird_id", right_on="bid", how="left")
            df = df[["id", "bird_nickname", "spotted_at", "location", "observer_name", "notes"]]
            df = df.rename(columns={"bird_nickname": "Bird"})
        else:
            df = df[["id", "bird_id", "spotted_at", "location", "observer_name", "notes"]]

        df = df.rename(columns={
            "bird_id": "Bird",
            "spotted_at": "Spotted at",
            "location": "Location",
            "observer_name": "Observer name",
            "notes": "Notes"
        })
    return df

def add_sighting(bird_nickname, spotted_at, location, observer_name, notes):
    if not bird_nickname or not spotted_at or not location or not observer_name:
        raise gr.Error("Please fill in all required fields.")

    birds_df = get_birds()
    bird_id = None

    if not birds_df.empty:
        match = birds_df[birds_df["nickname"] == bird_nickname]
        if not match.empty:
            bird_id = int(match.iloc[0]["id"])

    if bird_id is None:
        print(f"Error: Bird '{bird_nickname}' not found.")
        return load_sightings()

    data = {
        "bird_id": bird_id,
        "spotted_at": spotted_at,
        "location": location,
        "observer_name": observer_name,
        "notes": notes
    }

    try:
        response = httpx.post(sightings_url, json=data)
        response.raise_for_status()
    except Exception as e:
        print("Error adding sighting:", e)
    
    return load_sightings()

def get_bird_choices():
    birds_df = get_birds()
    bird_nicknames = birds_df["nickname"].tolist()

    if birds_df.empty or "nickname" not in birds_df.columns:
        return []

    return bird_nicknames

def refresh_bird_choices():
    bird_nicknames = get_bird_choices()
    return gr.Dropdown(choices=bird_nicknames)

with gr.Blocks() as app:
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
            refresh_button_birds = gr.Button("🔄️ Refresh")
        
        with gr.Row():
            birds_table = gr.Dataframe(load_birds())
        
        with gr.Accordion("➕ Add new birds", open=False):
            with gr.Row():
                nickname = gr.Textbox(
                    label="Nickname", 
                    placeholder="e.g. Ghost"
                )
                ring_code = gr.Textbox(
                    label="Ring code",
                    placeholder="e.g. OWL-001"
                )
            
            with gr.Row():
                age = gr.Number(
                    label="Age (years)",
                    minimum=0,
                )
                species_options = gr.Dropdown(
                    label="Species",
                    choices=get_species_choices(),
                    interactive=True
                )
            
            with gr.Row():
                refresh_species_list = gr.Button("🔄️ Refresh species list", scale=1)
                create_bird_button = gr.Button(
                    "Create bird",
                    variant="primary",
                    scale=2
                )

    ################
    # Birds Events #
    ################
    refresh_button_birds.click(
        fn=load_birds,
        outputs=birds_table
    )
    
    refresh_species_list.click(
        fn=refresh_species_choices,
        outputs=species_options
    )
    
    create_bird_button.click(
        fn=add_bird,
        inputs=[nickname, ring_code, age, species_options],
        outputs=birds_table
    )

    #################
    # Sightings Tab #
    #################
    with gr.Tab("Sightings"):
        with gr.Row():
            observer_name_filter = gr.Textbox(
                label="Filter by observer name",
                placeholder="e.g. Carl",
                scale=2
            )
            refresh_button_sightings = gr.Button("🔄️ Refresh", scale=1)
        
        with gr.Row():
            sightings_table = gr.Dataframe(load_sightings())

        with gr.Accordion("➕ Add new sightings", open=False):
            with gr.Row():
                bird_options = gr.Dropdown(
                    label="Bird",
                    choices=get_bird_choices(),
                    interactive=True
                )
                refresh_bird_list = gr.Button("🔄️ Refresh bird list")
            
            with gr.Row():
                spotted_at = gr.Textbox(
                    label="Spotted at (ISO 8601)",
                    placeholder="e.g. 2026-03-23T19:08:00"
                )
                location = gr.Textbox(
                    label="Location",
                    placeholder="e.g. Stockholm"
                )

            with gr.Row():
                oberver_name =gr.Textbox(
                    label="Observer name",
                    placeholder="e.g. Carl Jonsson"
                )
                notes = gr.Textbox(
                    label="Notes (optional)",
                    placeholder="e.g. Flew past the tower in high speed"
                )
            
            with gr.Row():
                create_sighting_button = gr.Button(
                    "Create sighting",
                    variant="primary"
                )
    
    ####################
    # Sightings Events #
    ####################
    refresh_button_sightings.click(
        fn=load_sightings,
        inputs=observer_name_filter,
        outputs=sightings_table
    )
    
    refresh_bird_list.click(
        fn=refresh_bird_choices,
        outputs=bird_options
    )
    
    create_sighting_button.click(
        fn=add_sighting,
        inputs=[bird_options, spotted_at, location, oberver_name, notes],
        outputs=sightings_table
    )

app.launch(theme=gr.themes.Soft(primary_hue="blue"))