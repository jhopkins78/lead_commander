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

# --- Simple Login System ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login_form():
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

if not st.session_state.get("authenticated", False):
    login_form()
else:
    # Add Logout button to sidebar
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()

# Set Streamlit page config
st.set_page_config(
    page_title="Lead Commander",
    layout="wide",
    initial_sidebar_state="expanded"
)

if st.session_state.get("authenticated", False):

    # Sidebar navigation and dark mode toggle
    st.sidebar.title("Lead Commander")
    st.sidebar.markdown(
        '<div style="font-size: 0.9em; color: #888; margin-bottom: 10px;">Lead Commander is currently in <b>Beta</b>. Some features may change.</div>',
        unsafe_allow_html=True
    )
    dark_mode = st.sidebar.checkbox("Dark Mode", value=False)
    menu = st.sidebar.selectbox(
        "Navigate",
        [
            "Upload Leads",
            "View Leads",
            "Optimize Pipeline",
            "Automate Actions",
            "Coaching Tips"
        ]
    )

    # Welcome message at the top of the dashboard
    st.markdown("**Welcome to Lead Commander — Your AI-Driven Lead Optimization Hub**")
    st.markdown("")
    st.markdown("---")

    # Initialize session state for uploaded leads and filters
    if "uploaded_leads" not in st.session_state:
        st.session_state["uploaded_leads"] = None
    if "filters" not in st.session_state:
        st.session_state["filters"] = {
            "score": (0, 100),
            "win_probability": (0, 100),
            "market_signal_only": False,
            "recommended_actions": [],
        }

    # Dynamic CSS for light/dark mode and executive styling
    def inject_css(dark_mode: bool):
        if dark_mode:
            bg_color = "#121212"
            text_color = "#f8f9fa"
            header_color = "#00b4d8"
            subheader_color = "#48cae4"
        else:
            bg_color = "#f8f9fa"
            text_color = "#212529"
            header_color = "#0077b6"
            subheader_color = "#48cae4"
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
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    inject_css(dark_mode)

    # Set your backend base URL here (update as needed)
    API_BASE_URL = "http://localhost:8000/leads"

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
                st.markdown("**Preview:**")
                styled_dataframe(df.head(5))
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    elif st.session_state["uploaded_leads"] is not None:
        df = st.session_state["uploaded_leads"]
        st.info(f"{len(df)} leads currently loaded from previous upload.")
        st.markdown(f"**Columns detected:** {', '.join(df.columns)}")
        st.markdown("---")
        st.markdown("**Preview:**")
        styled_dataframe(df.head(5))
    st.markdown("---")

elif menu == "View Leads":
    section_header("View Leads")
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
    if not df.empty:
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        styled_dataframe(filtered)
    st.markdown("---")

elif menu == "Optimize Pipeline":
    section_header("Optimize Pipeline")
    if st.session_state["uploaded_leads"] is not None:
        leads = st.session_state["uploaded_leads"].to_dict(orient="records")
        optimized = call_api("/optimize_pipeline", method="POST", payload=leads)
        if optimized is not None and isinstance(optimized, list) and len(optimized) > 0:
            df = pd.DataFrame(optimized)
        else:
            df = pd.DataFrame()
    else:
        leads = call_api("/get_leads", method="GET")
        if leads is not None and isinstance(leads, list) and len(leads) > 0:
            optimized = call_api("/optimize_pipeline", method="POST", payload=leads)
            if optimized is not None and isinstance(optimized, list) and len(optimized) > 0:
                df = pd.DataFrame(optimized)
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
    if not df.empty:
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        styled_dataframe(filtered)
    st.markdown("---")

elif menu == "Automate Actions":
    section_header("Automate Actions")
    if st.session_state["uploaded_leads"] is not None:
        leads = st.session_state["uploaded_leads"].to_dict(orient="records")
        automated = call_api("/automate_actions", method="POST", payload=leads)
        if automated is not None and isinstance(automated, list) and len(automated) > 0:
            df = pd.DataFrame(automated)
        else:
            df = pd.DataFrame()
    else:
        leads = call_api("/get_leads", method="GET")
        if leads is not None and isinstance(leads, list) and len(leads) > 0:
            automated = call_api("/automate_actions", method="POST", payload=leads)
            if automated is not None and isinstance(automated, list) and len(automated) > 0:
                df = pd.DataFrame(automated)
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
    if not df.empty:
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        styled_dataframe(filtered)
    st.markdown("---")

elif menu == "Coaching Tips":
    section_header("Coaching Tips")
    if st.session_state["uploaded_leads"] is not None:
        leads = st.session_state["uploaded_leads"].to_dict(orient="records")
        coached = call_api("/generate_coaching", method="POST", payload=leads)
        if coached is not None and isinstance(coached, list) and len(coached) > 0:
            df = pd.DataFrame(coached)
        else:
            df = pd.DataFrame()
    else:
        leads = call_api("/get_leads", method="GET")
        if leads is not None and isinstance(leads, list) and len(leads) > 0:
            coached = call_api("/generate_coaching", method="POST", payload=leads)
            if coached is not None and isinstance(coached, list) and len(coached) > 0:
                df = pd.DataFrame(coached)
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
    if not df.empty:
        show_filters(df)
        filtered = apply_filters(df)
        st.markdown(f"**Showing {len(filtered)} out of {len(df)} leads**")
        styled_dataframe(filtered)
    st.markdown("---")
