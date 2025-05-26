import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import io
import re
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime



# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1e3a8a;
    text-align: center;
    margin-bottom: 2rem;
}
.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #3b82f6;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.highlight-box {
    background-color: #f0f9ff;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #3b82f6;
    margin: 1rem 0;
}
.error-box {
    background-color: #fef2f2;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ef4444;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def get_secret(key, default=None):
    """Get secret from environment variables or Streamlit secrets"""
    # Try environment variable first
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Fallback to Streamlit secrets
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        return default

def clean_text(text):
    """Clean and normalize text content"""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def scrape_website(url, max_pages=5):
    """Scrape website content with error handling"""
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Extract text content
        content = {
            'title': soup.title.string if soup.title else '',
            'headings': [],
            'paragraphs': [],
            'navigation': [],
            'all_text': ''
        }
        
        # Get headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if heading.get_text(strip=True):
                content['headings'].append(clean_text(heading.get_text()))
        
        # Get paragraphs
        for para in soup.find_all('p'):
            text = clean_text(para.get_text())
            if text and len(text) > 20:  # Filter out very short paragraphs
                content['paragraphs'].append(text)
        
        # Get navigation text
        for nav in soup.find_all(['nav', 'menu']):
            nav_text = clean_text(nav.get_text())
            if nav_text:
                content['navigation'].append(nav_text)
        
        # Get all text content
        content['all_text'] = clean_text(soup.get_text())
        
        return content, None
        
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching website: {str(e)}"
    except Exception as e:
        return None, f"Error parsing website: {str(e)}"

def analyze_website_voice(content, openai_api_key):
    """Analyze website voice using OpenAI GPT-4"""
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Prepare content for analysis
        text_sample = content['all_text'][:8000]  # Limit text for API
        
        prompt = f"""
        Analyze the voice, tone, and language style of this website content. Provide a comprehensive analysis in the following format:

        **VOICE ANALYSIS:**
        - Primary voice characteristics
        - Brand personality traits
        - Communication style

        **TONE ANALYSIS:**
        - Overall tone (professional, casual, friendly, authoritative, etc.)
        - Emotional qualities
        - Consistency assessment

        **LANGUAGE ANALYSIS:**
        - Language complexity level
        - Vocabulary characteristics
        - Writing style patterns

        **KEY WORDS & PHRASES:**
        - Most frequently used words
        - Distinctive phrases and expressions
        - Industry-specific terminology

        **SENTENCE STRUCTURE:**
        - Typical sentence length and complexity
        - Common sentence patterns
        - Writing flow and rhythm

        **PARAGRAPH STRUCTURE:**
        - Paragraph length and organization
        - Information hierarchy
        - Content flow patterns

        **OVERALL ASSESSMENT:**
        - Strengths of the communication style
        - Areas for improvement
        - Target audience alignment

        **RECOMMENDATIONS:**
        - Suggestions for voice consistency
        - Opportunities for enhancement

        Website Content to Analyze:
        Title: {content.get('title', 'N/A')}
        
        Main Content:
        {text_sample}
        
        Key Headings: {' | '.join(content.get('headings', [])[:10])}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert copywriter and brand voice analyst. Provide detailed, actionable insights about website voice and tone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content, None
        
    except Exception as e:
        return None, f"Error analyzing content: {str(e)}"

def create_pdf_report(analysis, website_url, content):
    """Create PDF report from analysis"""
    try:
        # Create a BytesIO buffer for the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#1f2937'),
            spaceAfter=8,
            spaceBefore=12
        )
        
        # Story container
        story = []
        
        # Title page
        story.append(Paragraph("Website Voice Analysis Report", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Website:</b> {website_url}", styles['Normal']))
        story.append(Paragraph(f"<b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"<b>Page Title:</b> {content.get('title', 'N/A')}", styles['Normal']))
        story.append(PageBreak())
        
        # Main analysis content
        story.append(Paragraph("Voice & Tone Analysis", heading_style))
        
        # Split analysis into sections and format
        analysis_lines = analysis.split('\n')
        current_section = ""
        
        for line in analysis_lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a section header (contains **text**)
            if line.startswith('**') and line.endswith('**'):
                section_title = line.strip('*').strip(':')
                story.append(Paragraph(section_title, subheading_style))
            elif line.startswith('- '):
                # Bullet point
                story.append(Paragraph(line, styles['Normal']))
            else:
                # Regular paragraph
                story.append(Paragraph(line, styles['Normal']))
            
            story.append(Spacer(1, 6))
        
        # Website statistics
        story.append(PageBreak())
        story.append(Paragraph("Website Content Statistics", heading_style))
        
        stats = [
            f"Total Content Length: {len(content.get('all_text', ''))} characters",
            f"Number of Headings: {len(content.get('headings', []))}",
            f"Number of Paragraphs: {len(content.get('paragraphs', []))}",
            f"Average Paragraph Length: {sum(len(p) for p in content.get('paragraphs', [])) // max(len(content.get('paragraphs', [])), 1)} characters"
        ]
        
        for stat in stats:
            story.append(Paragraph(stat, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue(), None
        
    except Exception as e:
        return None, f"Error creating PDF: {str(e)}"

def main():
    """Main Streamlit application"""
    st.markdown('<h1 class="main-header">🎯 Website Voice Analyzer</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="highlight-box">
    <p><strong>Analyze your website's voice and tone with AI-powered insights.</strong></p>
    <p>This tool scrapes your website content and uses GPT-4 to analyze the voice, tone, language style, and provides actionable recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=get_secret("OPENAI_API_KEY", ""),
            type="password",
            help="Enter your OpenAI API key. You can get one from https://platform.openai.com/"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Report Includes:")
        st.markdown("""
        - Voice characteristics
        - Tone analysis
        - Language style
        - Key words & phrases
        - Sentence structure
        - Paragraph analysis
        - Overall assessment
        - Recommendations
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="section-header">Enter Website URL</h2>', unsafe_allow_html=True)
        
        # URL input
        website_url = st.text_input(
            "Website URL",
            placeholder="https://example.com or example.com",
            help="Enter the website URL you want to analyze"
        )
        
        # Analysis button
        if st.button("🔍 Analyze Website Voice", type="primary", use_container_width=True):
            if not website_url:
                st.error("Please enter a website URL")
                return
            
            if not openai_api_key:
                st.error("Please enter your OpenAI API key in the sidebar")
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Scrape website
                status_text.text("🔍 Scraping website content...")
                progress_bar.progress(20)
                
                content, error = scrape_website(website_url)
                if error:
                    st.markdown(f'<div class="error-box"><strong>Error:</strong> {error}</div>', unsafe_allow_html=True)
                    return
                
                progress_bar.progress(40)
                status_text.text("📝 Content extracted successfully. Analyzing with AI...")
                
                # Step 2: Analyze with OpenAI
                analysis, error = analyze_website_voice(content, openai_api_key)
                if error:
                    st.markdown(f'<div class="error-box"><strong>Error:</strong> {error}</div>', unsafe_allow_html=True)
                    return
                
                progress_bar.progress(70)
                status_text.text("📊 Analysis complete. Generating PDF report...")
                
                # Step 3: Generate PDF
                pdf_data, error = create_pdf_report(analysis, website_url, content)
                if error:
                    st.markdown(f'<div class="error-box"><strong>Error:</strong> {error}</div>', unsafe_allow_html=True)
                    return
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Display results
                st.success("🎉 Analysis completed successfully!")
                
                # Show preview of analysis
                with st.expander("📄 View Analysis Preview", expanded=True):
                    st.markdown(analysis)
                
                # Download button
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name=f"voice_analysis_{urlparse(website_url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.markdown(f'<div class="error-box"><strong>Unexpected Error:</strong> {str(e)}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h3 class="section-header">💡 Tips</h3>', unsafe_allow_html=True)
        st.markdown("""
        **For best results:**
        - Use complete website URLs
        - Ensure the website is publicly accessible
        - Make sure your OpenAI API key has sufficient credits
        - The analysis focuses on main content areas
        
        **Privacy:**
        - Your API key is not stored
        - Website content is only sent to OpenAI for analysis
        - No data is permanently stored
        """)
        
        st.markdown("---")
        st.markdown("### 🚀 Example URLs to try:")
        st.code("https://stripe.com")
        st.code("https://openai.com")
        st.code("https://apple.com")

if __name__ == "__main__":
    main()
