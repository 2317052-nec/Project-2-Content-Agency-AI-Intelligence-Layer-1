"""
Content Calendar Service for generating and managing content schedules.
"""

import random
import calendar
from datetime import datetime
from typing import Dict, List, Tuple

from config import INDUSTRIES


class EnhancedContentCalendar:
    """Generate and manage content calendars."""
    
    def __init__(self):
        # Seasonal themes
        self.seasonal_themes = {
            "Q1": ["New Year Planning", "Winter Solutions", "Year-ahead Trends", "Goal Setting"],
            "Q2": ["Spring Updates", "Mid-year Reviews", "Summer Preparation", "Industry Events"],
            "Q3": ["Back to School", "Fall Planning", "Holiday Prep", "Year-end Strategy"],
            "Q4": ["Year-end Review", "Holiday Campaigns", "New Year Prep", "Annual Reports"]
        }
        
        # Industry-specific topics
        self.industry_topics = {
            "Technology": ["AI Trends", "Digital Transformation", "Tech Tips", "Innovation Spotlight", "Cybersecurity"],
            "Fashion": ["Seasonal Trends", "Style Guides", "Behind the Scenes", "Collection Launches", "Sustainable Fashion"],
            "Healthcare": ["Wellness Tips", "Medical Advances", "Patient Stories", "Health Education", "Preventive Care"],
            "Finance": ["Investment Tips", "Market Updates", "Financial Planning", "Economic Trends", "Retirement Planning"],
            "Education": ["E-learning Trends", "Student Success", "EdTech Innovations", "Teaching Tips", "Online Learning"],
            "Real Estate": ["Market Trends", "Home Buying Tips", "Property Spotlight", "Investment Advice", "Interior Design"],
            "Food & Beverage": ["Recipe Ideas", "Restaurant Spotlight", "Food Trends", "Cooking Tips", "Healthy Eating"]
        }
        
        # Color mapping for content types
        self.color_map = {
            "Educational": "#3b82f6",
            "Promotional": "#10b981",
            "Engagement": "#f97316",
            "Industry News": "#8b5cf6",
            "Client Spotlight": "#ec4899"
        }
    
    def generate_month_calendar(
        self,
        client_profile: Dict,
        month: str,
        year: int = 2025
    ) -> Tuple[Dict[int, Dict], int]:
        """Generate monthly content calendar with unique topics."""
        
        strategy = client_profile.get("content_strategy", {})
        basic_info = client_profile.get("basic_info", {})
        
        industry = basic_info.get("industry", "Technology")
        content_mix = strategy.get("content_mix", {"promotional": 30, "educational": 40, "engagement": 30})
        platforms = strategy.get("platforms", ["Instagram", "LinkedIn"])
        posting_frequency = strategy.get("posting_frequency", {"monthly": 20})
        content_pillars = strategy.get("content_pillars", ["Product/Service", "Industry Insights", "Customer Success"])
        
        target_posts = posting_frequency.get("monthly", 20)
        industry_topics = self.industry_topics.get(industry, self.industry_topics["Technology"])
        
        # Get seasonal themes
        quarter = f"Q{(int(month)-1)//3 + 1}"
        seasonal_options = self.seasonal_themes.get(quarter, self.seasonal_themes["Q1"])
        
        days_in_month = calendar.monthrange(int(year), int(month))[1]
        calendar_data = {}
        
        # Spread posts throughout the month
        post_days = sorted(random.sample(range(1, days_in_month + 1), min(target_posts, days_in_month)))
        
        used_topics = set()
        
        for day in post_days:
            post_date = datetime(int(year), int(month), day)
            
            # Determine content type based on mix
            rand_val = random.randint(1, 100)
            if rand_val <= content_mix["promotional"]:
                content_type = "Promotional"
            elif rand_val <= content_mix["promotional"] + content_mix["educational"]:
                content_type = "Educational"
            else:
                content_type = "Engagement"
            
            platform = random.choice(platforms)
            
            # Select unique topic
            available_topics = [t for t in industry_topics if t not in used_topics]
            if not available_topics:
                available_topics = industry_topics
                used_topics.clear()
            
            if content_pillars and random.random() > 0.3:
                pillar = random.choice(content_pillars)
                topic = f"{pillar}: {random.choice(available_topics)}"
            else:
                topic = random.choice(available_topics)
            
            used_topics.add(topic.split(": ")[-1] if ": " in topic else topic)
            
            seasonal = random.choice(seasonal_options)
            
            calendar_data[day] = {
                "date": post_date.strftime("%Y-%m-%d"),
                "day_of_week": post_date.strftime("%A"),
                "content_type": content_type,
                "platform": platform,
                "topic": topic,
                "content_pillar": random.choice(content_pillars) if content_pillars else "General",
                "seasonal_theme": seasonal,
                "status": "Scheduled",
                "color": self.color_map.get(content_type, "#3b82f6"),
                "time": f"{random.randint(9, 17)}:00",
                "title": f"Day {day}: {topic[:30]}...",
                "generated_content": None
            }
        
        return calendar_data, days_in_month
    
    def update_calendar_post(
        self,
        client_id: str,
        month: str,
        year: int,
        day: int,
        content_data: Dict,
        session_state: Dict
    ) -> bool:
        """Update calendar post with generated content."""
        calendar_key = f"{client_id}_{year}_{month}"
        
        if calendar_key in session_state.get('calendar_posts', {}):
            if day in session_state.calendar_posts[calendar_key]:
                session_state.calendar_posts[calendar_key][day]["generated_content"] = content_data
                session_state.calendar_posts[calendar_key][day]["status"] = "Content Ready"
                return True
        
        return False
    
    def render_calendar_grid(
        self,
        calendar_data: Dict,
        days_in_month: int,
        month: str,
        year: int,
        st
    ):
        """Render calendar grid using Streamlit columns."""
        
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        first_weekday = calendar.monthrange(int(year), int(month))[0]
        
        # CSS styling
        st.markdown("""
        <style>
        .calendar-day-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 15px;
            min-height: 120px;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .calendar-day-card:hover {
            background: rgba(59,130,246,0.15);
            border-color: #3b82f6;
        }
        .calendar-day-card.empty {
            background: transparent;
            border: 1px dashed rgba(255,255,255,0.1);
            cursor: default;
        }
        .day-number {
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .post-title {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .post-type {
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 8px;
        }
        .weekday-header {
            text-align: center;
            font-weight: 700;
            color: #1e3a8a;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Weekday headers
        cols = st.columns(7)
        for i, day in enumerate(weekdays):
            with cols[i]:
                st.markdown(f"<div class='weekday-header'>{day}</div>", unsafe_allow_html=True)
        
        # Calendar grid
        day_counter = 1
        total_cells = first_weekday + days_in_month
        num_rows = (total_cells + 6) // 7
        
        for row in range(num_rows):
            cols = st.columns(7)
            for col in range(7):
                cell_index = row * 7 + col
                
                with cols[col]:
                    if cell_index < first_weekday:
                        st.markdown("<div class='calendar-day-card empty'></div>", unsafe_allow_html=True)
                    elif day_counter <= days_in_month:
                        if day_counter in calendar_data:
                            post = calendar_data[day_counter]
                            color = post['color']
                            has_content = post.get('generated_content') is not None
                            
                            # Create clickable button
                            if st.button(
                                f"Day {day_counter}",
                                key=f"day_{day_counter}_{month}_{year}",
                                use_container_width=True
                            ):
                                return {
                                    "selected": True,
                                    "day": day_counter,
                                    "post": post
                                }
                            
                            status_html = "<span style='color:green;'>✓</span>" if has_content else ""
                            
                            st.markdown(f"""
                            <div class='calendar-day-card' style='background: {color}20; border-left: 3px solid {color};'>
                                <div class='day-number'>Day {day_counter} {status_html}</div>
                                <div class='post-title'>{post['title'][:40]}</div>
                                <span class='post-type' style='background: {color}30;'>{post['content_type']}</span>
                                <div style='font-size:11px; margin-top:5px;'>{post.get('time', '10:00')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class='calendar-day-card empty'>
                                <div class='day-number'>Day {day_counter}</div>
                                <div style='color:#475569; font-size:13px;'>No post</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        day_counter += 1
                    else:
                        st.markdown("<div class='calendar-day-card empty'></div>", unsafe_allow_html=True)
        
        return {"selected": False}