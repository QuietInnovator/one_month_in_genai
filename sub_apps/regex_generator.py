import streamlit as st
import re
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime

@dataclass
class RegexResult:
    pattern: str
    explanation: str
    test_examples: List[str]
    non_match_examples: List[str]
    breakdown: Dict[str, str]

# Pattern examples for quick access
PATTERN_EXAMPLES = {
    "Email Validation": "Find valid email addresses",
    "Phone Numbers": "Match US phone numbers with various formats",
    "URLs": "Extract website URLs from text",
    "Dates": "Match dates in MM/DD/YYYY format",
    "Credit Cards": "Validate credit card numbers",
    "IP Addresses": "Find IPv4 addresses",
    "Social Security": "Match SSN patterns (XXX-XX-XXXX)",
    "Postal Codes": "US ZIP codes (5 or 9 digits)",
    "Passwords": "Strong password validation (8+ chars, mixed case, numbers)",
    "Hexadecimal": "Match hexadecimal color codes",
    "Time Format": "Match time in HH:MM format",
    "File Extensions": "Find files with specific extensions"
}

def simulate_ai_regex_generation(description: str, complexity: str, language: str) -> RegexResult:
    """
    Simulates AI regex generation. In a real app, this would call OpenAI API.
    For demo purposes, this provides predefined patterns for common use cases.
    """
    
    # Common regex patterns (simulating AI responses)
    patterns = {
        "email": {
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "explanation": "Matches email addresses with standard format: username@domain.extension",
            "test_examples": ["user@example.com", "test.email+tag@domain.co.uk", "simple@test.org"],
            "non_match_examples": ["invalid.email", "@domain.com"],
            "breakdown": {
                "[a-zA-Z0-9._%+-]+": "Username: letters, numbers, and common special chars",
                "@": "Literal @ symbol",
                "[a-zA-Z0-9.-]+": "Domain name with letters, numbers, dots, hyphens",
                "\\.": "Literal dot (escaped)",
                "[a-zA-Z]{2,}": "Top-level domain (2 or more letters)"
            }
        },
        "phone": {
            "pattern": r"(\+1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
            "explanation": "Matches US phone numbers in various formats with optional country code",
            "test_examples": ["(555) 123-4567", "555-123-4567", "+1 555.123.4567"],
            "non_match_examples": ["123-45-6789", "555-12-3456"],
            "breakdown": {
                "(\+1[-.\s]?)?": "Optional +1 country code with separator",
                "\(?": "Optional opening parenthesis",
                "([0-9]{3})": "Area code (3 digits)",
                "\)?": "Optional closing parenthesis",
                "[-.\s]?": "Optional separator (dash, dot, or space)",
                "([0-9]{3})": "Exchange code (3 digits)",
                "([0-9]{4})": "Line number (4 digits)"
            }
        },
        "url": {
            "pattern": r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?",
            "explanation": "Matches HTTP and HTTPS URLs with optional ports, paths, queries, and fragments",
            "test_examples": ["https://example.com", "http://site.com:8080/path?query=value#anchor"],
            "non_match_examples": ["ftp://example.com", "not-a-url"],
            "breakdown": {
                "https?": "HTTP or HTTPS protocol",
                "://": "Protocol separator",
                "(?:[-\w.])+": "Domain name with letters, numbers, dots, hyphens",
                "(?:\:[0-9]+)?": "Optional port number",
                "(?:/(?:[\w/_.])*)?": "Optional path",
                "(?:\?(?:[\w&=%.])*)?": "Optional query string",
                "(?:\#(?:[\w.])*)?": "Optional fragment"
            }
        },
        "date": {
            "pattern": r"(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/([0-9]{4})",
            "explanation": "Matches dates in MM/DD/YYYY format with basic validation",
            "test_examples": ["01/15/2023", "12/31/2024", "06/30/2025"],
            "non_match_examples": ["13/01/2023", "01/32/2023"],
            "breakdown": {
                "(0[1-9]|1[0-2])": "Month: 01-12",
                "/": "Literal slash separator",
                "(0[1-9]|[12][0-9]|3[01])": "Day: 01-31",
                "/": "Literal slash separator",
                "([0-9]{4})": "Year: 4 digits"
            }
        }
    }
    
    # Simple keyword matching to return appropriate pattern
    desc_lower = description.lower()
    if "email" in desc_lower:
        return RegexResult(**patterns["email"])
    elif "phone" in desc_lower:
        return RegexResult(**patterns["phone"])
    elif "url" in desc_lower or "website" in desc_lower:
        return RegexResult(**patterns["url"])
    elif "date" in desc_lower:
        return RegexResult(**patterns["date"])
    else:
        # Default simple pattern
        return RegexResult(
            pattern=r"\b\w+\b",
            explanation="Basic word matching pattern - matches whole words",
            test_examples=["hello", "world", "test123"],
            non_match_examples=["!", "@#$"],
            breakdown={
                r"\b": "Word boundary",
                r"\w+": "One or more word characters",
                r"\b": "Word boundary"
            }
        )

def highlight_matches(text: str, pattern: str) -> str:
    """Highlight regex matches in text with HTML"""
    try:
        highlighted = re.sub(
            pattern, 
            r'<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;">\g<0></mark>', 
            text
        )
        return highlighted
    except re.error:
        return text

def test_regex_pattern(pattern: str, test_text: str) -> Tuple[List[str], bool]:
    """Test regex pattern against text and return matches"""
    try:
        matches = re.findall(pattern, test_text)
        is_valid = True
        return matches, is_valid
    except re.error as e:
        return [], False

def main():
    # Header
    st.title("🔍 AI Regex Generator")
    st.markdown("### Convert plain English descriptions into working regular expressions")
    
    # Sidebar with examples
    st.sidebar.subheader("💡 Quick Examples")
    st.sidebar.markdown("Click any example to auto-fill:")
    
    for name, desc in PATTERN_EXAMPLES.items():
        if st.sidebar.button(name, key=f"example_{name}"):
            st.session_state.description = desc
            st.rerun()
    
    # Main input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        description = st.text_area(
            "Pattern Description",
            value=st.session_state.get('description', ''),
            placeholder="e.g., Find all email addresses in text",
            height=100,
            help="Describe what you want to match in plain English"
        )
    
    with col2:
        complexity = st.selectbox(
            "Complexity Level",
            ["Simple", "Intermediate", "Advanced"],
            help="Affects how strict/flexible the regex will be"
        )
        
        language = st.selectbox(
            "Target Language",
            ["Python", "JavaScript", "Java", "PHP", "General"],
            help="Adjusts syntax for specific languages"
        )
    
    # Generate button
    if st.button("🚀 Generate Regex", type="primary", disabled=not description.strip()):
        with st.spinner("Generating regex pattern..."):
            try:
                result = simulate_ai_regex_generation(description, complexity, language)
                
                # Store result in session state
                st.session_state.regex_result = result
                
                st.success("✅ Regex Generated Successfully!")
                
            except Exception as e:
                st.error(f"Error generating regex: {str(e)}")
                return
    
    # Display results if available
    if hasattr(st.session_state, 'regex_result'):
        result = st.session_state.regex_result
        
        # Pattern display
        st.subheader("📋 Generated Pattern")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(result.pattern, language="regex")
        with col2:
            if st.button("📋 Copy Pattern"):
                st.info("Pattern copied! (Use Ctrl+C to copy from code block)")
        
        # Explanation
        st.subheader("📖 Explanation")
        st.write(result.explanation)
        
        # Pattern breakdown
        with st.expander("🔍 Pattern Breakdown", expanded=False):
            for component, meaning in result.breakdown.items():
                st.markdown(f"**`{component}`** - {meaning}")
        
        # Test examples
        st.subheader("✅ Matching Examples")
        for i, example in enumerate(result.test_examples, 1):
            st.markdown(f"{i}. `{example}`")
        
        st.subheader("❌ Non-Matching Examples")
        for i, example in enumerate(result.non_match_examples, 1):
            st.markdown(f"{i}. `{example}`")
        
        # Interactive testing
        st.subheader("🧪 Test Your Regex")
        
        test_text = st.text_area(
            "Test Text",
            placeholder="Paste text here to test the regex pattern...",
            height=150,
            key="test_text"
        )
        
        if test_text:
            matches, is_valid = test_regex_pattern(result.pattern, test_text)
            
            if is_valid:
                if matches:
                    st.success(f"Found {len(matches)} matches:")
                    
                    # Display matches
                    for i, match in enumerate(matches[:10], 1):  # Limit to first 10
                        st.write(f"{i}. `{match}`")
                    
                    if len(matches) > 10:
                        st.info(f"... and {len(matches) - 10} more matches")
                    
                    # Highlight matches in original text
                    st.subheader("🎯 Highlighted Matches")
                    highlighted = highlight_matches(test_text, result.pattern)
                    st.markdown(highlighted, unsafe_allow_html=True)
                    
                else:
                    st.warning("No matches found in the test text")
            else:
                st.error("Invalid regex pattern - cannot test")
        
        # Code examples
        st.subheader("💻 Code Examples")
        
        code_examples = {
            "Python": f'''import re

pattern = r"{result.pattern}"
text = "your text here"

# Find all matches
matches = re.findall(pattern, text)
print(f"Found {{len(matches)}} matches: {{matches}}")

# Check if text matches pattern
if re.match(pattern, text):
    print("Text matches the pattern!")

# Replace matches
new_text = re.sub(pattern, "REPLACEMENT", text)''',
            
            "JavaScript": f'''const pattern = /{result.pattern}/g;
const text = "your text here";

// Find all matches
const matches = text.match(pattern);
console.log(`Found ${{matches?.length || 0}} matches:`, matches);

// Test if pattern matches
if (pattern.test(text)) {{
    console.log("Text matches the pattern!");
}}

// Replace matches
const newText = text.replace(pattern, "REPLACEMENT");''',
            
            "Java": f'''import java.util.regex.*;

String pattern = "{result.pattern}";
String text = "your text here";

Pattern p = Pattern.compile(pattern);
Matcher m = p.matcher(text);

// Find all matches
while (m.find()) {{
    System.out.println("Match: " + m.group());
}}

// Check if text matches
boolean matches = p.matcher(text).matches();'''
        }
        
        selected_lang = st.selectbox("Choose Language", list(code_examples.keys()))
        st.code(code_examples[selected_lang], language=selected_lang.lower())
        
        # Export options
        st.subheader("💾 Export & Save")
        
        export_data = {
            "description": description,
            "pattern": result.pattern,
            "explanation": result.explanation,
            "examples": result.test_examples,
            "created_at": datetime.now().isoformat()
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📁 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"regex_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            csv_data = f"Description,Pattern,Explanation\n\"{description}\",\"{result.pattern}\",\"{result.explanation}\""
            st.download_button(
                "📊 Download CSV",
                data=csv_data,
                file_name=f"regex_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col3:
            txt_data = f"Description: {description}\n\nPattern: {result.pattern}\n\nExplanation: {result.explanation}"
            st.download_button(
                "📄 Download TXT",
                data=txt_data,
                file_name=f"regex_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("🔍 **AI Regex Generator** - Convert natural language to regular expressions")

if __name__ == "__main__":
    main()
