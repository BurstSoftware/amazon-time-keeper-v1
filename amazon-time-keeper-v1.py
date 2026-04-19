import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Page config
st.set_page_config(
    page_title="Amazon Weekly Hours Tracker",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Amazon Weekly Hours Tracker")
st.markdown("Track your shifts • Multiple shifts per day supported • Export to CSV")

# Initialize session state
if "shifts" not in st.session_state:
    st.session_state.shifts = {}  # {date_str: [{"start": "14:30", "end": "18:30"}, ...]}

if "week_start" not in st.session_state:
    # Default to current week (Sunday or Monday - you can change)
    today = datetime.now()
    days_ahead = today.weekday() if today.weekday() < 6 else 0  # Adjust as needed
    week_start = today - timedelta(days=days_ahead)
    st.session_state.week_start = week_start.date()

# Week selector
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    week_start_date = st.date_input(
        "Week Starting Date",
        value=st.session_state.week_start,
        key="week_start_input"
    )

# Update session state when date changes
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

# Function to calculate hours
def calculate_hours(start: str, end: str) -> float:
    if not start or not end:
        return 0.0
    try:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        if e < s:  # overnight shift
            e += timedelta(days=1)
        delta = e - s
        return round(delta.total_seconds() / 3600, 2)
    except:
        return 0.0

# Display days in columns (3 per row for better layout)
cols = st.columns(3)

for idx, day in enumerate(days):
    with cols[idx % 3]:
        st.subheader(f"**{day['day_name']}**")
        st.caption(day['display_date'])
        
        date_str = day["date_str"]
        
        # Initialize empty list if day doesn't exist
        if date_str not in st.session_state.shifts:
            st.session_state.shifts[date_str] = []
        
        shifts_today = st.session_state.shifts[date_str]
        
        # Display existing shifts
        for i, shift in enumerate(shifts_today):
            col_a, col_b, col_c, col_d = st.columns([2, 2, 1.5, 0.8])
            with col_a:
                new_start = st.time_input(
                    "Start", 
                    value=datetime.strptime(shift["start"], "%H:%M").time() if shift["start"] else None,
                    key=f"start_{date_str}_{i}"
                )
                shift["start"] = new_start.strftime("%H:%M") if new_start else ""
            
            with col_b:
                new_end = st.time_input(
                    "End", 
                    value=datetime.strptime(shift["end"], "%H:%M").time() if shift["end"] else None,
                    key=f"end_{date_str}_{i}"
                )
                shift["end"] = new_end.strftime("%H:%M") if new_end else ""
            
            hours = calculate_hours(shift["start"], shift["end"])
            with col_c:
                st.metric("Hours", f"{hours:.2f}")
            
            with col_d:
                if st.button("🗑️", key=f"del_{date_str}_{i}"):
                    del st.session_state.shifts[date_str][i]
                    st.rerun()
        
        # Add new shift button
        if st.button("➕ Add Shift", key=f"add_{date_str}", use_container_width=True):
            st.session_state.shifts[date_str].append({"start": "14:30", "end": "18:30"})
            st.rerun()

# Calculate total hours
total_hours = 0.0
total_shifts = 0

for date_shifts in st.session_state.shifts.values():
    total_shifts += len(date_shifts)
    for shift in date_shifts:
        total_hours += calculate_hours(shift.get("start", ""), shift.get("end", ""))

# Footer summary
st.divider()
col_total1, col_total2, col_total3 = st.columns([2, 2, 3])

with col_total1:
    st.metric("**Total Hours This Week**", f"{total_hours:.2f}")

with col_total2:
    st.metric("**Total Shifts**", total_shifts)

with col_total3:
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("💾 Save Progress", use_container_width=True):
            st.success("✅ Progress saved in session!")
    
    with col_btn2:
        if st.button("📤 Export Week to CSV", type="primary", use_container_width=True):
            if total_shifts == 0:
                st.warning("No shifts entered yet.")
            else:
                data = []
                for date_str, shifts_list in st.session_state.shifts.items():
                    day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
                    for shift in shifts_list:
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
                    label="⬇️ Download CSV Now",
                    data=csv,
                    file_name=f"amazon_hours_{week_start_date.strftime('%Y-%m-%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col_btn3:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if st.checkbox("Confirm clear all shifts?"):
                st.session_state.shifts = {}
                st.success("All data cleared.")
                st.rerun()

# Optional: Show raw data for debugging
with st.expander("Show Raw Data (for verification)"):
    st.json(st.session_state.shifts)

st.caption("Built for Amazon Associates • Multiple/split shifts supported • Data saved in browser session")
