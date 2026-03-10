from flask import request, session, current_app
from flask_babel import Babel, gettext, ngettext
import os

# Initialize Babel
babel = Babel()

def get_locale():
    """
    Determine best locale to use:
    1. User's session preference
    2. URL parameter (?lang=en or ?lang=de)
    3. Browser's Accept-Language header
    4. Default to 'en'
    """
    # Check URL parameter first
    if request and request.args and request.args.get('lang'):
        lang = request.args.get('lang')
        if lang in ['en', 'de']:
            session['language'] = lang
            return lang
    
    # Check session preference
    if session and 'language' in session:
        return session['language']
    
    # Check browser preference
    if request and request.accept_languages:
        browser_lang = request.accept_languages.best_match(['en', 'de'])
        if browser_lang:
            # Store in session for consistency
            session['language'] = browser_lang
            return browser_lang
    
    # Default to English
    if session:
        session['language'] = 'en'
    return 'en'

# Configure Babel to find translations
def configure_babel(app):
    """Configure Babel to find translations"""
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    return babel

def get_translations():
    """
    Get available translations
    """
    translations_dir = os.path.join(current_app.root_path, 'translations') if current_app else 'translations'
    if os.path.exists(translations_dir):
        return [d for d in os.listdir(translations_dir) 
                if os.path.isdir(os.path.join(translations_dir, d))]
    return ['en', 'de']

# Translation helpers for templates
def t(key, **kwargs):
    """Translation helper function"""
    return gettext(key, **kwargs)

def tn(singular, plural, num, **kwargs):
    """Translation helper for plural forms"""
    return ngettext(singular, plural, num, **kwargs)
