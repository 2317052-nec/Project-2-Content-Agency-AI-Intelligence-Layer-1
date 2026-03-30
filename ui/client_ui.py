"""
Client management UI module.
"""

import streamlit as st
from datetime import datetime
from typing import Dict

from models.client_model import ClientModel
from services.scraper_service import SocialMediaScraper
from config import INDUSTRIES, PLATFORMS


class ClientUI:
    """Handle client onboarding and management UI."""
    
    def __init__(self):
        self.scraper = SocialMediaScraper()
    
    def _process_uploaded_file(self, uploaded_file):
        """Process uploaded file for storage."""
        if uploaded_file is None:
            return None
        
        file_details = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "content_preview": ""
        }
        
        try:
            if uploaded_file.type == "text/plain":
                content = uploaded_file.getvalue().decode("utf-8")
                file_details["content_preview"] = content[:500] + "..." if len(content) > 500 else content
                file_details["full_content"] = content
            
            elif uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
                import base64
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                file_details["image_base64"] = base64.b64encode(image_bytes).decode('utf-8')
                file_details["image_format"] = uploaded_file.type
                file_details["content_preview"] = f"Image uploaded: {uploaded_file.name}"
            
            elif uploaded_file.type == "application/pdf":
                import base64
                uploaded_file.seek(0)
                pdf_bytes = uploaded_file.read()
                file_details["pdf_base64"] = base64.b64encode(pdf_bytes).decode('utf-8')
                file_details["content_preview"] = f"PDF uploaded: {uploaded_file.name}"
            
            else:
                file_details["content_preview"] = f"File uploaded: {uploaded_file.name}"
        
        except Exception as e:
            file_details["content_preview"] = f"Error processing file: {str(e)}"
        
        return file_details
    
    def _get_rule_based_brand_voice(self, industry: str) -> Dict:
        """Get rule-based brand voice defaults."""
        
        defaults = {
            "Technology": {
                "tone": "Innovative and Professional",
                "dos": [
                    "Share technical insights and expertise",
                    "Highlight innovation and cutting-edge solutions",
                    "Discuss industry trends",
                    "Provide educational content"
                ],
                "donts": [
                    "Avoid making exaggerated claims",
                    "Don't use overly technical jargon",
                    "Avoid negative competitor comments"
                ],
                "keywords": ["innovation", "technology", "digital", "solutions"]
            },
            "Fashion": {
                "tone": "Trendy and Aspirational",
                "dos": [
                    "Showcase high-quality visual content",
                    "Highlight craftsmanship",
                    "Engage with fashion trends",
                    "Share behind-the-scenes"
                ],
                "donts": [
                    "Avoid poor quality images",
                    "Don't copy competitors",
                    "Avoid promoting fast fashion waste"
                ],
                "keywords": ["style", "fashion", "trends", "design"]
            },
            "Healthcare": {
                "tone": "Trustworthy and Compassionate",
                "dos": [
                    "Share evidence-based information",
                    "Highlight patient success stories",
                    "Discuss preventive care",
                    "Provide educational content"
                ],
                "donts": [
                    "Never give medical advice",
                    "Don't make false claims",
                    "Avoid unverified treatments"
                ],
                "keywords": ["health", "wellness", "care", "medical"]
            }
        }
        
        return defaults.get(industry, {
            "tone": "Professional and Engaging",
            "dos": ["Share company updates", "Highlight customer success", "Discuss industry trends"],
            "donts": ["Avoid unsubstantiated claims", "Don't ignore feedback", "Avoid inconsistent posting"],
            "keywords": ["professional", "quality", "service", "excellence"]
        })
    
    def create_client_profile(self, form_data: Dict) -> Dict:
        """Create structured client profile from form data."""
        
        # Process uploaded files
        logo_data = self._process_uploaded_file(form_data.get("logo"))
        brand_guidelines_data = self._process_uploaded_file(form_data.get("brand_guidelines"))
        
        sample_posts_data = []
        if form_data.get("sample_posts"):
            for sample_post in form_data["sample_posts"]:
                processed = self._process_uploaded_file(sample_post)
                if processed:
                    sample_posts_data.append(processed)
        
        industry = form_data.get("industry", "Other")
        rule_based_voice = self._get_rule_based_brand_voice(industry)
        
        # Build client profile
        client_id = ClientModel.generate_client_id(form_data["company_name"])
        
        return {
            "client_id": client_id,
            "basic_info": {
                "company_name": form_data["company_name"],
                "industry": industry,
                "company_size": form_data.get("company_size", ""),
                "website": form_data.get("website", ""),
                "description": form_data.get("description", ""),
                "target_audience": form_data.get("target_audience", ""),
                "competitors": form_data.get("competitors", "").split("\n") if form_data.get("competitors") else []
            },
            "brand_voice": {
                "tone": form_data.get("brand_tone") or rule_based_voice["tone"],
                "dos": [x.strip() for x in form_data.get("dos", "").split("\n") if x.strip()] or rule_based_voice["dos"],
                "donts": [x.strip() for x in form_data.get("donts", "").split("\n") if x.strip()] or rule_based_voice["donts"],
                "keywords": [x.strip() for x in form_data.get("keywords", "").split(",") if x.strip()] or rule_based_voice["keywords"]
            },
            "content_strategy": {
                "content_pillars": [x.strip() for x in form_data.get("content_pillars", "").split("\n") if x.strip()],
                "platforms": form_data.get("platforms", []),
                "posting_frequency": {
                    "daily": int(form_data.get("daily_posts", 1)),
                    "weekly": int(form_data.get("weekly_posts", 5)),
                    "monthly": int(form_data.get("monthly_posts", 20))
                },
                "content_mix": {
                    "promotional": int(form_data.get("promotional_percent", 30)),
                    "educational": int(form_data.get("educational_percent", 40)),
                    "engagement": int(form_data.get("engagement_percent", 30))
                }
            },
            "assets": {
                "logo": logo_data,
                "sample_posts": sample_posts_data,
                "brand_guidelines": brand_guidelines_data,
                "color_palette": form_data.get("color_palette", "").split(",") if form_data.get("color_palette") else []
            },
            "social_profile": form_data.get("social_profile", {}),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "status": "active"
            }
        }
    
    def populate_from_social_profile(self, profile_data: Dict) -> Dict:
        """Populate form data from scraped social profile."""
        
        company_name = profile_data.get('company_name', '')
        if not company_name and profile_data.get('username'):
            company_name = profile_data['username'].replace('-', ' ').replace('_', ' ').title()
        
        industry = profile_data.get('industry', 'Other')
        rule_based = self._get_rule_based_brand_voice(industry)
        
        # Determine brand tone from content style
        content_style = profile_data.get('content_style', '')
        if 'concise' in content_style.lower():
            brand_tone = 'Concise and Direct'
        elif 'professional' in content_style.lower():
            brand_tone = 'Professional and Authoritative'
        else:
            brand_tone = rule_based["tone"]
        
        # Extract keywords from hashtags
        hashtags = profile_data.get('hashtags_used', [])
        keywords = [tag.replace('#', '') for tag in hashtags[:5]]
        keywords_str = ", ".join(keywords) if keywords else ", ".join(rule_based["keywords"])
        
        bio = profile_data.get('bio', '')
        description = profile_data.get('description', '') or bio or f"Official profile of {company_name}"
        
        return {
            "company_name": company_name,
            "industry": industry,
            "website": f"https://www.{profile_data.get('platform', 'example')}.com/{profile_data.get('username', '')}",
            "description": description,
            "target_audience": f"Followers of {company_name}",
            "brand_tone": brand_tone,
            "keywords": keywords_str,
            "dos": "\n".join(rule_based["dos"][:3]),
            "donts": "\n".join(rule_based["donts"][:3]),
            "content_pillars": "\n".join(profile_data.get('common_topics', ["Company Updates", "Industry News", "Customer Stories"])[:3]),
            "platforms": [profile_data.get('platform', 'Instagram').capitalize()],
            "social_profile_data": profile_data
        }
    
    def render_onboarding_form(self):
        """Render client onboarding form."""
        st.header("Onboard New Client")
        st.markdown("Fill in the details below to create a new client profile")
        
        # Social media auto-fill section
        with st.expander("Auto-fill from Social Media", expanded=True):
            st.markdown("Enter Instagram, LinkedIn, or Twitter URL to auto-populate details")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                profile_url = st.text_input(
                    "Social Media URL",
                    placeholder="https://www.instagram.com/username",
                    key="profile_url_input"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔍 Fetch Details", type="primary", use_container_width=True):
                    if profile_url:
                        with st.spinner("Fetching profile data..."):
                            profile_data = self.scraper.scrape_profile_data(profile_url)
                            
                            if profile_data.get("error"):
                                st.warning(profile_data["error"])
                            else:
                                st.session_state.scraped_profile = profile_data
                                populated = self.populate_from_social_profile(profile_data)
                                
                                for key, value in populated.items():
                                    if key != "social_profile_data":
                                        st.session_state[f"form_{key}"] = value
                                
                                st.success(f"✅ Data fetched from {profile_data['platform'].capitalize()}!")
                                st.rerun()
        
        # Main form
        with st.form("client_onboarding_form"):
            st.subheader("Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input(
                    "Company/Brand Name*",
                    value=st.session_state.get("form_company_name", "")
                )
                
                industry_idx = 0
                default_industry = st.session_state.get("form_industry", "Technology")
                if default_industry in INDUSTRIES:
                    industry_idx = INDUSTRIES.index(default_industry)
                
                industry = st.selectbox("Industry*", INDUSTRIES, index=industry_idx)
                
                website = st.text_input("Website URL", value=st.session_state.get("form_website", ""))
            
            with col2:
                target_audience = st.text_area(
                    "Target Audience",
                    height=100,
                    value=st.session_state.get("form_target_audience", "")
                )
                
                description = st.text_area(
                    "Company Description",
                    height=100,
                    value=st.session_state.get("form_description", "")
                )
            
            st.subheader("Brand Voice")
            col1, col2 = st.columns(2)
            
            with col1:
                brand_tone = st.text_input(
                    "Brand Tone",
                    placeholder="e.g., Professional, Friendly, Innovative",
                    value=st.session_state.get("form_brand_tone", "")
                )
                
                keywords = st.text_input(
                    "Brand Keywords (comma-separated)",
                    value=st.session_state.get("form_keywords", "")
                )
            
            with col2:
                dos = st.text_area(
                    "Brand Do's (one per line)",
                    height=80,
                    value=st.session_state.get("form_dos", "")
                )
                
                donts = st.text_area(
                    "Brand Don'ts (one per line)",
                    height=80,
                    value=st.session_state.get("form_donts", "")
                )
            
            st.subheader("Content Strategy")
            col1, col2 = st.columns(2)
            
            with col1:
                content_pillars = st.text_area(
                    "Content Pillars (one per line)",
                    height=100,
                    value=st.session_state.get("form_content_pillars", "")
                )
                
                default_platforms = st.session_state.get("form_platforms", ["Instagram", "LinkedIn"])
                if isinstance(default_platforms, str):
                    default_platforms = [default_platforms]
                
                platforms = st.multiselect(
                    "Target Platforms*",
                    PLATFORMS,
                    default=default_platforms
                )
            
            with col2:
                st.markdown("**Posting Frequency**")
                daily_posts = st.number_input("Posts per day", min_value=0, max_value=10, value=1)
                weekly_posts = st.number_input("Posts per week", min_value=0, max_value=50, value=5)
                monthly_posts = st.number_input("Posts per month", min_value=0, max_value=200, value=20)
                
                st.markdown("**Content Mix (%)**")
                promo, edu, engage = st.columns(3)
                with promo:
                    promotional = st.number_input("Promotional", min_value=0, max_value=100, value=30)
                with edu:
                    educational = st.number_input("Educational", min_value=0, max_value=100, value=40)
                with engage:
                    engagement = st.number_input("Engagement", min_value=0, max_value=100, value=30)
            
            st.subheader("Brand Assets")
            col1, col2 = st.columns(2)
            
            with col1:
                logo = st.file_uploader(
                    "Company Logo",
                    type=["png", "jpg", "jpeg"],
                    help="Upload your company logo"
                )
            
            with col2:
                brand_guidelines = st.file_uploader(
                    "Brand Guidelines",
                    type=["pdf"],
                    help="Upload brand guidelines document"
                )
            
            sample_posts = st.file_uploader(
                "Sample Posts",
                type=["png", "jpg", "txt", "pdf"],
                accept_multiple_files=True,
                help="Upload examples of successful posts"
            )
            
            # Create a submit button that will trigger the form submission
            submitted = st.form_submit_button("Create Client Profile", type="primary", use_container_width=True)
            
            # Handle form submission
            if submitted:
                # Validate required fields
                if not company_name:
                    st.error("❌ Please enter a company name")
                    return
                if not platforms:
                    st.error("❌ Please select at least one platform")
                    return
                if promotional + educational + engagement != 100:
                    st.error("❌ Content mix percentages must total 100%")
                    return
                
                # Create form data dictionary
                form_data = {
                    "company_name": company_name,
                    "industry": industry,
                    "website": website,
                    "description": description,
                    "target_audience": target_audience,
                    "brand_tone": brand_tone,
                    "keywords": keywords,
                    "dos": dos,
                    "donts": donts,
                    "content_pillars": content_pillars,
                    "platforms": platforms,
                    "daily_posts": daily_posts,
                    "weekly_posts": weekly_posts,
                    "monthly_posts": monthly_posts,
                    "promotional_percent": promotional,
                    "educational_percent": educational,
                    "engagement_percent": engagement,
                    "logo": logo,
                    "brand_guidelines": brand_guidelines,
                    "sample_posts": sample_posts,
                    "social_profile": st.session_state.get("scraped_profile", {})
                }
                
                # Create the client profile
                with st.spinner("Creating client profile..."):
                    profile = self.create_client_profile(form_data)
                    
                    # Save to database
                    if st.session_state.user_id:
                        save_success = ClientModel.save_client(st.session_state.user_id, profile)
                        
                        if save_success:
                            # Store in session state
                            st.session_state.clients[company_name] = profile
                            st.session_state.current_client_id = profile["client_id"]
                            
                            # Clear auto-fill data
                            st.session_state.scraped_profile = {}
                            for key in list(st.session_state.keys()):
                                if key.startswith("form_"):
                                    del st.session_state[key]
                            
                            # Set success message in session state for persistence
                            st.session_state.success_message = f"✅ Client '{company_name}' created successfully!"
                            st.session_state.show_success_popup = True
                            
                            # Use st.rerun to refresh the page and show the success message
                            st.rerun()
                        else:
                            st.error("❌ Failed to save client to database. Please try again.")
                    else:
                        st.error("❌ User not logged in. Please log in again.")
    
    def render_edit_form(self, client: Dict):
        """Render client edit form."""
        st.header(f"Edit {client['basic_info']['company_name']} Profile")
        
        with st.form("edit_client_form"):
            st.subheader("Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name", value=client['basic_info']['company_name'])
                industry = st.selectbox("Industry", INDUSTRIES, index=INDUSTRIES.index(client['basic_info']['industry']))
            
            with col2:
                website = st.text_input("Website", value=client['basic_info'].get('website', ''))
                target_audience = st.text_area("Target Audience", value=client['basic_info'].get('target_audience', ''))
            
            st.subheader("Brand Voice")
            col1, col2 = st.columns(2)
            
            with col1:
                brand_tone = st.text_input("Brand Tone", value=client['brand_voice']['tone'])
                keywords = st.text_input("Keywords", value=", ".join(client['brand_voice']['keywords']))
            
            with col2:
                dos = st.text_area("Do's", value="\n".join(client['brand_voice']['dos']))
                donts = st.text_area("Don'ts", value="\n".join(client['brand_voice']['donts']))
            
            st.subheader("Content Strategy")
            col1, col2 = st.columns(2)
            
            with col1:
                content_pillars = st.text_area("Content Pillars", value="\n".join(client['content_strategy']['content_pillars']))
                platforms = st.multiselect("Platforms", PLATFORMS, default=client['content_strategy']['platforms'])
            
            with col2:
                monthly_posts = st.number_input(
                    "Monthly Posts",
                    value=client['content_strategy']['posting_frequency']['monthly']
                )
            
            submitted = st.form_submit_button("Update Profile", type="primary", use_container_width=True)
            
            if submitted:
                client['basic_info']['company_name'] = company_name
                client['basic_info']['industry'] = industry
                client['basic_info']['website'] = website
                client['basic_info']['target_audience'] = target_audience
                
                client['brand_voice']['tone'] = brand_tone
                client['brand_voice']['keywords'] = [k.strip() for k in keywords.split(",") if k.strip()]
                client['brand_voice']['dos'] = [d.strip() for d in dos.split("\n") if d.strip()]
                client['brand_voice']['donts'] = [d.strip() for d in donts.split("\n") if d.strip()]
                
                client['content_strategy']['content_pillars'] = [p.strip() for p in content_pillars.split("\n") if p.strip()]
                client['content_strategy']['platforms'] = platforms
                client['content_strategy']['posting_frequency']['monthly'] = monthly_posts
                client['metadata']['last_updated'] = datetime.now().isoformat()
                
                # Update in session and database
                st.session_state.clients[company_name] = client
                ClientModel.update_client(client['client_id'], client)
                
                st.success("Profile updated successfully!")
                st.rerun()