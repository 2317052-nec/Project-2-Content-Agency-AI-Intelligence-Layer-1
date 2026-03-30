"""
Constants used throughout the application.
"""

# Industry categories
INDUSTRIES = [
    "Technology", "Fashion", "Healthcare", "Finance", 
    "Education", "Real Estate", "Food & Beverage", 
    "Travel", "Entertainment", "Other"
]

# Social media platforms
PLATFORMS = ["Instagram", "LinkedIn", "Twitter", "Facebook", "Blog", "Newsletter"]

# Platform-specific content guidelines
PLATFORM_GUIDELINES = {
    "LinkedIn": """
        - Professional and formal tone
        - Focus on industry insights and thought leadership
        - Length: 150-300 words
        - Include a call-to-action
    """,
    "Instagram": """
        - Visual-first approach
        - Conversational tone
        - Use 5-10 relevant hashtags
        - Length: 138-150 characters optimal
    """,
    "Twitter": """
        - Concise and impactful
        - Maximum 280 characters
        - Use 1-2 hashtags max
    """,
    "Facebook": """
        - Conversational and engaging
        - Length: 40-80 characters optimal
        - Include questions to drive comments
    """,
    "Blog": """
        - In-depth and informative
        - Length: 1500-2500 words
        - Use headings and subheadings
    """,
    "Newsletter": """
        - Personal and engaging
        - Include a clear subject line
        - Add a personal note from the author
    """
}

# Seasonal themes by quarter
SEASONAL_THEMES = {
    "Q1": ["New Year Planning", "Winter Solutions", "Year-ahead Trends", "Goal Setting"],
    "Q2": ["Spring Updates", "Mid-year Reviews", "Summer Preparation", "Industry Events"],
    "Q3": ["Back to School", "Fall Planning", "Holiday Prep", "Year-end Strategy"],
    "Q4": ["Year-end Review", "Holiday Campaigns", "New Year Prep", "Annual Reports"]
}

# Content type colors
CONTENT_TYPE_COLORS = {
    "Educational": "#3b82f6",
    "Promotional": "#10b981",
    "Engagement": "#f97316",
    "Industry News": "#8b5cf6",
    "Client Spotlight": "#ec4899"
}