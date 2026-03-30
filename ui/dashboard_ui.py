"""
Dashboard UI module for displaying client overview and performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict

from models.content_model import ContentModel


class DashboardUI:
    """Handle dashboard display."""
    
    @staticmethod
    def render(client: Dict):
        """Render client dashboard."""
        st.header(f"{client['basic_info']['company_name']} Dashboard")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Posts", client['content_strategy']['posting_frequency']['monthly'])
        with col2:
            st.metric("Active Platforms", len(client['content_strategy']['platforms']))
        with col3:
            st.metric("Content Pillars", len(client['content_strategy']['content_pillars']))
        with col4:
            st.metric("Client Since", client['metadata']['created_at'][:10])
        
        # Brand voice overview
        with st.expander("Brand Voice Overview", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Tone:** {client['brand_voice']['tone']}")
                st.markdown("**Do's:**")
                for do in client['brand_voice']['dos'][:3]:
                    st.markdown(f"- {do}")
            with col2:
                st.markdown("**Don'ts:**")
                for dont in client['brand_voice']['donts'][:3]:
                    st.markdown(f"- {dont}")
        
        # Performance section
        st.markdown("---")
        DashboardUI._render_performance(client['client_id'])
    
    @staticmethod
    def _render_performance(client_id: str):
        """Render performance metrics with graphs."""
        st.subheader("Performance Dashboard")
        
        metrics = ContentModel.get_performance_metrics(client_id)
        
        if not metrics:
            st.info("No performance data available. Generate sample data to see insights.")
            
            if st.button("Generate Sample Data"):
                DashboardUI._generate_sample_data(client_id)
                st.rerun()
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(metrics, columns=['platform', 'date', 'impressions', 'likes', 'comments', 'shares'])
        df['date'] = pd.to_datetime(df['date'])
        df['engagement_rate'] = ((df['likes'] + df['comments'] + df['shares']) / df['impressions'] * 100).round(2)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Impressions", f"{df['impressions'].sum():,}")
        with col2:
            st.metric("Total Engagement", f"{df['likes'].sum() + df['comments'].sum() + df['shares'].sum():,}")
        with col3:
            st.metric("Avg. Engagement Rate", f"{df['engagement_rate'].mean():.1f}%")
        with col4:
            st.metric("Platforms Active", df['platform'].nunique())
        
        # Performance trends
        st.subheader("Performance Trends")
        fig = px.line(df, x='date', y=['impressions', 'likes', 'comments', 'shares'],
                     color='platform', title='Performance Metrics Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Platform comparison
        st.subheader("Platform Comparison")
        platform_agg = df.groupby('platform').agg({
            'impressions': 'sum',
            'likes': 'sum',
            'comments': 'sum',
            'shares': 'sum'
        }).reset_index()
        
        fig2 = px.bar(platform_agg, x='platform', y=['impressions', 'likes', 'comments', 'shares'],
                     title='Performance by Platform', barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Download report
        if st.button("Download Performance Report"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="performance_report.csv",
                mime="text/csv"
            )
    
    @staticmethod
    def _generate_sample_data(client_id: str):
        """Generate sample performance data."""
        import random
        platforms = ['Instagram', 'LinkedIn', 'Twitter', 'Facebook']
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).date()
            for platform in platforms:
                impressions = random.randint(1000, 10000)
                likes = random.randint(100, 1000)
                comments = random.randint(10, 200)
                shares = random.randint(5, 100)
                ContentModel.save_performance_metrics(
                    client_id, platform, impressions, likes, comments, shares, date
                )