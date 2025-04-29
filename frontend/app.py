"""
app.py
------
Streamlit frontend for Lead Commander.

Features:
- Sidebar navigation for different pipeline stages.
- call_api helper for backend interaction.
- Pages: Upload Leads, View Leads, Optimize Pipeline, Automate Actions, Coaching Tips.
- Light/dark mode toggle, custom CSS, polished headers, and styled DataFrames.
- CSV upload, session state, dynamic data source switching, and advanced sidebar filters.
"""

import streamlit as st
import requests
import pandas as pd
import io
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
import sys

# Import RelationshipMappingAgent from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lead_commander_backend', 'app', 'agents')))
RelationshipMappingAgent = None
try:
    from relationship_mapping_agent import RelationshipMappingAgent
except Exception:
    # If import fails, RelationshipMappingAgent remains None
    pass

# Set your backend base URL here (update as needed)
API_BASE_URL = "https://lead-commander.onrender.com/leads"
BACKEND_URL = "https://lead-commander.onrender.com"

# Set Streamlit page config
st.set_page_config(
    page_title="Lead Commander",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "uploaded_leads" not in st.session_state:
    st.session_state["uploaded_leads"] = None
if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "score": (0, 100),
        "win_probability": (0, 100),
        "market_signal_only": False,
        "recommended_actions": [],
    }

# --- Simple Login System ---

def login_form():
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; min-height: 30vh;">
        <div style="min-width: 340px; max-width: 400px; width: 100%;">
        """,
        unsafe_allow_html=True
    )
    st.title("Lead Commander Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if username == "admin" and password == "password123":
                st.session_state["authenticated"] = True
                st.success("Login successful!")
            else:
                st.session_state["authenticated"] = False
                st.error("Invalid username or password.")
    st.markdown("</div></div>", unsafe_allow_html=True)

if not st.session_state.get("authenticated", False):
    login_form()
else:
    # Add Logout button to sidebar
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()

if st.session_state.get("authenticated", False):

    # Sidebar navigation and dark mode toggle
    st.sidebar.title("Lead Commander")
    st.sidebar.markdown(
        '<div style="font-size: 0.9em; color: #888; margin-bottom: 10px;">Lead Commander is currently in <b>Beta</b>. Some features may change.</div>',
        unsafe_allow_html=True
    )
    dark_mode = st.sidebar.checkbox("Dark Mode", value=False)

    # Welcome message at the top of the dashboard
    st.markdown("**Welcome to Lead Commander — Your AI-Driven Lead Optimization Hub**")
    st.markdown("")
    st.markdown("---")


    # Dynamic CSS for light/dark mode and executive styling
    def inject_css(dark_mode: bool):
        if dark_mode:
            bg_color = "#121212"
            text_color = "#f8f9fa"
            header_color = "#00b4d8"
            subheader_color = "#48cae4"
            table_bg = "#181a1b"
            table_hover = "#23272b"
            input_bg = "#23272b"
            input_border = "#444"
            button_bg = "#00b4d8"
            button_text = "#fff"
            divider_color = "#222"
        else:
            bg_color = "#f8f9fa"
            text_color = "#212529"
            header_color = "#0077b6"
            subheader_color = "#48cae4"
            table_bg = "#fff"
            table_hover = "#f1f3f4"
            input_bg = "#fff"
            input_border = "#ccc"
            button_bg = "#0077b6"
            button_text = "#fff"
            divider_color = "#e0e0e0"
        css = f"""
        <style>
        html, body, [class*="st-"] {{
            font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        .stApp {{
            background-color: {bg_color} !important;
        }}
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: {header_color} !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }}
        .section-header {{
            font-size: 2rem;
            font-weight: 700;
            color: {header_color};
            margin-bottom: 0.4rem;
            margin-top: 1.5rem;
        }}
        .section-underline {{
            border: none;
            height: 3px;
            background: linear-gradient(90deg, {header_color} 0%, {subheader_color} 100%);
            margin-bottom: 1.2rem;
            margin-top: 0.1rem;
            width: 100%;
        }}
        /* Table Styling */
        .stDataFrame, .stTable {{
            border-radius: 10px !important;
            overflow: hidden !important;
            background: {table_bg} !important;
        }}
        .stDataFrame tbody tr:hover {{
            background: {table_hover} !important;
            transition: background 0.2s;
        }}
        .stDataFrame th, .stDataFrame td {{
            padding: 0.7em 1.2em !important;
            font-size: 1.05em !important;
        }}
        /* Login Form Styling */
        .stForm {{
            padding: 2em 2em 1em 2em !important;
            border-radius: 12px !important;
            background: {table_bg} !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            margin-bottom: 2em !important;
        }}
        .stTextInput > div > div > input {{
            background: {input_bg} !important;
            border: 1.5px solid {input_border} !important;
            border-radius: 8px !important;
            padding: 0.7em 1em !important;
            font-size: 1.1em !important;
        }}
        .stButton button {{
            background: {button_bg} !important;
            color: {button_text} !important;
            border-radius: 8px !important;
            padding: 0.6em 1.5em !important;
            font-size: 1.1em !important;
            border: none !important;
            margin-top: 0.5em !important;
        }}
        /* Upload Section Styling */
        .stFileUploader {{
            padding: 1.2em 1em 1.2em 1em !important;
            border-radius: 10px !important;
            background: {table_bg} !important;
            margin-bottom: 1.2em !important;
        }}
        /* Section Divider */
        hr, .stMarkdown hr {{
            border: none;
            border-top: 2px solid {divider_color};
            margin: 2em 0 1.5em 0;
        }}
        /* General Margin Consistency */
        .block-container {{
            padding-top: 2.5rem !important;
            padding-bottom: 2.5rem !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    inject_css(dark_mode)


def call_api(endpoint: str, method="GET", payload=None):
    """
    Helper to call backend API endpoints.
    Args:
        endpoint (str): API endpoint (e.g., "/get_leads")
        method (str): "GET" or "POST"
        payload (dict or list): Data to send for POST requests
    Returns:
        Parsed JSON response or None on error.
    """
    url = API_BASE_URL + endpoint
    try:
        with st.spinner("Processing leads..."):
            if method == "GET":
                resp = requests.get(url)
            elif method == "POST":
                resp = requests.post(url, json=payload)
            else:
                st.error(f"Unsupported HTTP method: {method}")
                return None
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        st.error("Unable to process request. Please try again later.")
        return None

def section_header(title: str):
    st.markdown("")
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-underline"></div>', unsafe_allow_html=True)
    st.markdown("")

def styled_dataframe(df: pd.DataFrame):
    # Highlight important columns if present
    highlight_cols = {
        "win_probability": "#ffe066",
        "estimated_revenue": "#b5ead7",
        "market_signal": "#f7b2ad",
        "coaching_tip": "#b2c7f7",
        "automation_status": "#f7e6ad",
        "recommended_action": "#b2f7c7"
    }
    def highlight(s):
        return [
            f"background-color: {highlight_cols.get(col, '')}; font-weight: 600;" if col in highlight_cols else ""
            for col in s.index
        ]
    styled = df.style.apply(highlight, axis=1)
    st.dataframe(
        styled,
        use_container_width=True,
        height=min(600, 40 + 35 * len(df)),
        hide_index=True
    )

def show_filters(df: pd.DataFrame):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    # Reset button
    if st.sidebar.button("Reset Filters"):
        st.session_state["filters"] = {
            "score": (0, 100),
            "win_probability": (0, 100),
            "market_signal_only": False,
            "recommended_actions": [],
        }
    # Score slider
    min_score, max_score = int(df.get("score", pd.Series([0])).min()), int(df.get("score", pd.Series([100])).max())
    score_range = st.sidebar.slider("Score Range", 0, 100, st.session_state["filters"]["score"])
    st.session_state["filters"]["score"] = score_range
    # Win probability slider
    if "win_probability" in df.columns:
        min_wp, max_wp = int(df["win_probability"].min()), int(df["win_probability"].max())
    else:
        min_wp, max_wp = 0, 100
    wp_range = st.sidebar.slider("Win Probability Range", 0, 100, st.session_state["filters"]["win_probability"])
    st.session_state["filters"]["win_probability"] = wp_range
    # Market signal checkbox
    ms_only = st.sidebar.checkbox("Show Only Leads with Market Signals", value=st.session_state["filters"]["market_signal_only"])
    st.session_state["filters"]["market_signal_only"] = ms_only
    # Recommended actions multiselect
    actions = []
    if "recommended_action" in df.columns:
        actions = sorted(df["recommended_action"].dropna().unique())
    rec_actions = st.sidebar.multiselect("Recommended Actions", actions, default=st.session_state["filters"]["recommended_actions"])
    st.session_state["filters"]["recommended_actions"] = rec_actions

def apply_filters(df: pd.DataFrame):
    f = st.session_state["filters"]
    # Score filter
    if "score" in df.columns:
        df = df[(df["score"] >= f["score"][0]) & (df["score"] <= f["score"][1])]
    # Win probability filter
    if "win_probability" in df.columns:
        df = df[(df["win_probability"] >= f["win_probability"][0]) & (df["win_probability"] <= f["win_probability"][1])]
    # Market signal filter
    if f["market_signal_only"] and "market_signal_detected" in df.columns:
        df = df[df["market_signal_detected"] == True]
    # Recommended actions filter
    if f["recommended_actions"] and "recommended_action" in df.columns:
        df = df[df["recommended_action"].isin(f["recommended_actions"])]
    return df

st.title("Lead Commander Dashboard")

# Sidebar navigation menu (inserted after login and dashboard title)
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Upload Leads",
        "View Leads",
        "Optimize Pipeline",
        "Automate Actions",
        "Coaching Tips",
        "Relationship Map"
    ]
)

if menu == "Upload Leads":
    section_header("Upload Leads")
    uploaded_file = st.file_uploader("Upload a CSV file of leads", type=["csv"])
    clear = st.button("Clear Uploaded Leads")
    if clear:
        st.session_state["uploaded_leads"] = None
        st.success("Uploaded leads cleared.")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Validate for 'name' or 'company' column
            cols = [c.lower() for c in df.columns]
            if "name" not in cols and "company" not in cols:
                st.error("Uploaded file must contain at least a 'name' or 'company' column.")
            else:
                st.session_state["uploaded_leads"] = df
                st.success(f"Uploaded {len(df)} leads.")
                st.markdown(f"**Columns detected:** {', '.join(df.columns)}")
                st.markdown("---")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

elif menu == "Relationship Map":
    section_header("Relationship Map")
    if RelationshipMappingAgent is None:
        st.error("RelationshipMappingAgent could not be imported. Please check backend integration.")
    else:
        # Step 1: Prepare lead data
        if st.session_state["uploaded_leads"] is not None:
            leads_df = st.session_state["uploaded_leads"]
        else:
            leads = call_api("/get_leads", method="GET")
            if leads is not None and isinstance(leads, list) and len(leads) > 0:
                leads_df = pd.DataFrame(leads)
            else:
                leads_df = pd.DataFrame()
        if leads_df.empty:
            st.info("No leads available to visualize.")
        else:
            # Ensure required columns exist
            if "id" not in leads_df.columns:
                leads_df = leads_df.reset_index().rename(columns={"index": "id"})
            # Fill missing risk_score and projected_ltv with defaults
            if "risk_score" not in leads_df.columns:
                leads_df["risk_score"] = 0.0
            if "projected_ltv" not in leads_df.columns:
                leads_df["projected_ltv"] = 100.0
            # Step 2: Generate relationships
            leads_list = leads_df.to_dict(orient="records")
            agent = RelationshipMappingAgent()
            relationships = agent.run(leads_list)
            lead_data = {str(lead["id"]): lead for lead in leads_list}
            # Step 3: Build pyvis network
            net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=False)
            for lead_id, data in relationships.items():
                lead = lead_data.get(str(lead_id)) or lead_data.get(lead_id)
                if not lead:
                    continue
                risk = lead.get("risk_score", 0.0)
                ltv = lead.get("projected_ltv", 100.0)
                name = lead.get("name", f"Lead {lead_id}")
                # Color by risk_score
                if risk < 0.4:
                    risk_color = "green"
                elif risk < 0.7:
                    risk_color = "yellow"
                else:
                    risk_color = "red"
                # Node size by projected_ltv (min 10, max 60)
                node_size = max(10, min(60, ltv / 100 * 30 + 20))
                tooltip = f"{name}<br>Risk: {risk:.2f}<br>LTV: ${ltv:,.2f}"
                net.add_node(
                    lead_id,
                    label=name,
                    color=risk_color,
                    size=node_size,
                    title=tooltip
                )
                for connection_id in data.get("connections", []):
                    net.add_edge(lead_id, connection_id)
            net.toggle_physics(True)
            net.set_options("""
            var options = {
              "nodes": {
                "borderWidth": 2,
                "shadow": true
              },
              "edges": {
                "color": {
                  "inherit": true
                },
                "smooth": false
              },
              "interaction": {
                "hover": true,
                "navigationButtons": true,
                "keyboard": true
              },
              "physics": {
                "enabled": true,
                "barnesHut": {
                  "gravitationalConstant": -8000,
                  "centralGravity": 0.3,
                  "springLength": 95,
                  "springConstant": 0.04,
                  "damping": 0.09,
                  "avoidOverlap": 0.1
                }
              }
            }
            """)
            # Step 4: Save and display
            with tempfile.NamedTemporaryFile("w+", suffix=".html", delete=False) as tmp_file:
                net.save_graph(tmp_file.name)
                tmp_file.flush()
                components.iframe(tmp_file.name, height=600, scrolling=True)
            st.caption("Pan, zoom, and hover nodes for details. Node color = risk, size = LTV.")

elif menu == "View Leads":
    section_header("View Leads")
    optimize_clicked = False
    if st.session_state["uploaded_leads"] is not None:
        st.info("Viewing uploaded leads")
        df = st.session_state["uploaded_leads"]
    else:
        if st.button("Refresh Leads"):
            leads = call_api("/get_leads", method="GET")
        else:
            leads = call_api("/get_leads", method="GET")
        if leads is not None and isinstance(leads, list) and len(leads) > 0:
            df = pd.DataFrame(leads)
        else:
            df = pd.DataFrame()
    # Optimize Pipeline Button
    if not df.empty:
        st.markdown(
            "<div style='display: flex; justify-content: flex-end; margin-bottom: 0.5em;'>"
            "<button id='optimize-btn' style='background: #00b4d8; color: #fff; border: none; border-radius: 8px; padding: 0.6em 1.5em; font-size: 1.1em; cursor: pointer;'>Optimize Pipeline</button>"
            "</div>",
            unsafe_allow_html=True
        )
        optimize_clicked = st.button("Optimize Pipeline", key="optimize_pipeline_btn")
    # Optimization logic
    if not df.empty and optimize_clicked:
        with st.spinner("Optimizing leads..."):
            try:
                # Send to backend /optimize endpoint
                leads_json = df.to_dict(orient="records")
                import requests
                response = requests.post(
                    BACKEND_URL + "/optimize",
                    json=leads_json,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                if response.status_code == 200:
                    scored_leads = response.json()
                    df = pd.DataFrame(scored_leads)
                    st.session_state["uploaded_leads"] = df
                    st.success("Leads optimized and scored!")
                else:
                    st.error("Optimization failed. Please try again.")
            except Exception as e:
                st.error(f"Error optimizing leads: {e}")
    if not df.empty:
        show_filters(df)
        filtered = apply_filters(df)
        # Style Score column if present
        if "Score" in filtered.columns:
            def highlight_score(val):
                color = "#ffe066" if val >= filtered["Score"].max() * 0.7 else "#fff3cd"
                return f"background-color: {color}; font-weight: 700; color: #333;"
            styled = filtered.style.applymap(highlight_score, subset=["Score"])
            st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
            st.dataframe(
                styled,
                use_container_width=True,
                height=min(600, 40 + 35 * len(filtered)),
                hide_index=True
            )
        else:
            st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
            styled_dataframe(filtered)
    st.markdown("---")

elif menu == "Optimize Pipeline":
    section_header("Optimize Pipeline")
    # Use session_state to cache optimized leads
    if "optimized_leads" not in st.session_state:
        st.session_state["optimized_leads"] = None
    leads = None
    if st.session_state["uploaded_leads"] is not None:
        leads = st.session_state["uploaded_leads"].to_dict(orient="records")
    else:
        api_leads = call_api("/get_leads", method="GET")
        if api_leads is not None and isinstance(api_leads, list) and len(api_leads) > 0:
            leads = api_leads
    df = pd.DataFrame()
    if leads is not None:
        try:
            if st.session_state["optimized_leads"] is not None:
                optimized = st.session_state["optimized_leads"]
            else:
                optimized = call_api("/optimize_pipeline", method="POST", payload=leads)
                if optimized is not None and isinstance(optimized, list) and len(optimized) > 0:
                    st.session_state["optimized_leads"] = optimized
            if optimized is not None and isinstance(optimized, list) and len(optimized) > 0:
                df = pd.DataFrame(optimized)
        except Exception as e:
            st.error(f"Pipeline optimization failed: {e}")
    if not df.empty:
        # Ensure required columns
        required_cols = ["Lead Name", "Score", "Win Probability", "Risk Score", "Projected LTV", "Recommended Action"]
        col_map = {
            "name": "Lead Name",
            "score": "Score",
            "win_probability": "Win Probability",
            "risk_score": "Risk Score",
            "projected_ltv": "Projected LTV",
            "recommended_action": "Recommended Action"
        }
        for orig, new in col_map.items():
            if orig in df.columns and new not in df.columns:
                df[new] = df[orig]
        df = df[[c for c in required_cols if c in df.columns]]
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        # Conditional styling: highlight high risk + high LTV
        def highlight_row(row):
            risk = row.get("Risk Score", 0)
            ltv = row.get("Projected LTV", 0)
            if risk >= 0.7 and ltv >= 100:
                return ["background-color: #ffb3b3; font-weight: 700"] * len(row)
            return ["" for _ in row]
        styled = filtered.style.apply(highlight_row, axis=1)
        st.dataframe(
            styled,
            use_container_width=True,
            height=min(600, 40 + 35 * len(filtered)),
            hide_index=True
        )
    else:
        st.info("No optimized pipeline data available.")
    st.markdown("---")

elif menu == "Automate Actions":
    section_header("Automate Actions")
    # Use session_state to cache automated actions
    if "automated_actions" not in st.session_state:
        st.session_state["automated_actions"] = None
    leads = None
    if st.session_state["uploaded_leads"] is not None:
        leads = st.session_state["uploaded_leads"].to_dict(orient="records")
    else:
        api_leads = call_api("/get_leads", method="GET")
        if api_leads is not None and isinstance(api_leads, list) and len(api_leads) > 0:
            leads = api_leads
    df = pd.DataFrame()
    if leads is not None:
        try:
            if st.session_state["automated_actions"] is not None:
                automated = st.session_state["automated_actions"]
            else:
                automated = call_api("/automate_actions", method="POST", payload=leads)
                # Use dummy data if backend returns nothing
                if not (automated and isinstance(automated, list) and len(automated) > 0):
                    automated = [
                        {
                            "Lead Name": lead.get("name", f"Lead {i+1}"),
                            "Last Action Taken": "Initial Outreach",
                            "Next Recommended Action": "Follow Up",
                            "Automation Status": "Pending"
                        }
                        for i, lead in enumerate(leads)
                    ]
                st.session_state["automated_actions"] = automated
            if automated is not None and isinstance(automated, list) and len(automated) > 0:
                df = pd.DataFrame(automated)
        except Exception as e:
            st.error(f"Automation agent failed: {e}")
    if not df.empty:
        # Ensure required columns
        required_cols = ["Lead Name", "Last Action Taken", "Next Recommended Action", "Automation Status"]
        col_map = {
            "name": "Lead Name",
            "last_action_taken": "Last Action Taken",
            "next_recommended_action": "Next Recommended Action",
            "automation_status": "Automation Status"
        }
        for orig, new in col_map.items():
            if orig in df.columns and new not in df.columns:
                df[new] = df[orig]
        df = df[[c for c in required_cols if c in df.columns]]
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        st.dataframe(
            filtered,
            use_container_width=True,
            height=min(600, 40 + 35 * len(filtered)),
            hide_index=True
        )
    else:
        st.info("No automated actions data available.")
    st.markdown("---")

elif menu == "Coaching Tips":
    section_header("Coaching Tips")
    # Use session_state to cache coaching tips
    if "coaching_tips" not in st.session_state:
        st.session_state["coaching_tips"] = None
    leads = None
    if st.session_state["uploaded_leads"] is not None:
        leads = st.session_state["uploaded_leads"].to_dict(orient="records")
    else:
        api_leads = call_api("/get_leads", method="GET")
        if api_leads is not None and isinstance(api_leads, list) and len(api_leads) > 0:
            leads = api_leads
    df = pd.DataFrame()
    if leads is not None:
        try:
            if st.session_state["coaching_tips"] is not None:
                coached = st.session_state["coaching_tips"]
            else:
                coached = call_api("/generate_coaching", method="POST", payload=leads)
                if not (coached and isinstance(coached, list) and len(coached) > 0):
                    coached = [
                        {
                            "Lead Name": lead.get("name", f"Lead {i+1}"),
                            "Coaching Tip Text": "No tip available."
                        }
                        for i, lead in enumerate(leads)
                    ]
                st.session_state["coaching_tips"] = coached
            if coached is not None and isinstance(coached, list) and len(coached) > 0:
                df = pd.DataFrame(coached)
        except Exception as e:
            st.error(f"Coaching agent failed: {e}")
    if not df.empty:
        # Ensure required columns
        required_cols = ["Lead Name", "Coaching Tip Text"]
        col_map = {
            "name": "Lead Name",
            "coaching_tip": "Coaching Tip Text"
        }
        for orig, new in col_map.items():
            if orig in df.columns and new not in df.columns:
                df[new] = df[orig]
        df = df[[c for c in required_cols if c in df.columns]]
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        st.dataframe(
            filtered,
            use_container_width=True,
            height=min(600, 40 + 35 * len(filtered)),
            hide_index=True
        )
    else:
        st.info("No coaching tips data available.")
    st.markdown("---")
