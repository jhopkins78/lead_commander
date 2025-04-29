# Lead Commander – UI Layout Overview

This document summarizes the Streamlit dashboard structure for Lead Commander, including pages, main sections, and key widgets.

---

## Dashboard Navigation

- **Sidebar Navigation**:  
  - Navigation selectbox for switching between main pages:
    - Upload Leads
    - View Leads
    - Optimize Pipeline
    - Automate Actions
    - Coaching Tips
  - Dark Mode toggle (checkbox)
  - Logout button (if authenticated)
  - Filters section (on relevant pages)

---

## Pages and Main Sections

### 1. Upload Leads

- **Main Sections:**
  - Section Header: "Upload Leads"
  - File Uploader: Upload a CSV file of leads
  - Clear Uploaded Leads button
  - Preview of uploaded leads (styled DataFrame)
  - Info/Success/Error messages for upload status

- **Key Widgets:**
  - `st.file_uploader` (CSV)
  - `st.button` ("Clear Uploaded Leads")
  - `st.dataframe` (preview)
  - Markdown for columns detected

---

### 2. View Leads

- **Main Sections:**
  - Section Header: "View Leads"
  - Refresh Leads button (if no uploaded leads)
  - Optimize Pipeline button (styled, plus Streamlit button)
  - Table of leads (styled DataFrame, with score highlighting if present)
  - Filters (in sidebar)
  - Info/Success/Error messages

- **Key Widgets:**
  - `st.button` ("Refresh Leads", "Optimize Pipeline")
  - `st.dataframe` (main table)
  - Sidebar filters (see below)

---

### 3. Optimize Pipeline

- **Main Sections:**
  - Section Header: "Optimize Pipeline"
  - Table of optimized leads (styled DataFrame)
  - Filters (in sidebar)
  - Info/Success/Error messages

- **Key Widgets:**
  - `st.dataframe` (main table)
  - Sidebar filters

---

### 4. Automate Actions

- **Main Sections:**
  - Section Header: "Automate Actions"
  - Table of leads with automation status/results (styled DataFrame)
  - Filters (in sidebar)
  - Info/Success/Error messages

- **Key Widgets:**
  - `st.dataframe` (main table)
  - Sidebar filters

---

### 5. Coaching Tips

- **Main Sections:**
  - Section Header: "Coaching Tips"
  - Table of leads with coaching tips (styled DataFrame)
  - Filters (in sidebar)
  - Info/Success/Error messages

- **Key Widgets:**
  - `st.dataframe` (main table)
  - Sidebar filters

---

## Sidebar Filters (on data pages)

- **Score Range**: Slider (0–100)
- **Win Probability Range**: Slider (0–100)
- **Market Signal Only**: Checkbox
- **Recommended Actions**: Multiselect
- **Reset Filters**: Button

---

## Other UI Features

- **Login Form**:  
  - Username/password fields, login button, error/success messages
- **Custom CSS**:  
  - Light/dark mode, styled headers, tables, forms, and buttons
- **Session State**:  
  - Tracks authentication, uploaded leads, and filter settings

---

## Key Widgets and Their Roles

- **st.file_uploader**: Upload CSV leads
- **st.button**: Actions (clear, refresh, optimize, automate, logout, reset filters)
- **st.dataframe**: Display and style lead tables
- **st.sidebar.selectbox**: Navigation
- **st.sidebar.checkbox**: Dark mode, market signal filter
- **st.sidebar.slider**: Score and win probability filters
- **st.sidebar.multiselect**: Recommended actions filter
- **st.form**: Login form

---

This layout provides a clear, modular structure for future UI improvements and feature additions.
