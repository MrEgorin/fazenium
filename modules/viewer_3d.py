"""
FAZENIUM — 3D Molecular Viewer (3Dmol.js via JavaScript CDN)
Replaces py3Dmol/stmol with direct 3Dmol.js for better mobile & web support.
"""
import streamlit as st
import streamlit.components.v1 as components
import json
import html as html_mod


# ─── CDN for 3Dmol.js ──────────────────────────────────
_3DMOL_CDN = "https://3dmol.csb.pitt.edu/build/3Dmol-min.js"


def _escape_pdb(pdb_text: str) -> str:
    """Escape PDB text for safe embedding in JavaScript template literal."""
    return (pdb_text
            .replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("${", "\\${"))


def render_3d_viewer(pdb_text: str, style: str = "cartoon", color: str = "spectrum",
                     show_surface: bool = False, spin: bool = False, width: int = 700, height: int = 500):
    """Render an interactive 3D molecular viewer using 3Dmol.js.

    Args:
        pdb_text: PDB file contents as string.
        style: Rendering style — cartoon, stick, sphere, line, cross.
        color: Coloring scheme — spectrum, chain, ssType, Jmol.
        show_surface: Whether to overlay a translucent VDW surface.
        spin: Whether to enable spin animation.
        width: Viewer width in pixels.
        height: Viewer height in pixels.
    """
    # Build style JSON for 3Dmol.js
    if style == "cartoon":
        if color in ["spectrum", "chain", "ssType"]:
            style_js = json.dumps({"cartoon": {"colorscheme": color}})
        else:
            style_js = json.dumps({"cartoon": {"color": color}})
    elif style == "stick":
        cs = color if color != "spectrum" else "Jmol"
        style_js = json.dumps({"stick": {"colorscheme": cs}})
    elif style == "sphere":
        cs = color if color != "spectrum" else "Jmol"
        style_js = json.dumps({"sphere": {"colorscheme": cs, "scale": 0.3}})
    elif style == "line":
        cs = color if color != "spectrum" else "Jmol"
        style_js = json.dumps({"line": {"colorscheme": cs}})
    elif style == "cross":
        cs = color if color != "spectrum" else "Jmol"
        style_js = json.dumps({"cross": {"colorscheme": cs}})
    else:
        style_js = json.dumps({"cartoon": {"colorscheme": "spectrum"}})

    surface_js = ""
    if show_surface:
        surface_js = 'viewer.addSurface($3Dmol.VDW, {opacity: 0.5, color: "white"});'

    spin_js = "viewer.spin(true);" if spin else "viewer.spin(false);"

    escaped_pdb = _escape_pdb(pdb_text)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="{_3DMOL_CDN}"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; overflow: hidden; }}
            #viewer-container {{
                width: 100%;
                height: {height}px;
                position: relative;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid rgba(0, 240, 255, 0.15);
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            }}
        </style>
    </head>
    <body>
        <div id="viewer-container"></div>
        <script>
            (function() {{
                var pdbData = `{escaped_pdb}`;
                var container = document.getElementById('viewer-container');
                var viewer = $3Dmol.createViewer(container, {{
                    backgroundColor: '#F5F5F7',
                    antialias: true,
                    cartoonQuality: 10
                }});
                viewer.addModel(pdbData, 'pdb');
                viewer.setStyle({{}}, {style_js});
                {surface_js}
                {spin_js}
                viewer.zoomTo();
                viewer.render();
                viewer.enableTouch();
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height + 10, scrolling=False)


def render_pocket_viewer(pdb_text: str, pockets: list,
                         width: int = 720, height: int = 500):
    """Render 3D view with binding-site pockets highlighted."""
    colors = ["#00F0FF", "#39FF14", "#FF6B6B", "#FFE66D", "#A78BFA"]
    pocket_js_lines = []
    for i, pocket in enumerate(pockets):
        c = pocket["center"]
        clr = colors[i % len(colors)]
        pocket_js_lines.append(f"""
            viewer.addSphere({{
                center: {{x: {c['x']}, y: {c['y']}, z: {c['z']}}},
                radius: 5,
                color: '{clr}',
                opacity: 0.4
            }});
            viewer.addLabel('P{i + 1}', {{
                position: {{x: {c['x']}, y: {c['y'] + 6}, z: {c['z']}}},
                fontColor: '{clr}',
                backgroundColor: 'transparent',
                fontSize: 14,
                fontOpacity: 1
            }});
        """)
    pockets_js = "\n".join(pocket_js_lines)
    escaped_pdb = _escape_pdb(pdb_text)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="{_3DMOL_CDN}"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; overflow: hidden; }}
            #viewer-container {{
                width: 100%; height: {height}px; position: relative;
                border-radius: 12px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.05);
            }}
        </style>
    </head>
    <body>
        <div id="viewer-container"></div>
        <script>
            (function() {{
                var pdbData = `{escaped_pdb}`;
                var container = document.getElementById('viewer-container');
                var viewer = $3Dmol.createViewer(container, {{
                    backgroundColor: '#F5F5F7',
                    antialias: true
                }});
                viewer.addModel(pdbData, 'pdb');
                viewer.setStyle({{}}, {{cartoon: {{colorscheme: 'spectrum', opacity: 0.7}}}});
                {pockets_js}
                viewer.zoomTo();
                viewer.render();
                viewer.enableTouch();
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height + 10, scrolling=False)


def render_md_trajectory(pdb_multi_model: str, width: int = 700, height: int = 450):
    """Render a multi-model PDB file as a molecular dynamics animation."""
    escaped_pdb = _escape_pdb(pdb_multi_model)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="{_3DMOL_CDN}"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; overflow: hidden; }}
            #viewer-container {{
                width: 100%; height: {height}px; position: relative;
                border-radius: 12px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.05);
            }}
        </style>
    </head>
    <body>
        <div id="viewer-container"></div>
        <script>
            (function() {{
                var pdbData = `{escaped_pdb}`;
                var container = document.getElementById('viewer-container');
                var viewer = $3Dmol.createViewer(container, {{
                    backgroundColor: '#F5F5F7',
                    antialias: true
                }});
                viewer.addModelsAsFrames(pdbData, 'pdb');
                viewer.setStyle({{}}, {{cartoon: {{colorscheme: 'spectrum', style: 'trace'}}, line: {{}}}});
                viewer.zoomTo();
                viewer.animate({{loop: "forward", step: 1, interval: 100}});
                viewer.render();
                viewer.enableTouch();
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height + 10, scrolling=False)


def render_docking_result(receptor_pdb: str, ligand_molblock: str, width: int = 700, height: int = 500):
    """Render a receptor protein and a docked ligand."""
    escaped_rec = _escape_pdb(receptor_pdb)
    escaped_lig = _escape_pdb(ligand_molblock)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="{_3DMOL_CDN}"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; overflow: hidden; }}
            #viewer-container {{
                width: 100%; height: {height}px; position: relative;
                border-radius: 12px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.05);
            }}
        </style>
    </head>
    <body>
        <div id="viewer-container"></div>
        <script>
            (function() {{
                var recData = `{escaped_rec}`;
                var ligData = `{escaped_lig}`;
                var container = document.getElementById('viewer-container');
                var viewer = $3Dmol.createViewer(container, {{
                    backgroundColor: '#F5F5F7',
                    antialias: true
                }});
                var m1 = viewer.addModel(recData, 'pdb');
                viewer.setStyle({{model: m1.getID()}}, {{cartoon: {{color: 'lightgrey', opacity: 0.5}}, surface: {{opacity: 0.1, color: 'grey'}}}});
                var m2 = viewer.addModel(ligData, 'sdf');
                viewer.setStyle({{model: m2.getID()}}, {{stick: {{colorscheme: 'Jmol', radius: 0.25}}}});
                viewer.zoomTo({{model: m2.getID()}});
                viewer.render();
                viewer.enableTouch();
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height + 10, scrolling=False)
