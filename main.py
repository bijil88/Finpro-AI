import streamlit as st
from ui import setup_ui, render_chat, render_input_area, render_save_page
from sql_assistant import get_sql_suggestions
from google_sheets_handler import GoogleSheetsHandler
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if API key exists
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

# Initialize Google Sheets handler
sheets_handler = GoogleSheetsHandler()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'component_value' not in st.session_state:
    st.session_state.component_value = None
if 'page' not in st.session_state:
    st.session_state.page = "chat"

# Configure page
st.set_page_config(layout="wide", page_title="FinPro.ai", page_icon="⚡️")

# Apply custom CSS
setup_ui()

# Create sidebar for navigation
with st.sidebar:
    st.markdown("<div class='sidebar-header'>FinPro SQL AI</div>", unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
    
    if st.button("💬 Chat", use_container_width=True, 
                key="chat_nav", 
                help="Ask questions and get SQL queries"):
        st.session_state.page = "chat"
        st.rerun()
        
    if st.button("⚡ Contribute", use_container_width=True, 
                key="save_nav", 
                help="Manually save a question and SQL query pair"):
        st.session_state.page = "save"
        st.rerun()
    
    query_count = sheets_handler.get_query_count()
    st.markdown(f"<div class='sidebar-stats'>Saved Queries: {query_count}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer in sidebar
    st.markdown(
        """
        <div class="sidebar-footer">
            Finpro Innovate v2.1<br>
            Powered by Gemini
        </div>
        """, 
        unsafe_allow_html=True
    )

# Callback for the submit button
def submit_query():
    if st.session_state.user_input:
        user_query = st.session_state.user_input
        
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Reset the input field by updating session state
        st.session_state.user_input = ""
        st.session_state.submitted = True

# Callback to clear chat
def clear_chat():
    st.session_state.chat_history = []
    st.session_state.submitted = False

# Handle saving queries
def handle_save_query():
    """Handle saving queries from the UI component value."""
    # Get the component value from the UI
    component_value = st.session_state.get("component_value")
    
    if component_value:
        question = component_value.get("question")
        sql = component_value.get("sql")
        
        if question and sql:
            try:
                success, message = sheets_handler.save_query(question, sql)
                if success:
                    st.toast(f"✅ {message}", icon="✅")
                    # Clear the component value after successful save
                    st.session_state.component_value = None
                else:
                    st.warning(f"⚠️ {message}", icon="⚠️")
            except Exception as e:
                st.error(f"❌ Error saving query: {str(e)}")
        else:
            st.error("❌ Missing question or SQL query")

# Main layout container
st.markdown("<div class='app-container'>", unsafe_allow_html=True)

# Prominent app header - always visible at the top
st.markdown(
    """
    <div class="app-header">
        <div class="logo-container">
            <div class="app-logo-icon"></div>
            <div class="app-name">FinPro SQL AI</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Check which page to display
if st.session_state.page == "chat":
    # Welcome text section below header - visible regardless of chat history
    st.markdown(
        """
        <div class="welcome-message">
            <p class="welcome-text">
                Ask me any question about your Finpro TSP database, and I'll generate the
                perfect SQL query for you. Try questions like <span style="font-style: italic; color: #6d28d9;">"Give the count of consents raised for each day in the last week"</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render chat area
    render_chat()

    # Render input area
    render_input_area(submit_query, clear_chat)

elif st.session_state.page == "save":
    # Render save page
    render_save_page(sheets_handler)

st.markdown("</div>", unsafe_allow_html=True)  # Close app-container

# Process submitted query
if st.session_state.submitted and st.session_state.page == "chat":
    # Get SQL suggestions for the last user message
    user_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
    if user_messages:
        last_user_query = user_messages[-1]["content"]
        
        # Don't process if there's already a response
        bot_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "model"]
        if len(bot_messages) < len(user_messages):
            # First check for exact match in Google Sheets
            exact_match = sheets_handler.find_exact_match(last_user_query)
            
            if exact_match:
                # If exact match found, use the corresponding SQL query
                sql_suggestions = f"""
ANALYSIS:
Found exact match in query database.

BEST QUERY:
```sql
{exact_match['sql']}
```

This query was previously saved and verified.
"""
                # Add bot response to chat history without extra formatting
                st.session_state.chat_history.append({
                    "role": "model", 
                    "content": sql_suggestions,
                    "is_exact_match": True  # Add flag to indicate this is an exact match
                })
            else:
                # If no exact match, proceed with normal flow
                with st.spinner("Generating SQL query..."):
                    # Get similar queries from Google Sheets
                    similar_queries = sheets_handler.find_similar_queries(last_user_query)
                    
                    # Get SQL suggestions using both chat history and similar queries
                    sql_suggestions = get_sql_suggestions(
                        last_user_query, 
                        st.session_state.chat_history[:-1],
                        similar_queries,
                        sheets_handler  # Pass the sheets_handler instance
                    )
                    # Add bot response to chat history
                    st.session_state.chat_history.append({
                        "role": "model", 
                        "content": sql_suggestions,
                        "is_exact_match": False
                    })
            
    # Reset submission flag
    st.session_state.submitted = False
    st.rerun()

# Handle saving queries
handle_save_query()

# Minimal footer
st.markdown(
    """
    <div class="footer">
        Finpro Innovate v2.1 · Powered by Gemini
    </div>
    """,
    unsafe_allow_html=True
)