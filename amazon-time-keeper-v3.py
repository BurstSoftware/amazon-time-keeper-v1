import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Amazon Weekly Hours Tracker",
    page_icon="📦",
    layout="centered"
)

# Custom CSS for better alignment and dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .main-header {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .sub-header {
        color: #aaaaaa;
        margin-bottom: 30px;
    }
    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin: 25px 0 15px 0;
    }
    .stButton>button {
        height: 48px;
        font-weight: 600;
    }
    .add-btn {
        background-color: #ff4d4d !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    .metric-card {
        background-color: #1e242f;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📦 Amazon Weekly Hours Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enter shifts with custom dates • Multiple shifts supported • Export to CSV</p>', unsafe_allow_html=True)

# Initialize session state
if "all_shifts" not in st.session_state:
    st.session_state.all_shifts = []

def calculate_hours(start: str, end: str) -> float:
    if not start or not end:
        return 0.0
    try:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        if e < s:
            e += timedelta(days=1)
        return round((e - s).total_seconds() / 3600, 2)
    except:
        return 0.0

# ====================== ADD NEW SHIFT SECTION ======================
st.markdown('<p class="section-title">➕ Add a New Shift</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2.2, 1.6, 1.6, 1.3])

with col1:
    shift_date = st.date_input(
        "Shift Date",
        value=datetime.now().date(),
        key="new_shift_date"
    )

with col2:
    start_time = st.time_input(
        "Start Time",
        value=datetime.strptime("14:30", "%H:%M").time(),
        key="new_start"
    )

with col3:
    end_time = st.time_input(
        "End Time",
        value=datetime.strptime("18:30", "%H:%M").time(),
        key="new_end"
    )

with col4:
    st.write("")  # Spacer
    st.write("")
    if st.button("Add Shift", key="add_shift_btn", use_container_width=True):
        new_shift = {
            "date": shift_date.strftime("%Y-%m-%d"),
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M")
        }
        st.session_state.all_shifts.append(new_shift)
        st.success(f"✅ Shift added for {shift_date.strftime('%B %d, %Y')}")
        st.rerun()

st.divider()

# ====================== ALL SHIFTS SECTION ======================
st.markdown(f'<p class="section-title">📋 All Entered Shifts ({len(st.session_state.all_shifts)})</p>', unsafe_allow_html=True)

if not st.session_state.all_shifts:
    st.info("No shifts added yet. Use the form above to add your first shift.")
else:
    sorted_shifts = sorted(st.session_state.all_shifts, key=lambda x: x["date"], reverse=True)
    
    for i, shift in enumerate(sorted_shifts):
        date_obj = datetime.strptime(shift["date"], "%Y-%m-%d")
        hours = calculate_hours(shift["start"], shift["end"])
        
        with st.container(border=True):
            cols = st.columns([2.8, 1.7, 1.7, 1.3, 0.8])
            with cols[0]:
                st.write(f"**{date_obj.strftime('%A, %B %d, %Y')}**")
            
            with cols[1]:
                new_start = st.time_input(
                    "Start", 
                    value=datetime.strptime(shift["start"], "%H:%M").time(),
                    key=f"edit_start_{i}"
                )
                shift["start"] = new_start.strftime("%H:%M")
            
            with cols[2]:
                new_end = st.time_input(
                    "End", 
                    value=datetime.strptime(shift["end"], "%H:%M").time(),
                    key=f"edit_end_{i}"
                )
                shift["end"] = new_end.strftime("%H:%M")
            
            with cols[3]:
                st.metric("Hours", f"{hours:.2f}")
            
            with cols[4]:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this shift"):
                    st.session_state.all_shifts.pop(i)
                    st.rerun()

# ====================== SUMMARY & EXPORT ======================
st.divider()

col_summary1, col_summary2, col_summary3 = st.columns([2, 2, 3])

total_hours = sum(calculate_hours(s["start"], s["end"]) for s in st.session_state.all_shifts)

with col_summary1:
    st.metric("**Total Hours**", f"{total_hours:.2f}")

with col_summary2:
    st.metric("**Total Shifts**", len(st.session_state.all_shifts))

with col_summary3:
    if st.button("📤 Export All Shifts to CSV", type="primary", use_container_width=True):
        if not st.session_state.all_shifts:
            st.warning("No shifts to export.")
        else:
            data = []
            for shift in st.session_state.all_shifts:
                date_obj = datetime.strptime(shift["date"], "%Y-%m-%d")
                data.append({
                    "Date": shift["date"],
                    "Day": date_obj.strftime("%A"),
                    "Start Time": shift["start"],
                    "End Time": shift["end"],
                    "Hours Worked": calculate_hours(shift["start"], shift["end"])
                })
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"amazon_shifts_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

st.caption("✅ Custom date per shift • Works great on Streamlit Cloud • Python 3.14 ready")
