"""
Content Generator UI module for creating and editing content.
"""

import streamlit as st
import base64
import time
from io import BytesIO
from datetime import datetime
from typing import Dict

from models.content_model import ContentModel
from services.ai_service import GroqAIService
from services.image_service import CloudflareImageGenerator
from config import DEFAULT_FORMALITY, DEFAULT_HUMOR


class ContentUI:
    """Handle content generation and editing UI."""
    
    def __init__(self):
        self.ai_service = GroqAIService()
        self.image_service = CloudflareImageGenerator()
    
    def render(self, client: Dict):
        """Render content generator with text and image sections."""
        st.header("Content Generator")
        
        # Initialize session state for this client
        if 'formality_level' not in st.session_state:
            st.session_state.formality_level = DEFAULT_FORMALITY
        if 'humor_level' not in st.session_state:
            st.session_state.humor_level = DEFAULT_HUMOR
        
        # Topic selection
        self._render_topic_selection(client)
        
        # Tone controls
        self._render_tone_controls()
        
        # Auto-generate if needed
        self._auto_generate_content(client)
        
        st.markdown("---")
        
        # Two-column layout
        col_text, col_image = st.columns(2, gap="large")
        
        with col_text:
            self._render_text_section(client)
        
        with col_image:
            self._render_image_section(client)
        
        # AI reasoning
        if st.session_state.get('current_explanation'):
            with st.expander("View AI Reasoning"):
                explanation = st.session_state.current_explanation
                if isinstance(explanation, dict):
                    for key, value in explanation.items():
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                        st.markdown(f"{value}")
                        st.markdown("---")
    
    def _render_topic_selection(self, client: Dict):
        """Render topic selection UI."""
        st.markdown("### Select Topic")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Source selection
            source_options = ["Select from Calendar", "Manual Input"]
            default_source = "Select from Calendar" if st.session_state.get('selected_calendar_post') else "Manual Input"
            source = st.radio("Source", source_options, index=source_options.index(default_source), horizontal=True)
            
            if source == "Select from Calendar":
                self._render_calendar_topic_selector(client)
            else:
                st.session_state.selected_topic = st.text_input(
                    "Topic",
                    placeholder="Enter your content topic...",
                    value=st.session_state.get('manual_topic', '')
                )
                st.session_state.manual_topic = st.session_state.selected_topic
        
        with col2:
            st.markdown("### Platform")
            platform_options = ["LinkedIn", "Instagram", "Twitter", "Facebook", "Blog"]
            default_platform = st.session_state.get('selected_platform', 'LinkedIn')
            default_idx = platform_options.index(default_platform) if default_platform in platform_options else 0
            st.session_state.selected_platform = st.selectbox(
                "Choose platform",
                platform_options,
                index=default_idx,
                label_visibility="collapsed",
                key="platform_selector"
            )
    
    def _render_calendar_topic_selector(self, client: Dict):
        """Render calendar-based topic selection."""
        client_id = client['client_id']
        available_calendars = [k for k in st.session_state.get('calendar_posts', {}).keys() if k.startswith(client_id)]
        
        if available_calendars:
            month = st.session_state.get('calendar_month', datetime.now().strftime("%m"))
            year = st.session_state.get('calendar_year', datetime.now().year)
            cal_key = f"{client_id}_{year}_{month}"
            
            if cal_key in st.session_state.calendar_posts:
                calendar_data = st.session_state.calendar_posts[cal_key]
                if calendar_data:
                    post_options = []
                    post_map = {}
                    for day, post in calendar_data.items():
                        status = "✓" if post.get('generated_content') else "○"
                        label = f"{status} Day {day}: {post['topic']} ({post['platform']})"
                        post_options.append(label)
                        post_map[label] = (day, post)
                    
                    selected_label = st.selectbox("Choose a scheduled post", post_options, key="calendar_post_selector")
                    selected_day, selected_post = post_map[selected_label]
                    
                    st.session_state.selected_topic = selected_post['topic']
                    st.session_state.selected_platform = selected_post['platform']
                    st.session_state.selected_calendar_post = {
                        "day": selected_day,
                        "topic": selected_post['topic'],
                        "platform": selected_post['platform'],
                        "month": month,
                        "year": year
                    }
                    
                    if selected_post.get('generated_content'):
                        st.info("✅ Content already exists. You can edit it below.")
                        st.session_state.current_draft = selected_post['generated_content'].get('content', '')
                        st.session_state.editable_text = st.session_state.current_draft
                    else:
                        st.info(f"Selected: **{selected_post['platform']}** post about **{selected_post['topic']}**")
                else:
                    st.warning("No posts in calendar. Generate a calendar first.")
            else:
                st.warning(f"No calendar for {month}/{year}. Generate a calendar first.")
        else:
            st.warning("No calendar generated. Go to Calendar tab first.")
    
    def _render_tone_controls(self):
        """Render tone and voice control sliders."""
        with st.expander("🎭 Tone & Voice Controls", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Formality Level**")
                st.session_state.formality_level = st.slider(
                    "Formality",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.formality_level,
                    step=0.1,
                    help="0 = Casual, 1 = Formal"
                )
            
            with col2:
                st.markdown("**Humor Level**")
                st.session_state.humor_level = st.slider(
                    "Humor",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.humor_level,
                    step=0.1,
                    help="0 = Professional, 1 = Humorous"
                )
            
            # Tone description
            formality_desc = ("Very Casual" if st.session_state.formality_level < 0.3 else
                            "Moderately Casual" if st.session_state.formality_level < 0.5 else
                            "Moderately Formal" if st.session_state.formality_level < 0.7 else
                            "Very Formal")
            
            humor_desc = ("No Humor" if st.session_state.humor_level < 0.2 else
                         "Subtle Humor" if st.session_state.humor_level < 0.5 else
                         "Light Humor" if st.session_state.humor_level < 0.7 else
                         "Playful/Humorous")
            
            st.info(f"**Current Tone:** {formality_desc} | {humor_desc}")
    
    def _auto_generate_content(self, client: Dict):
        """Auto-generate content when selecting from calendar."""
        if (st.session_state.get('selected_calendar_post') and
            st.session_state.get('last_generated_day') != st.session_state.selected_calendar_post.get('day')):
            
            cal_post = st.session_state.selected_calendar_post
            month = cal_post.get('month')
            year = cal_post.get('year')
            day = cal_post.get('day')
            
            if month and year and day:
                calendar_key = f"{client['client_id']}_{year}_{month}"
                
                # Check for existing content
                if (calendar_key in st.session_state.get('calendar_posts', {}) and
                    day in st.session_state.calendar_posts[calendar_key] and
                    st.session_state.calendar_posts[calendar_key][day].get('generated_content')):
                    
                    existing = st.session_state.calendar_posts[calendar_key][day]['generated_content']
                    st.session_state.current_draft = existing.get('content', '')
                    st.session_state.editable_text = st.session_state.current_draft
                    st.session_state.current_explanation = existing.get('explanation', {})
                    st.session_state.last_generated_day = day
                else:
                    # Generate new content
                    with st.spinner(f"Generating content for {cal_post['topic']}..."):
                        context = self._build_context(client)
                        result = self.ai_service.generate_content(
                            f"Generate a {st.session_state.selected_platform} post about {st.session_state.selected_topic}",
                            context
                        )
                        st.session_state.current_draft = result.get("content", "")
                        st.session_state.editable_text = st.session_state.current_draft
                        st.session_state.current_explanation = result.get("explanation", {})
                        st.session_state.current_context = context
                        st.session_state.last_generated_day = day
    
    def _build_context(self, client: Dict) -> Dict:
        """Build context dictionary for AI generation."""
        return {
            "company_name": client['basic_info']['company_name'],
            "industry": client['basic_info']['industry'],
            "target_audience": client['basic_info'].get('target_audience', 'General'),
            "brand_tone": client['brand_voice']['tone'],
            "platform": st.session_state.selected_platform,
            "topic": st.session_state.selected_topic,
            "dos": client['brand_voice']['dos'],
            "donts": client['brand_voice']['donts'],
            "keywords": client['brand_voice']['keywords'],
            "formality": st.session_state.formality_level,
            "humor": st.session_state.humor_level
        }
    
    def _render_text_section(self, client: Dict):
        """Render text content generation section."""
        st.markdown("### Text Content")
        
        # Generate button
        if st.button("Generate Text", use_container_width=True, type="secondary"):
            if not st.session_state.selected_topic:
                st.warning("Please enter a topic or select from calendar.")
            else:
                with st.spinner("Generating text content..."):
                    context = self._build_context(client)
                    result = self.ai_service.generate_content(
                        f"Generate a {st.session_state.selected_platform} post about {st.session_state.selected_topic}",
                        context
                    )
                    st.session_state.current_draft = result.get("content", "")
                    st.session_state.editable_text = st.session_state.current_draft
                    st.session_state.current_explanation = result.get("explanation", {})
                    st.session_state.current_context = context
                    st.success("Text content generated!")
        
        # Text editor
        if st.session_state.get('current_draft'):
            edited_text = st.text_area(
                "Edit your content below:",
                value=st.session_state.current_draft,
                height=300,
                key="text_editor"
            )
            
            if edited_text != st.session_state.current_draft:
                st.session_state.current_draft = edited_text
                st.session_state.editable_text = edited_text
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                feedback = st.text_input("💭 Refine:", placeholder="Enter feedback...", key="text_feedback")
            
            with col2:
                if st.button("Apply Feedback", use_container_width=True):
                    if feedback:
                        with st.spinner("Refining text..."):
                            result = self.ai_service.refine_content(
                                st.session_state.current_draft,
                                feedback,
                                st.session_state.current_context
                            )
                            st.session_state.current_draft = result.get("content", "")
                            st.session_state.editable_text = st.session_state.current_draft
                            st.session_state.current_explanation = result.get("explanation", {})
                            st.success("Content refined!")
                    else:
                        st.info("Enter feedback first")
            
            with col3:
                if st.button("Save to Calendar", use_container_width=True, type="primary"):
                    self._save_text_content(client)
        else:
            st.info("Click 'Generate Text' to create content")
    
    def _save_text_content(self, client: Dict):
        """Save text content to calendar and history."""
        content_data = {
            "content": st.session_state.current_draft,
            "platform": st.session_state.selected_platform,
            "topic": st.session_state.selected_topic,
            "explanation": st.session_state.current_explanation,
            "tone_settings": {
                "formality": st.session_state.formality_level,
                "humor": st.session_state.humor_level
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if st.session_state.get('selected_calendar_post'):
            cal_post = st.session_state.selected_calendar_post
            calendar_key = f"{client['client_id']}_{cal_post['year']}_{cal_post['month']}"
            
            if calendar_key in st.session_state.calendar_posts:
                day = cal_post['day']
                st.session_state.calendar_posts[calendar_key][day]["generated_content"] = content_data
                st.session_state.calendar_posts[calendar_key][day]["status"] = "Content Ready"
                
                # Save to database
                post_date = f"{cal_post['year']}-{cal_post['month']}-{day:02d}"
                ContentModel.save_calendar_post(
                    client['client_id'], content_data, post_date,
                    cal_post['month'], cal_post['year'], day
                )
                
                st.success(f"Saved to calendar for Day {day}!")
        
        # Save to history
        ContentModel.save_content(
            client['client_id'], content_data, "text",
            st.session_state.selected_platform, st.session_state.selected_topic
        )
        
        st.success("Text saved!")
    
    def _render_image_section(self, client: Dict):
        """Render image generation section."""
        st.markdown("### Image Generation")
        
        visual_style = st.selectbox(
            "Visual Style",
            ["photorealistic", "digital art", "watercolor", "sketch", "3D render", "cinematic", "business"],
            key="image_style"
        )
        
        if st.button("Generate Image", use_container_width=True, type="secondary"):
            if not st.session_state.selected_topic:
                st.warning("Please enter a topic or select from calendar.")
            else:
                with st.spinner("Generating image with Cloudflare AI..."):
                    image = self.image_service.generate_image(st.session_state.selected_topic, visual_style)
                    if image:
                        st.session_state.generated_image = image
                        st.success("Image generated!")
        
        if st.session_state.get('generated_image'):
            st.image(st.session_state.generated_image, use_container_width=True)
            
            # Download button
            buf = BytesIO()
            st.session_state.generated_image.save(buf, format="PNG")
            st.download_button(
                "Download Image",
                buf.getvalue(),
                file_name=f"generated_image_{int(time.time())}.png",
                mime="image/png",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("#### Refine Image")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                feedback = st.text_input("💭 Refinement prompt:", key="image_feedback")
            
            with col2:
                if st.button("Regenerate", use_container_width=True):
                    if feedback:
                        with st.spinner("Regenerating image..."):
                            enhanced_prompt = f"{st.session_state.selected_topic}, {feedback}"
                            image = self.image_service.generate_image(enhanced_prompt, visual_style)
                            if image:
                                st.session_state.generated_image = image
                                st.success("Image regenerated!")
            
            if st.button("Save Image to Calendar", use_container_width=True, type="primary"):
                self._save_image_content(client)
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 80px 20px;
                text-align: center;
                color: white;
            ">
                <h3>✨ No Image Generated</h3>
                <p>Click 'Generate Image' to create AI-powered visuals</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _save_image_content(self, client: Dict):
        """Save image content to calendar and history."""
        buf = BytesIO()
        st.session_state.generated_image.save(buf, format="PNG")
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        content_data = {
            "content": f"Generated image for: {st.session_state.selected_topic}",
            "platform": st.session_state.selected_platform,
            "topic": st.session_state.selected_topic,
            "media_type": "image",
            "media_data": img_base64,
            "timestamp": datetime.now().isoformat()
        }
        
        if st.session_state.get('selected_calendar_post'):
            cal_post = st.session_state.selected_calendar_post
            calendar_key = f"{client['client_id']}_{cal_post['year']}_{cal_post['month']}"
            
            if calendar_key in st.session_state.calendar_posts:
                day = cal_post['day']
                st.session_state.calendar_posts[calendar_key][day]["generated_content"] = content_data
                st.session_state.calendar_posts[calendar_key][day]["status"] = "Content Ready"
                
                post_date = f"{cal_post['year']}-{cal_post['month']}-{day:02d}"
                ContentModel.save_calendar_post(
                    client['client_id'], content_data, post_date,
                    cal_post['month'], cal_post['year'], day
                )
                
                st.success(f"Image saved to calendar for Day {day}!")
        
        # Save to history
        ContentModel.save_content(
            client['client_id'], content_data, "image",
            st.session_state.selected_platform, st.session_state.selected_topic
        )
        
        st.success("Image saved!")