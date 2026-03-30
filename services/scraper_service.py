"""
Social Media Scraper Service for fetching profile data.
Uses instaloader when available, falls back to web scraping.
"""

import re
import requests
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Optional, List, Any, Union

try:
    import instaloader  # type: ignore
    INSTALOADER_AVAILABLE = True
except ImportError:
    instaloader = None  # type: ignore
    INSTALOADER_AVAILABLE = False


class SocialMediaScraper:
    """Scrape social media profile data from various platforms."""
    
    def __init__(self):
        self.instaloader_available = INSTALOADER_AVAILABLE
        self.loader: Optional[Any] = None
        
        if self.instaloader_available and instaloader is not None:
            try:
                self.loader = instaloader.Instaloader()
            except Exception:
                self.loader = None
                self.instaloader_available = False
    
    @staticmethod
    def extract_username_from_url(url: str) -> str:
        """Extract username from social media URL."""
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        username = path_parts[0] if path_parts else ""
        
        # Clean up username
        if '?' in username:
            username = username.split('?')[0]
        if '#' in username:
            username = username.split('#')[0]
        
        return username
    
    @staticmethod
    def detect_platform(url: str) -> str:
        """Detect which social media platform the URL is from."""
        url_lower = url.lower()
        
        platform_map = {
            'instagram.com': 'instagram',
            'linkedin.com': 'linkedin',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'facebook.com': 'facebook',
            'tiktok.com': 'tiktok',
            'youtube.com': 'youtube',
            'youtu.be': 'youtube'
        }
        
        for domain, platform in platform_map.items():
            if domain in url_lower:
                return platform
        
        return 'unknown'
    
    def scrape_profile_data(self, url: str) -> Dict[str, Any]:
        """Scrape profile data from social media URL."""
        
        platform = self.detect_platform(url)
        username = self.extract_username_from_url(url)
        
        # Base profile data structure
        profile_data: Dict[str, Any] = {
            "platform": platform,
            "username": username,
            "url": url,
            "company_name": username.replace('-', ' ').replace('_', ' ').title() if username else "",
            "industry": self._detect_industry_from_username(username),
            "description": "",
            "bio": "",
            "followers_count": "N/A",
            "posts_count": "N/A",
            "recent_posts": [],
            "common_topics": [],
            "hashtags_used": [],
            "content_style": "Professional",
            "scrape_time": datetime.now().isoformat(),
            "error": None
        }
        
        if platform == 'unknown':
            profile_data["error"] = "Unsupported platform. Please enter details manually."
            return profile_data
        
        # Try Instagram scraping with instaloader
        if platform == 'instagram' and self.instaloader_available and self.loader:
            try:
                insta_data = self._scrape_instagram(username)
                if insta_data:
                    profile_data.update(insta_data)
                    profile_data["scrape_method"] = "instaloader"
                    return profile_data
            except Exception as e:
                print(f"Instaloader error: {e}")
        
        # Try basic web scraping
        try:
            web_data = self._scrape_with_requests(platform, username)
            if web_data:
                profile_data.update(web_data)
                profile_data["scrape_method"] = "web"
                return profile_data
        except Exception as e:
            print(f"Web scraping error: {e}")
        
        # Return default data based on rules
        rule_data = self._get_rule_based_defaults(platform, username)
        profile_data.update(rule_data)
        profile_data["scrape_method"] = "rule-based"
        
        return profile_data
    
    def _scrape_instagram(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape Instagram data using instaloader."""
        if not self.instaloader_available or self.loader is None:
            return None
        
        try:
            # Type ignore for instaloader operations since it's optional
            profile = instaloader.Profile.from_username(self.loader.context, username)  # type: ignore
            
            recent_posts: List[Dict[str, Any]] = []
            hashtags_used: List[str] = []
            
            for post in profile.get_posts():
                if len(recent_posts) >= 5:
                    break
                
                if post.caption:
                    post_hashtags = re.findall(r'#(\w+)', post.caption)
                    hashtags_used.extend([f"#{tag}" for tag in post_hashtags])
                
                recent_posts.append({
                    "text": post.caption[:200] if post.caption else "No caption",
                    "likes": post.likes,
                    "comments": post.comments,
                    "timestamp": post.date_utc.isoformat() if post.date_utc else None
                })
            
            hashtags_used = list(set(hashtags_used))[:10]
            
            # Determine industry from bio
            industry = self._detect_industry_from_text(profile.biography)
            
            return {
                "company_name": profile.full_name or username,
                "bio": profile.biography,
                "followers_count": f"{profile.followers:,}",
                "posts_count": profile.mediacount,
                "recent_posts": recent_posts,
                "hashtags_used": hashtags_used,
                "industry": industry,
                "content_style": self._analyze_content_style(recent_posts)
            }
        except Exception as e:
            print(f"Instaloader scraping failed: {e}")
            return None
    
    def _scrape_with_requests(self, platform: str, username: str) -> Optional[Dict[str, Any]]:
        """Try to fetch data using simple HTTP requests."""
        
        if platform == 'instagram':
            try:
                url = f"https://www.instagram.com/{username}/?__a=1"
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    graphql = data.get('graphql', {}).get('user', {})
                    if graphql:
                        return {
                            "company_name": graphql.get('full_name', username),
                            "bio": graphql.get('biography', ''),
                            "followers_count": f"{graphql.get('edge_followed_by', {}).get('count', 0):,}",
                            "posts_count": graphql.get('edge_owner_to_timeline_media', {}).get('count', 0)
                        }
            except Exception:
                pass
        
        elif platform == 'linkedin':
            try:
                url = f"https://www.linkedin.com/in/{username}/"
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                
                if response.status_code == 200:
                    html = response.text
                    title_match = re.search(r'<title>(.*?)</title>', html)
                    if title_match:
                        name = title_match.group(1).split('|')[0].strip()
                        return {"company_name": name}
            except Exception:
                pass
        
        return None
    
    def _get_rule_based_defaults(self, platform: str, username: str) -> Dict[str, Any]:
        """Get rule-based default values."""
        
        industry = self._detect_industry_from_username(username)
        
        defaults: Dict[str, Dict[str, Any]] = {
            "Technology": {
                "content_pillars": ["Product Updates", "Tech Trends", "Industry Insights"],
                "keywords": ["innovation", "technology", "digital", "solutions"],
                "tone": "Innovative and Professional"
            },
            "Fashion": {
                "content_pillars": ["Style Guides", "Behind the Scenes", "Collection Launches"],
                "keywords": ["style", "fashion", "trends", "design"],
                "tone": "Trendy and Aspirational"
            },
            "Healthcare": {
                "content_pillars": ["Health Tips", "Medical Advances", "Patient Stories"],
                "keywords": ["health", "wellness", "medical", "care"],
                "tone": "Trustworthy and Compassionate"
            },
            "Finance": {
                "content_pillars": ["Market Updates", "Financial Tips", "Investment Strategies"],
                "keywords": ["finance", "investment", "wealth", "money"],
                "tone": "Authoritative and Educational"
            },
            "Education": {
                "content_pillars": ["Learning Tips", "Student Success", "Educational Resources"],
                "keywords": ["education", "learning", "students", "teaching"],
                "tone": "Encouraging and Informative"
            }
        }
        
        default_data = defaults.get(industry, {
            "content_pillars": ["Company Updates", "Industry News", "Customer Stories"],
            "keywords": ["professional", "quality", "service", "excellence"],
            "tone": "Professional and Engaging"
        })
        
        return {
            "industry": industry,
            "common_topics": default_data["content_pillars"],
            "keywords": default_data["keywords"],
            "content_style": default_data["tone"],
            "company_name": username.replace('-', ' ').replace('_', ' ').title()
        }
    
    def _detect_industry_from_username(self, username: str) -> str:
        """Detect likely industry from username patterns."""
        username_lower = username.lower()
        
        industry_keywords: Dict[str, List[str]] = {
            "Technology": ["tech", "software", "ai", "digital", "cloud", "data", "cyber", "app"],
            "Fashion": ["fashion", "style", "clothing", "wear", "beauty", "makeup"],
            "Healthcare": ["health", "medical", "care", "wellness", "fitness", "clinic"],
            "Finance": ["finance", "bank", "invest", "wealth", "money", "capital"],
            "Education": ["edu", "learn", "school", "academy", "training", "course"],
            "Food": ["food", "restaurant", "cafe", "kitchen", "chef", "cooking"],
            "Real Estate": ["realestate", "property", "home", "housing", "rent"]
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in username_lower for keyword in keywords):
                return industry
        
        return "Other"
    
    def _detect_industry_from_text(self, text: str) -> str:
        """Detect industry from text content."""
        if not text:
            return "Other"
        
        text_lower = text.lower()
        
        industry_keywords: Dict[str, List[str]] = {
            "Technology": ["tech", "software", "ai", "digital", "developer", "app"],
            "Fashion": ["fashion", "style", "clothing", "designer", "trendy"],
            "Healthcare": ["health", "medical", "wellness", "fitness", "doctor"],
            "Finance": ["finance", "invest", "money", "banking", "wealth"],
            "Education": ["education", "learning", "student", "teacher", "school"]
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return "Other"
    
    def _analyze_content_style(self, posts: List[Dict[str, Any]]) -> str:
        """Analyze content style from recent posts."""
        if not posts:
            return "Professional"
        
        has_emojis = any(re.search(r'[\U0001F600-\U0001F650]', post.get('text', '')) for post in posts)
        avg_length = sum(len(post.get('text', '')) for post in posts) / len(posts) if posts else 0
        
        if avg_length < 100:
            style = "Concise"
        elif avg_length < 300:
            style = "Medium-length"
        else:
            style = "Detailed"
        
        if has_emojis:
            style += ", Visual"
        
        return style