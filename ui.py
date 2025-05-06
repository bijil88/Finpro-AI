import streamlit as st
import re
from utils import extract_sql, escape_sql_for_js

def setup_ui():
    """Setup the custom CSS for the application"""
    st.markdown(
        """
        <style>
        /* Force Light Mode - Override Browser Dark Mode */
        @media (prefers-color-scheme: dark) {
            html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
            [data-testid="baseButton-headerNoPadding"], [data-testid="collapsedControl"], 
            [data-testid="stToolbar"], [data-testid="stDecoration"], 
            [data-testid="stStatusWidget"], [data-testid="stWidgetLabel"],
            [data-testid="stMarkdown"], [data-testid="stTable"] {
                color-scheme: light !important;
                background-color: white !important;
                color: #0f172a !important;
            }
            
            /* Make sure text remains dark in all elements */
            [data-testid="stMarkdown"] p, [data-testid="stMarkdown"] span,
            [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span,
            [data-testid="stHeader"] p, [data-testid="stHeader"] span {
                color: #0f172a !important;
            }
            
            /* Keep inputs light colored with dark text */
            input, textarea, [data-testid="stTextInput"], [data-testid="stTextArea"] {
                background-color: white !important;
                color: #0f172a !important;
            }
        }
        
        /* Modern Design System */
        :root {
            --color-primary: #0ea5e9;       /* Light blue */
            --color-primary-dark: #0284c7;  /* Darker blue */
            --color-secondary: #10b981;     /* Light green */
            --color-secondary-dark: #059669;/* Darker green */
            --color-tertiary: #06b6d4;      /* Teal */
            --color-background: #fefce8;    /* Light yellow background */
            --color-card: #ffffff;          /* White cards */
            --color-text-primary: #0f172a;  /* Dark text */
            --color-text-secondary: #64748b;/* Medium text */
            --border-radius: 12px;
            --drop-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        }
        
        /* Reset and Base styling */
        body {
            background: linear-gradient(135deg, #fefce8 0%, #ecfccb 100%);
            color: var(--color-text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }
        
        .main {
            background: transparent;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
        }
        
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 1rem;
            max-width: 1200px;
        }
        
        /* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #e0f2fe 0%, #bae6fd 30%, #d8b4fe 70%, #c4b5fd 100%);
    border-radius: 0 16px 16px 0;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-left: none;
    box-shadow: 
        inset 0 2px 8px rgba(255, 255, 255, 0.7), 
        inset -2px 0 8px rgba(255, 255, 255, 0.5),
        inset 0 -2px 8px rgba(148, 163, 255, 0.4),
        5px 0 15px -2px rgba(99, 102, 241, 0.15);
    overflow: hidden;
    position: relative;
}

/* Top highlight */
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, 
        rgba(255, 255, 255, 0.7), 
        rgba(212, 190, 255, 0.8), 
        rgba(158, 238, 255, 0.7));
    border-radius: 0 4px 0 0;
    z-index: 3;
}

/* Right side highlight */
[data-testid="stSidebar"]::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 1px;
    background: linear-gradient(to bottom, 
        rgba(255, 255, 255, 0.8), 
        rgba(209, 213, 255, 0.6), 
        rgba(255, 255, 255, 0.4));
    z-index: 2;
}

/* Bottom highlight */
[data-testid="stSidebar"] .main .block-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, 
        rgba(148, 163, 255, 0.5), 
        rgba(175, 205, 255, 0.6), 
        rgba(99, 116, 255, 0.5));
    border-radius: 0 0 4px 0;
    z-index: 2;
}

/* Soft inner glow */
[data-testid="stSidebar"] .main .block-container::before {
    content: '';
    position: absolute;
    top: 10%;
    left: 10%;
    right: 10%;
    bottom: 10%;
    background: radial-gradient(
        circle at center,
        rgba(255, 255, 255, 0.2) 0%,
        rgba(255, 255, 255, 0) 70%
    );
    pointer-events: none;
    z-index: 1;
}
        
        .sidebar-header {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ea580c;
            margin: 1rem 0 1.5rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
            text-align: center;
            text-shadow: none;
        }
        
        .nav-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
.nav-container button {
    background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%);
    border: 1px solid rgba(251, 191, 36, 0.3);
    color: #7c2d12;
    border-radius: 8px;
    transition: all 0.2s ease;
    font-weight: 500;
    text-shadow: 0 1px 1px rgba(255, 255, 255, 0.5);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.nav-container button:hover {
    background: linear-gradient(135deg, #fcd34d 0%, #f59e0b 100%);
    border-color: #d97706;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(234, 88, 12, 0.15);
}

.nav-container button:active {
    transform: translateY(1px);
    box-shadow: inset 0 2px 4px rgba(120, 53, 15, 0.1);
}
        
        .sidebar-stats {
            margin-top: 1rem;
            padding: 0.75rem;
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 8px;
            font-size: 0.875rem;
            color: #475569;
            text-align: center;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .sidebar-footer {
            display: none;
        }
        
        /* App Header - Redesigned with dynamic elements */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem 0;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            border-radius: var(--border-radius);
            box-shadow: var(--drop-shadow);
            position: relative;
            overflow: hidden;
        }
        
        .app-header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.1'/%3E%3C/svg%3E");
            opacity: 0.3;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        
        .app-logo-icon {
            font-size: 2rem;
            color: white;
            margin-right: 0.75rem;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
        }
        
        .app-logo-icon::before {
            content: "⚡️";
            position: relative;
            z-index: 2;
        }
        
        .app-logo-icon::after {
            content: "";
            position: absolute;
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 50%;
            z-index: 1;
        }
        
        .app-name {
            font-size: 1.5rem;
            font-weight: 800;
            color: white;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            letter-spacing: -0.5px;
        }
        
        /* Welcome message - Enhanced with modern styling */
        .welcome-message {
            text-align: center;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background: var(--color-card);
            border-radius: var(--border-radius);
            box-shadow: var(--drop-shadow);
            position: relative;
            overflow: hidden;
            border-left: 5px solid var(--color-primary);
        }
        
        .welcome-message::before {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 150px;
            height: 150px;
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            opacity: 0.05;
            border-radius: 50%;
            transform: translate(40%, -40%);
        }
        
        .welcome-text {
            color: var(--color-text-primary);
            line-height: 1.6;
            font-size: 1.05rem;
            position: relative;
            z-index: 1;
        }
        
        /* Save Page Styling */
        .save-page-container {
            background: var(--color-card);
            border-radius: var(--border-radius);
            box-shadow: var(--drop-shadow);
            padding: 2rem;
            max-width: 800px;
            margin: 0 auto 1rem auto;
            border-top: 5px solid var(--color-secondary);
        }
        
        .save-page-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--color-secondary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .save-page-description {
            color: var(--color-text-secondary);
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        
        .input-label {
            font-weight: 500;
            font-size: 0.9rem;
            color: var(--color-text-primary);
            margin-bottom: 0.5rem;
        }
        
        /* Chat container - Enhanced with dynamic styling */
        .chat-container {
            height: 50vh;
            overflow-y: auto;
            padding: 1.5rem;
            background-color: #fff7ed;
            border-radius: var(--border-radius);
            box-shadow: var(--drop-shadow);
            margin-bottom: 1rem;
            scrollbar-width: thin;
            scrollbar-color: #e5e7eb #fff7ed;
            scroll-behavior: smooth;
            position: relative;
        }
        
        .chat-container::after {
            content: "";
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(to top, #fff7ed, transparent);
            pointer-events: none;
            opacity: 0.8;
            border-bottom-left-radius: var(--border-radius);
            border-bottom-right-radius: var(--border-radius);
        }
        
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: #d1d5db;
            border-radius: 10px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #a1a1aa;
        }
        
        /* Modern Chat messages */
        .chat-message {
            padding: 1rem 1.25rem;
            border-radius: var(--border-radius);
            margin-bottom: 1rem;
            max-width: 85%;
            position: relative;
            line-height: 1.5;
            animation: slideIn 0.3s ease-out;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease;
        }
        
        .chat-message:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, #e0eaff, #d1f5ea);
            margin-left: auto;
            border-bottom-right-radius: 4px;
            color: #1e293b;
            border-right: 3px solid var(--color-primary);
        }
        
        .bot-message {
            background: linear-gradient(135deg, #f0f4ff, #ede9fe);
            border-left: 3px solid #818cf8;
            border-bottom-left-radius: 4px;
        }
        
        .bot-message .message-header {
            color: #6366f1;
        }
        
        .bot-message .message-header::before {
            background-color: #6366f1;
        }
        
        .message-header {
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            color: #6b7280;
            display: flex;
            align-items: center;
            letter-spacing: 0.02em;
        }
        
        .user-message .message-header {
            color: var(--color-primary);
        }
        
        .message-header::before {
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            margin-right: 8px;
            border-radius: 50%;
        }
        
        .user-message .message-header::before {
            background-color: var(--color-primary);
        }
        
        .message-content {
            color: var(--color-text-primary);
            line-height: 1.6;
            font-size: 0.95rem;
        }
        
        /* SQL formatting - Enhanced with modern styling */
        .sql-query {
            background: #e0e7ff;  /* Slightly darker indigo background */
            color: #334155;
            padding: 1.25rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.9rem;
            margin: 0.75rem 0;
            position: relative;
            overflow-x: auto;
            line-height: 1.7;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid #a5b4fc;  /* Slightly darker indigo border */
            white-space: pre;
        }
        
        /* SQL syntax highlighting */
        .sql-query .keyword {
            color: #4f46e5;  /* Indigo for keywords */
            font-weight: 600;
        }
        
        .sql-query .function {
            color: #7e22ce;  /* Purple for functions */
        }
        
        .sql-query .string {
            color: #15803d;  /* Keep green for strings */
        }
        
        .sql-query .number {
            color: #c2410c;  /* Keep orange for numbers */
        }
        
        .sql-query .comment {
            color: #78716c;  /* Stone/grey for comments */
            font-style: italic;
        }
        
        .sql-header {
            font-weight: 600;
            color: #6366f1;  /* Indigo for headers */
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
        }
        
        .alt-title {
            font-weight: 600;
            color: #6366f1;  /* Indigo for alt title */
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
        }
        
        .analysis-box {
            background-color: #f0f9ff;  /* Light sky blue background */
            border-left: 3px solid #60a5fa;  /* Sky blue border */
            padding: 1rem 1.25rem;
            margin: 0.75rem 0 1rem 0;
            border-radius: 0 8px 8px 0;
            line-height: 1.6;
            font-size: 0.95rem;
            color: #4b5563;
        }
        
        .explanation {
            background-color: #faf5ff;  /* Light purple background - more purple than the SQL box */
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin-top: 0.75rem;
            margin-bottom: 1rem;
            font-size: 0.95rem;
            line-height: 1.6;
            color: #4b5563;
            border-left: 3px solid #a78bfa;  /* Medium purple border */
        }
        
        /* Input area - Enhanced with modern styling */
        .input-area {
            background-color: var(--color-card);
            padding: 1rem;
            border-radius: var(--border-radius);
            box-shadow: var(--drop-shadow);
            margin-bottom: 0.75rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border-top: 1px solid rgba(0, 0, 0, 0.03);
        }
        
        .input-area:focus-within {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }
        
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
        }
        
        /* Button Controls - Enhanced with modern styling */
        .button-container {
            display: flex;
            gap: 0.75rem;
        }
        
        .primary-button button {
            background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 500;
            border: none;
            transition: all 0.2s ease;
            width: 100%;
            box-shadow: 0 2px 4px rgba(0, 128, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .primary-button button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 128, 255, 0.3);
            filter: brightness(1.05);
        }
        
        .primary-button button:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 128, 255, 0.1);
        }
        
        .send-button button {
            background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
            color: white;
        }
        
        .save-button-large button {
            background: linear-gradient(135deg, var(--color-secondary), var(--color-secondary-dark));
            color: white;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            transition: all 0.2s ease;
            width: 100%;
            box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
            margin-top: 1rem;
        }
        
        .save-button-large button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3);
            filter: brightness(1.05);
        }
        
        .clear-button button, .save-button button {
            background-color: #f3f4f6;
            color: #4b5563;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            border: none;
            transition: all 0.2s ease;
            width: 100%;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Special styling for save button */
        .save-button button {
            background: linear-gradient(135deg, var(--color-secondary), var(--color-secondary-dark));
            color: white;
        }
        
        .save-button button:disabled {
            background: #e5e7eb;
            color: #9ca3af;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .clear-button button:hover, .save-button button:hover {
            background-color: #e5e7eb;
            color: #374151;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .save-button button:hover:not(:disabled) {
            background: linear-gradient(135deg, var(--color-secondary-dark), var(--color-secondary));
            color: white;
            filter: brightness(1.05);
        }
        
        .clear-button button:active, .save-button button:active {
            transform: translateY(0);
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        /* Save Success Animation */
        @keyframes saveSuccess {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        
        .save-success {
            animation: saveSuccess 0.5s ease;
        }
        
        /* Toast Notification - Enhanced with modern styling */
        .toast-notification {
            position: fixed;
            top: 20px;  /* Changed from bottom to top */
            right: 20px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);  /* Indigo to violet gradient */
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            display: flex;
            align-items: center;
            animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
            border-left: 4px solid #c4b5fd;  /* Light purple border */
            font-weight: 500;
        }
        
        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; visibility: hidden; }
        }
        
        /* Footer - Enhanced with modern styling */
        .footer {
            text-align: center;
            color: var(--color-text-secondary);
            font-size: 0.8rem;
            padding: 1rem 0;
            margin-top: 1rem;
            border-top: 1px solid #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .footer::before {
            content: "⚡";
            font-size: 0.9rem;
        }
        
        /* Empty state styling - Enhanced with modern styling */
        .empty-message {
            text-align: center;
            color: var(--color-text-secondary);
            padding: 2rem;
            font-size: 1rem;
            font-weight: 500;
            background-color: #f8fafc;
            border-radius: 8px;
            border: 1px dashed #cbd5e1;
            margin: 2rem 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 200px;
        }
        
        .empty-message::before {
            content: "💬";
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .chat-message {
                max-width: 90%;
            }
            .app-header {
                padding: 1rem 0;
            }
            .app-name {
                font-size: 1.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Add JavaScript to handle scrolling and other functionality
    st.markdown(
        """
        <script>
            // Function to scroll chat to bottom
            function scrollToBottom() {
                const chatContainer = document.getElementById('chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
            
            // Call after the page loads and with a delay
            window.addEventListener('load', scrollToBottom);
            setTimeout(scrollToBottom, 500);
            
            // Save button click animation
            function animateSaveButton() {
                const saveBtn = document.querySelector('.save-button button');
                if (saveBtn) {
                    saveBtn.classList.add('save-success');
                    setTimeout(() => {
                        saveBtn.classList.remove('save-success');
                    }, 500);
                }
            }
            
            // Show toast notification
            function showToast(message) {
                // Remove any existing toast
                const existingToast = document.querySelector('.toast-notification');
                if (existingToast) {
                    existingToast.remove();
                }
                
                // Create new toast
                const toast = document.createElement('div');
                toast.className = 'toast-notification';
                toast.innerHTML = `<span style="margin-right: 8px;">✓</span> ${message}`;
                document.body.appendChild(toast);
                
                // Remove toast after 3 seconds
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }
            
            // Copy button functionality
            function copyToClipboard(text) {
                navigator.clipboard.writeText(text).then(function() {
                    showToast('SQL query copied to clipboard!');
                }, function(err) {
                    console.error('Could not copy text: ', err);
                });
            }
        </script>
        """,
        unsafe_allow_html=True
    )

def format_bot_message(content):
    """Format bot message with improved SQL formatting."""
    # Extract different sections using regex
    analysis_match = re.search(r"ANALYSIS:(.*?)(?=BEST QUERY:|$)", content, re.DOTALL)
    best_query_match = re.search(r"BEST QUERY:\s*```sql\s*(.*?)\s*```", content, re.DOTALL)
    
    # Modified pattern to get explanation without capturing the SQL part again
    best_explanation_match = re.search(r"```sql.*?```\s*(EXPLANATION:.*?)(?=ALTERNATIVE APPROACH:|$)", content, re.DOTALL)
    
    alt_query_match = re.search(r"ALTERNATIVE APPROACH:\s*```sql\s*(.*?)\s*```", content, re.DOTALL)
    alt_explanation_match = re.search(r"ALTERNATIVE APPROACH:.*?```.*?```\s*(.*?)$", content, re.DOTALL)
    
    # Prepare formatted content
    formatted_content = "<div class='message-content'>"
    
    # Add analysis if found
    if analysis_match:
        analysis = analysis_match.group(1).strip()
        # Format the analysis text to be cleaner
        analysis = analysis.replace('\n', '<br>')
        formatted_content += f"<div class='analysis-box'>{analysis}</div>"
    
    # Add best query if found
    if best_query_match:
        sql_code = best_query_match.group(1).strip()
        # Format SQL keywords
        sql_code = format_sql_keywords(sql_code)
        formatted_content += f"<div class='sql-header'>Best Query</div>"
        formatted_content += f"<div class='sql-query'>{sql_code}</div>"
        
        # Add explanation if found
        if best_explanation_match:
            explanation = best_explanation_match.group(1).strip()
            # Format the explanation text to be cleaner
            explanation = explanation.replace('\n', '<br>')
            formatted_content += f"<div class='explanation'>{explanation}</div>"
    
    # Add alternative query if found
    if alt_query_match:
        alt_sql = alt_query_match.group(1).strip()
        # Format SQL keywords
        alt_sql = format_sql_keywords(alt_sql)
        formatted_content += f"<div class='alt-queries'>"
        formatted_content += f"<div class='alt-title'>Alternative Approach</div>"
        formatted_content += f"<div class='sql-query'>{alt_sql}</div>"
        
        # Add alternative explanation if found
        if alt_explanation_match:
            alt_explanation = alt_explanation_match.group(1).strip()
            # Format the alternative explanation text to be cleaner
            alt_explanation = alt_explanation.replace('\n', '<br>')
            formatted_content += f"<div class='explanation'>{alt_explanation}</div>"
        
        formatted_content += "</div>"  # Close alt-queries div
    
    formatted_content += "</div>"  # Close message-content div
    
    return formatted_content

def format_sql_keywords(sql):
    """Format SQL keywords with styling."""
    # List of SQL keywords to highlight
    keywords = [
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", 
        "OUTER JOIN", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET", "INSERT", 
        "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "AS", "AND", "OR", "NOT", 
        "IN", "BETWEEN", "LIKE", "IS NULL", "IS NOT NULL", "COUNT", "SUM", "AVG", 
        "MIN", "MAX", "DISTINCT", "UNION", "ALL", "CASE", "WHEN", "THEN", "ELSE", "END",
        "WITH", "OVER", "PARTITION BY", "ROW_NUMBER", "RANK", "DENSE_RANK"
    ]
    
    # Sort keywords by length to handle longer keywords first
    keywords.sort(key=len, reverse=True)
    
    # Replace keywords with styled spans
    for keyword in keywords:
        pattern = r'(\b' + re.escape(keyword) + r'\b)'
        sql = re.sub(pattern, f'<span class="keyword">{keyword}</span>', sql, flags=re.IGNORECASE)
    
    return sql

def render_chat():
    """Render the chat container with messages."""
    st.markdown("<div class='chat-container' id='chat-container'>", unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.chat_history:
        # Display chat messages with enhanced formatting
        for idx, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div class="chat-message user-message">
                        <div class="message-header">You</div>
                        <div class="message-content">{message['content']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # Check if this is an exact match from the database
                is_exact_match = message.get("is_exact_match", False)
                
                if is_exact_match:
                    # For exact matches, use simpler formatting
                    st.markdown(
                        f"""
                        <div class="chat-message bot-message">
                            <div class="message-header">SQL Assistant</div>
                            <div class="message-content">
                                {message['content']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Process bot message with improved SQL formatting
                    formatted_content = format_bot_message(message['content'])
                    
                    # Display the bot message without save button
                    st.markdown(
                        f"""
                        <div class="chat-message bot-message">
                            <div class="message-header">SQL Assistant</div>
                            {formatted_content}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Store SQL content for later use by the save button
                    if "BEST QUERY:" in message['content']:
                        sql_content = extract_sql(message['content'])
                        if sql_content:
                            st.session_state.last_question = st.session_state.chat_history[idx-1]['content'] if idx > 0 else ""
                            st.session_state.last_sql = sql_content[0]
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_input_area(submit_callback, clear_callback):
    """Render the input area with text field and buttons."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("<div class='input-area'>", unsafe_allow_html=True)
        # Text input for questions with a proper label
        st.text_input(
            "Query Input",
            key="user_input",
            placeholder="Ask a question about your database...",
            on_change=submit_callback,
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Button row with better alignment
        st.markdown("<div class='input-area' style='padding: 0.3rem 1rem;'>", unsafe_allow_html=True)
        
        # Create buttons in a row - now with Save and Clear
        button_cols = st.columns(2)
        
        # Save button - always enable if there are messages in chat history
        with button_cols[0]:
            st.markdown("<div class='save-button'>", unsafe_allow_html=True)
            save_button_enabled = len(st.session_state.chat_history) >= 2  # At least one Q&A pair
                
            if st.button("Save", use_container_width=True, disabled=not save_button_enabled, help="Save current query"):
                if save_button_enabled:
                    # Get last question and response
                    user_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
                    bot_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "model"]
                    
                    if user_messages and bot_messages:
                        last_question = user_messages[-1]["content"]
                        
                        # Extract SQL from the last bot message
                        last_response = bot_messages[-1]["content"]
                        sql_content = extract_sql(last_response)
                        last_sql = sql_content[0] if sql_content else ""
                        
                        # Set the component value in session state
                        st.session_state.component_value = {
                            "question": last_question,
                            "sql": last_sql
                        }
                        
                        # Add JavaScript to show toast notification
                        st.markdown(
                            """
                            <script>
                                showToast('Thanks for contributing!');
                            </script>
                            """,
                            unsafe_allow_html=True
                        )
                        # Handle save - this will be processed by the handle_save_query function in main.py
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Clear button
        with button_cols[1]:
            st.markdown("<div class='clear-button'>", unsafe_allow_html=True)
            if st.button("Clear", use_container_width=True):
                clear_callback()
                # Clear saved SQL when chat is cleared
                if hasattr(st.session_state, 'last_sql'):
                    del st.session_state.last_sql
                if hasattr(st.session_state, 'last_question'):
                    del st.session_state.last_question
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_save_page(sheets_handler):
    """Render the save page with form inputs for question and SQL query."""
    st.markdown(
        """
        <div class="save-page-container">
            <h2 class="save-page-title">Save SQL Query to Google Sheet</h2>
            <p class="save-page-description">
                Use this form to manually add a question and SQL query pair to the Google Sheet.
                These saved pairs will be used to match future questions and provide quick answers.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create form for entering question and SQL
    with st.form(key="manual_save_form"):
        # Question input
        st.markdown('<div class="input-label">Question</div>', unsafe_allow_html=True)
        question = st.text_area(
            "Enter the question",
            placeholder="What is the count of consents raised for each day in the last week?",
            label_visibility="collapsed",
            height=100
        )
        
        # SQL query input
        st.markdown('<div class="input-label">SQL Query</div>', unsafe_allow_html=True)
        sql_query = st.text_area(
            "Enter the SQL query",
            placeholder="SELECT DATE(created_at) AS date, COUNT(*) AS consent_count FROM customer_consents_requests WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY DATE(created_at) ORDER BY date;",
            label_visibility="collapsed",
            height=200
        )
        
        # Save button
        st.markdown('<div class="save-button-large">', unsafe_allow_html=True)
        submit_button = st.form_submit_button("⚡ Save", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submit_button:
            if question and sql_query:
                # Save to Google Sheets
                success, message = sheets_handler.save_query(question, sql_query)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.warning(f"⚠️ {message}")
            else:
                st.error("❌ Please provide both a question and SQL query")