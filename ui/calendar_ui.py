"""
Calendar UI module for displaying and managing content calendars.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict

from models.content_model import ContentModel
from services.calendar_service import EnhancedContentCalendar


class CalendarUI:
    """Handle calendar display and interaction."""
    
    def __init__(self):
        self.calendar_service = EnhancedContentCalendar()
    
    def render(self, client: Dict):
        """Render enhanced calendar with clickable days."""
        st.header(f"{client['basic_info']['company_name']} Content Calendar")
        
        # Month and year selection
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
            month = st.selectbox(
                "Month",
                months,
                format_func=lambda x: datetime(2025, int(x), 1).strftime("%B"),
                key="calendar_month",
                index=int(datetime.now().strftime("%m")) - 1
            )
        
        with col2:
            years = list(range(2024, 2031))
            year = st.selectbox(
                "Year",
                years,
                index=years.index(datetime.now().year),
                key="calendar_year"
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_btn = st.button("Generate Calendar", type="primary", use_container_width=True)
        
        # Load or generate calendar
        calendar_key = f"{client['client_id']}_{year}_{month}"
        
        if calendar_key not in st.session_state.get('calendar_posts', {}):
            # Try to load from database
            db_posts = ContentModel.get_calendar_posts(client['client_id'], month, year)
            
            if db_posts:
                calendar_data = {}
                for day, post_data in db_posts.items():
                    calendar_data[day] = {
                        "date": f"{year}-{month}-{day:02d}",
                        "day_of_week": datetime(year, int(month), day).strftime("%A"),
                        "content_type": post_data.get("content_type", "Educational"),
                        "platform": post_data.get("platform", "LinkedIn"),
                        "topic": post_data.get("topic", "General"),
                        "status": "Content Ready" if post_data.get('content') else "Scheduled",
                        "color": self.calendar_service.color_map.get(post_data.get("content_type", "Educational"), "#3b82f6"),
                        "time": post_data.get("time", "10:00"),
                        "title": f"Day {day}: {post_data.get('topic', 'Topic')[:30]}...",
                        "generated_content": post_data
                    }
                
                st.session_state.calendar_posts[calendar_key] = calendar_data
                st.session_state.calendar_days = {calendar_key: datetime(year, int(month), 1).day}
        
        # Generate new calendar if requested
        if generate_btn:
            with st.spinner("Generating calendar..."):
                new_calendar, days_in_month = self.calendar_service.generate_month_calendar(client, month, year)
                
                # Preserve existing generated content
                if calendar_key in st.session_state.get('calendar_posts', {}):
                    existing = st.session_state.calendar_posts[calendar_key]
                    for day, post in existing.items():
                        if day in new_calendar and post.get('generated_content'):
                            new_calendar[day]["generated_content"] = post["generated_content"]
                            new_calendar[day]["status"] = "Content Ready"
                
                st.session_state.calendar_posts[calendar_key] = new_calendar
                if 'calendar_days' not in st.session_state:
                    st.session_state.calendar_days = {}
                st.session_state.calendar_days[calendar_key] = days_in_month
                
                st.success(f"Calendar generated for {datetime(year, int(month), 1).strftime('%B %Y')}")
                st.rerun()
        
        # Display calendar
        if calendar_key in st.session_state.get('calendar_posts', {}):
            calendar_data = st.session_state.calendar_posts[calendar_key]
            days_in_month = st.session_state.calendar_days.get(calendar_key, 31)
            
            posts_with_content = sum(1 for post in calendar_data.values() if post.get('generated_content'))
            
            st.subheader(f"Content Calendar - {datetime(year, int(month), 1).strftime('%B %Y')}")
            st.caption(f"Scheduled: {len(calendar_data)} | With Content: {posts_with_content}")
            
            # Render calendar grid
            result = self.calendar_service.render_calendar_grid(
                calendar_data, days_in_month, month, year, st
            )
            
            if result.get("selected"):
                st.session_state.selected_calendar_post = {
                    "day": result["day"],
                    "topic": result["post"]["topic"],
                    "platform": result["post"]["platform"],
                    "month": month,
                    "year": year,
                    "content_type": result["post"]["content_type"]
                }
                st.session_state.active_tab = "generator"
                st.rerun()
            
            # Download calendar
            if st.button("Download Calendar CSV"):
                calendar_list = []
                for day, post in calendar_data.items():
                    post_copy = post.copy()
                    post_copy['day'] = day
                    post_copy['has_content'] = post.get('generated_content') is not None
                    calendar_list.append(post_copy)
                
                df = pd.DataFrame(calendar_list)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"calendar_{month}_{year}.csv",
                    mime="text/csv"
                )