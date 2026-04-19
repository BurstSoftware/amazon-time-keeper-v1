import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Amazon Hours Tracker",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Amazon Weekly Hours Tracker")
st.markdown("**Enter shifts with custom dates • Multiple shifts supported • Export to CSV**")

# Initialize session state
if "all_shifts" not in st.session_state:
    st.session_state.all_shifts = []   # List of dicts: [{"date": "2025-04-05", "start": "14:30", "end": "18:30"}, ...]

# Function to calculate hours
def calculate_hours(start: str, end: str) -> float:
    if not start or not end:
        return 0.0
    try:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        if e < s:  # overnight shift
            e += timedelta(days=1)
        return round((e - s).total_seconds() / 3600, 2)
    except:
        return 0.0

# Add New Shift Section
st.subheader("➕ Add a New Shift")

col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])

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
    if st.button("Add Shift", type="primary", use_container_width=True):
        new_shift = {
            "date": shift_date.strftime("%Y-%m-%d"),
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M")
        }
        st.session_state.all_shifts.append(new_shift)
        st.success(f"Shift added for {shift_date.strftime('%B %d, %Y')}")
        st.rerun()

# Display All Entered Shifts
st.divider()
st.subheader(f"📋 All Entered Shifts ({len(st.session_state.all_shifts)})")

if not st.session_state.all_shifts:
    st.info("No shifts added yet. Use the form above to add your first shift.")
else:
    # Sort shifts by date (newest first)
    sorted_shifts = sorted(
        st.session_state.all_shifts,
        key=lambda x: x["date"],
        reverse=True
    )
    
    for i, shift in enumerate(sorted_shifts):
        date_obj = datetime.strptime(shift["date"], "%Y-%m-%d")
        hours = calculate_hours(shift["start"], shift["end"])
        
        with st.container(border=True):
            cols = st.columns([2.5, 1.8, 1.8, 1.2, 0.7])
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
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.all_shifts.pop(i)
                    st.rerun()

# Summary
total_hours = sum(calculate_hours(s["start"], s["end"]) for s in st.session_state.all_shifts)

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("**Total Hours**", f"{total_hours:.2f}")

with col2:
    st.metric("**Total Shifts**", len(st.session_state.all_shifts))

with col3:
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
            csv_buffer = df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download CSV File",
                data=csv_buffer,
                file_name=f"amazon_shifts_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

st.caption("✅ Custom date per shift • Works great on Streamlit Cloud • Python 3.14 ready")
