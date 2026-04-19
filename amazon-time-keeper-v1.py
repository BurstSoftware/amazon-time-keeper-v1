import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Amazon Hours Tracker",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Amazon Weekly Hours Tracker")
st.markdown("**Simple • Multiple shifts per day • Ready for Streamlit Cloud**")

# Initialize session state
if "shifts" not in st.session_state:
    st.session_state.shifts = {}

if "week_start" not in st.session_state:
    today = datetime.now().date()
    # Start week on the most recent Sunday (common for pay weeks)
    week_start = today - timedelta(days=today.weekday() + 1 if today.weekday() < 6 else 0)
    st.session_state.week_start = week_start

# Week selector
week_start_date = st.date_input(
    "Select Week Starting Date",
    value=st.session_state.week_start,
    key="week_input"
)

if week_start_date != st.session_state.week_start:
    st.session_state.week_start = week_start_date

# Generate 7 days
days = []
current = datetime.combine(week_start_date, datetime.min.time())
for i in range(7):
    date_obj = current + timedelta(days=i)
    date_str = date_obj.strftime("%Y-%m-%d")
    day_name = date_obj.strftime("%A")
    display_date = date_obj.strftime("%B %d, %Y")
    
    days.append({
        "date_str": date_str,
        "day_name": day_name,
        "display_date": display_date
    })

def calculate_hours(start: str, end: str) -> float:
    """Calculate hours between two times (handles overnight shifts)."""
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

# Display days
for day in days:
    date_str = day["date_str"]
    
    if date_str not in st.session_state.shifts:
        st.session_state.shifts[date_str] = []
    
    with st.expander(f"**{day['day_name']}** — {day['display_date']}", expanded=True):
        shifts_today = st.session_state.shifts[date_str]
        
        for i, shift in enumerate(shifts_today[:]):
            cols = st.columns([2, 2, 1.2, 0.6])
            with cols[0]:
                start_time = st.time_input(
                    "Start Time", 
                    value=datetime.strptime(shift["start"], "%H:%M").time() if shift.get("start") else None,
                    key=f"start_{date_str}_{i}"
                )
                shift["start"] = start_time.strftime("%H:%M") if start_time else ""
            
            with cols[1]:
                end_time = st.time_input(
                    "End Time", 
                    value=datetime.strptime(shift["end"], "%H:%M").time() if shift.get("end") else None,
                    key=f"end_{date_str}_{i}"
                )
                shift["end"] = end_time.strftime("%H:%M") if end_time else ""
            
            hours = calculate_hours(shift.get("start", ""), shift.get("end", ""))
            with cols[2]:
                st.metric("Hours", f"{hours:.2f}")
            
            with cols[3]:
                if st.button("🗑️", key=f"del_{date_str}_{i}"):
                    del st.session_state.shifts[date_str][i]
                    st.rerun()
        
        # Add shift button
        if st.button("➕ Add Shift", key=f"add_{date_str}", use_container_width=True):
            st.session_state.shifts[date_str].append({"start": "14:30", "end": "18:30"})
            st.rerun()

# Summary
total_hours = 0.0
total_shifts = 0

for shifts_list in st.session_state.shifts.values():
    total_shifts += len(shifts_list)
    for shift in shifts_list:
        total_hours += calculate_hours(shift.get("start", ""), shift.get("end", ""))

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("**Total Hours**", f"{total_hours:.2f}")
with col2:
    st.metric("**Total Shifts**", total_shifts)

with col3:
    if st.button("📤 Export to CSV", type="primary", use_container_width=True):
        if total_shifts == 0:
            st.warning("No shifts added yet.")
        else:
            data = []
            for date_str, shift_list in st.session_state.shifts.items():
                day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
                for shift in shift_list:
                    hours = calculate_hours(shift.get("start", ""), shift.get("end", ""))
                    data.append({
                        "Date": date_str,
                        "Day": day_name,
                        "Start Time": shift.get("start", ""),
                        "End Time": shift.get("end", ""),
                        "Hours Worked": hours
                    })
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"amazon_hours_{week_start_date}.csv",
                mime="text/csv",
                use_container_width=True
            )

st.caption("✅ Works on Python 3.14 • Optimized for Streamlit Community Cloud")
