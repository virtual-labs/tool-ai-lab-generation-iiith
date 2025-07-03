"""
CSS Styles and Theme Management for AI Pipeline Studio
"""

def get_theme_variables(dark_mode=False):
    """Get CSS variables for the selected theme"""
    if dark_mode:
        return {
            'bg_primary': '#0f1419',
            'bg_secondary': '#1a1f2e',
            'bg_tertiary': '#252a3d',
            'bg_accent': '#2d3748',
            'text_primary': '#ffffff',
            'text_secondary': '#a0aec0',
            'text_muted': '#718096',
            'border_color': '#2d3748',
            'accent_primary': '#667eea',
            'accent_secondary': '#764ba2',
            'success': '#48bb78',
            'warning': '#ed8936',
            'error': '#f56565',
            'info': '#4299e1',
            'shadow': 'rgba(0,0,0,0.3)',
            'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }
    else:
        return {
            'bg_primary': '#f8fafc',  # light gray, not pure white
            'bg_secondary': '#ffffff',  # white cards
            'bg_tertiary': '#e2e8f0',  # light blue-gray
            'bg_accent': '#cbd5e1',    # accent for contrast
            'text_primary': '#22223b', # dark blue for text
            'text_secondary': '#3d405b', # slightly lighter dark
            'text_muted': '#6c757d',   # muted gray
            'border_color': '#cbd5e1',
            'accent_primary': '#667eea',
            'accent_secondary': '#764ba2',
            'success': '#38a169',
            'warning': '#d69e2e',
            'error': '#e53e3e',
            'info': '#3182ce',
            'shadow': 'rgba(0,0,0,0.07)',
            'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }

def get_base_css():
    """Get base CSS with theme variables"""
    return """
    <style>
    /* CSS Variables for theming */
    :root {
        --bg-primary: var(--bg-primary);
        --bg-secondary: var(--bg-secondary);
        --bg-tertiary: var(--bg-tertiary);
        --bg-accent: var(--bg-accent);
        --text-primary: var(--text-primary);
        --text-secondary: var(--text-secondary);
        --text-muted: var(--text-muted);
        --border-color: var(--border-color);
        --accent-primary: var(--accent-primary);
        --accent-secondary: var(--accent-secondary);
        --success: var(--success);
        --warning: var(--warning);
        --error: var(--error);
        --info: var(--info);
        --shadow: var(--shadow);
        --gradient: var(--gradient);
    }
    
    /* Base App Styling */
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .main .block-container {
        background: var(--bg-primary);
        padding: 2rem 1rem;
    }
    </style>
    """

def get_component_css():
    """Get CSS for UI components"""
    return """
    <style>
    /* Header Component */
    .modern-header {
        background: var(--gradient);
        padding: 2.5rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px var(--shadow);
        color: white;
        position: relative;
        overflow: hidden;
        word-wrap: break-word; /* Ensure text wraps inside the box */
    }

    .modern-header h1 {
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.18);
        position: relative;
        z-index: 1;
    }

    .modern-header p {
        font-size: 1.3rem;
        margin: 0.7rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }

    /* Navigation Buttons */
    .navigation-buttons {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1.5rem;
    }

    .navigation-buttons button {
        background: var(--gradient);
        border: none;
        border-radius: 14px;
        padding: 1rem 2rem;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 18px rgba(102, 126, 234, 0.18);
    }

    .navigation-buttons button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.22);
    }

    /* Theme Toggle Button */
    .theme-toggle {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: var(--gradient);
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        box-shadow: 0 4px 18px rgba(102, 126, 234, 0.18);
        cursor: pointer;
    }

    .theme-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.22);
    }

    /* Card Components */
    .modern-card {
        background: var(--bg-secondary);
        border-radius: 18px;
        padding: 2rem; /* Ensure sufficient padding for content */
        margin: 1.5rem 0;
        border: 1.5px solid var(--border-color);
        box-shadow: 0 4px 24px var(--shadow);
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        position: relative;
        overflow: hidden;
        display: block; /* Ensure the card behaves as a block element */
        word-wrap: break-word; /* Ensure text wraps inside the box */
    }

    .modern-card:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 8px 32px var(--shadow);
    }

    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient);
        border-radius: 18px 18px 0 0;
    }

    .card-header {
        font-size: 1.7rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 1.2rem;
        display: block; /* Ensure header behaves as a block element */
        text-align: center; /* Center-align the text */
    }

    .card-content {
        color: var(--text-secondary);
        line-height: 1.7;
        font-size: 1.1rem;
        padding: 1rem; /* Add padding to fit text properly */
        word-wrap: break-word; /* Ensure text wraps inside the box */
        text-align: left; /* Align text properly inside the card */
    }

    /* Progress Components */
    .progress-container {
        background: var(--bg-tertiary);
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }

    .progress-bar {
        width: 100%;
        height: 10px;
        background: var(--bg-accent);
        border-radius: 5px;
        overflow: hidden;
        margin: 1rem 0;
    }

    .progress-fill {
        height: 100%;
        background: var(--gradient);
        border-radius: 5px;
        transition: width 0.3s ease;
    }

    /* Step Indicators */
    .step-indicator {
        display: flex;
        align-items: center;
        padding: 1rem; /* Adjust padding for better text fit */
        margin: 0.6rem 0;
        border-radius: 14px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: 1.5px solid var(--border-color);
        word-wrap: break-word; /* Ensure text wraps inside the box */
    }

    .step-pending {
        background: var(--bg-tertiary);
        color: var(--text-muted);
    }

    .step-active {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        transform: scale(1.04);
        box-shadow: 0 4px 18px rgba(102, 126, 234, 0.18);
    }

    .step-complete {
        background: linear-gradient(135deg, var(--success), #68d391);
        color: white;
        box-shadow: 0 4px 18px rgba(72, 187, 120, 0.18);
    }

    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.2rem;
        border-radius: 22px;
        font-size: 1rem;
        font-weight: 700;
    }

    .status-success {
        background: rgba(72, 187, 120, 0.18);
        color: var(--success);
        border: 1.5px solid var(--success);
    }

    .status-warning {
        background: rgba(237, 137, 54, 0.18);
        color: var(--warning);
        border: 1.5px solid var(--warning);
    }

    .status-info {
        background: rgba(66, 153, 225, 0.18);
        color: var(--info);
        border: 1.5px solid var(--info);
    }
    </style>
    """

def get_chat_css():
    """Get CSS for chat components"""
    return """
    <style>
    /* Chat Container */
    .chat-container {
        background: var(--bg-secondary);
        border-radius: 16px;
        padding: 1rem; /* Ensure sufficient padding for content */
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid var(--border-color);
        box-shadow: inset 0 2px 10px var(--shadow);
        display: flex; /* Ensure content aligns properly */
        flex-direction: column; /* Stack messages vertically */
    }

    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        word-wrap: break-word;
        position: relative;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-user {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        margin-left: 2rem;
    }

    .chat-ai {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        margin-right: 2rem;
        border-left: 4px solid var(--accent-primary);
    }

    .chat-system {
        background: var(--bg-accent);
        color: var(--text-secondary);
        font-style: italic;
        text-align: center;
    }
    </style>
    """

def get_streamlit_overrides():
    """Get CSS overrides for Streamlit components"""
    return """
    <style>
    /* Streamlit Component Overrides */
    .stButton > button {
        background: var(--gradient) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 1rem 2rem !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 18px rgba(102, 126, 234, 0.18) !important;
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.22) !important;
    }

    .stButton > button:disabled {
        background: var(--bg-accent) !important;
        color: var(--text-muted) !important;
        box-shadow: none !important;
        transform: none !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: var(--bg-tertiary) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 1.1rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12) !important;
    }

    .stExpander {
        background: var(--bg-secondary) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
    }

    .stProgress > div > div {
        background: var(--gradient) !important;
        border-radius: 5px !important;
    }

    .stFileUploader {
        background: var(--bg-tertiary) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 14px !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }

    .stFileUploader:hover {
        border-color: var(--accent-primary) !important;
        background: var(--bg-secondary) !important;
    }
    </style>
    """

def get_responsive_css():
    """Get responsive design CSS"""
    return """
    <style>
    /* Responsive Design */
    @media (max-width: 768px) {
        .modern-header h1 {
            font-size: 2rem;
        }
        
        .modern-header p {
            font-size: 1rem;
        }
        
        .modern-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .card-header {
            font-size: 1.1rem;
        }
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-secondary);
    }
    </style>
    """

def apply_theme_css(dark_mode=False):
    """Apply complete theme CSS based on mode"""
    theme_vars = get_theme_variables(dark_mode)
    
    # Create dynamic CSS with theme variables
    dynamic_css = f"""
    <style>
    :root {{
        --bg-primary: {theme_vars['bg_primary']};
        --bg-secondary: {theme_vars['bg_secondary']};
        --bg-tertiary: {theme_vars['bg_tertiary']};
        --bg-accent: {theme_vars['bg_accent']};
        --text-primary: {theme_vars['text_primary']};
        --text-secondary: {theme_vars['text_secondary']};
        --text-muted: {theme_vars['text_muted']};
        --border-color: {theme_vars['border_color']};
        --accent-primary: {theme_vars['accent_primary']};
        --accent-secondary: {theme_vars['accent_secondary']};
        --success: {theme_vars['success']};
        --warning: {theme_vars['warning']};
        --error: {theme_vars['error']};
        --info: {theme_vars['info']};
        --shadow: {theme_vars['shadow']};
        --gradient: {theme_vars['gradient']};
    }}
    
    .stApp {{
        background: {theme_vars['bg_primary']};
        color: {theme_vars['text_primary']};
    }}
    
    .main .block-container {{
        background: {theme_vars['bg_primary']};
        padding: 2rem 1rem;
    }}
    </style>
    """
    
    return dynamic_css

def get_all_styles(dark_mode=False):
    """Get all styles combined"""
    return (
        apply_theme_css(dark_mode) +
        get_component_css() +
        get_chat_css() +
        get_streamlit_overrides() +
        get_responsive_css()
    )
