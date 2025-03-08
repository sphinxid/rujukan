from flask import Flask, render_template, request, redirect, url_for, flash, abort, Response, session
import os
import sqlite3
from models.database import Database
import time
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import logging
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log'), 
                           mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)

# Initialize Flask app with configuration
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_obj = get_config()
    app.config.from_object(config_obj)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Database configuration
    DB_PATH = app.config['DB_PATH']
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Initialize database
    logger.info(f"Initializing database at {DB_PATH}")
    db = Database(DB_PATH)
    
    # Check for old database file and migrate if needed
    OLD_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pastebin.db')
    if os.path.exists(OLD_DB_PATH):
        logger.info(f"Found old database at {OLD_DB_PATH}, migrating data...")
        try:
            # Connect to old database
            old_conn = sqlite3.connect(OLD_DB_PATH)
            old_cursor = old_conn.cursor()
            old_cursor.execute("SELECT * FROM pastes")
            old_pastes = old_cursor.fetchall()
            
            # Connect to new database
            new_conn = sqlite3.connect(DB_PATH)
            new_cursor = new_conn.cursor()
            
            # Migrate data
            for paste in old_pastes:
                # Check if the paste already exists in the new database
                new_cursor.execute("SELECT id FROM pastes WHERE id = ?", (paste[0],))
                if not new_cursor.fetchone():
                    new_cursor.execute(
                        "INSERT INTO pastes (id, content, title, created_at, expires_at, delete_token) VALUES (?, ?, ?, ?, ?, ?)",
                        paste
                    )
            
            new_conn.commit()
            new_conn.close()
            old_conn.close()
            
            logger.info(f"Migration completed. Migrated {len(old_pastes)} pastes.")
            
            # Optionally rename the old database as backup
            backup_path = OLD_DB_PATH + '.bak'
            os.rename(OLD_DB_PATH, backup_path)
            logger.info(f"Renamed old database to {backup_path}")
            
        except Exception as e:
            logger.error(f"Error during database migration: {str(e)}")
    
    # Expiration options mapping (days)
    EXPIRATION_OPTIONS = {
        "1d": 1,
        "2d": 2,
        "7d": 7,
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365
    }
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    @app.route('/')
    def index():
        # Get recent pastes
        recent_pastes = db.get_recent_pastes(10)
        
        # Format timestamps
        for paste in recent_pastes:
            paste['created_at_formatted'] = datetime.fromtimestamp(paste['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template('index.html', recent_pastes=recent_pastes)
    
    @app.route('/paste/new', methods=['GET', 'POST'])
    def new_paste():
        if request.method == 'POST':
            content = request.form.get('content', '')
            title = request.form.get('title', '')
            expiration = request.form.get('expiration', '7d')
            
            # Validate content
            if not content.strip():
                flash('Paste content cannot be empty', 'error')
                return render_template('new.html', expiration_options=EXPIRATION_OPTIONS)
            
            # Get expiration days
            expiration_days = EXPIRATION_OPTIONS.get(expiration, 7)
            
            # Create paste
            paste_id, delete_token = db.create_paste(content, title, expiration_days)
            
            # Store the delete token in the session for this paste
            session[f'delete_token_{paste_id}'] = delete_token
            
            # Set flag to show token once
            session[f'show_token_once_{paste_id}'] = True
            
            # Redirect to the regular paste view (not the token URL)
            flash('Paste created successfully. Your delete token is shown below.', 'success')
            return redirect(url_for('view_paste', paste_id=paste_id))
        
        return render_template('new.html', expiration_options=EXPIRATION_OPTIONS)
    
    @app.route('/paste/<paste_id>')
    def view_paste(paste_id):
        paste = db.get_paste(paste_id)
        
        if not paste:
            abort(404)
        
        # Format timestamps
        paste['created_at_formatted'] = datetime.fromtimestamp(paste['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        if paste['expires_at']:
            paste['expires_at_formatted'] = datetime.fromtimestamp(paste['expires_at']).strftime('%Y-%m-%d %H:%M:%S')
        else:
            paste['expires_at_formatted'] = 'Never'
        
        # Split content into lines for line numbering
        content_lines = paste['content'].split('\n')
        
        # Check if we have a delete token for this paste in the session
        delete_token = session.get(f'delete_token_{paste_id}')
        
        # Check if this is the first time viewing the token
        show_token_once = session.get(f'show_token_once_{paste_id}', True)
        
        # If we've already shown the token before, don't show it again
        if not show_token_once:
            delete_token = None
        elif delete_token:
            # Mark that we've shown the token once
            session[f'show_token_once_{paste_id}'] = False
        
        # Create shareable URL
        shareable_url = request.host_url.rstrip('/') + url_for('view_paste', paste_id=paste_id)
        
        return render_template('view.html', paste=paste, content_lines=content_lines, 
                              delete_token=delete_token, shareable_url=shareable_url)
    
    @app.route('/paste/<paste_id>/raw')
    def view_paste_raw(paste_id):
        paste = db.get_paste(paste_id)
        
        if not paste:
            abort(404)
        
        return Response(paste['content'], mimetype='text/plain')
    
    @app.route('/paste/<paste_id>/token/<token>')
    def view_paste_with_token(paste_id, token):
        paste = db.get_paste(paste_id)
        
        if not paste:
            abort(404)
        
        # Store the delete token in the session
        session[f'delete_token_{paste_id}'] = token
        
        # Reset the show_token_once flag to ensure the token is shown once
        session[f'show_token_once_{paste_id}'] = True
        
        # Redirect to the regular paste view
        return redirect(url_for('view_paste', paste_id=paste_id))
    
    @app.route('/paste/<paste_id>/delete/<token>', methods=['POST'])
    def delete_paste(paste_id, token):
        success = db.delete_paste(paste_id, token)
        
        if success:
            # Remove the token from the session if it exists
            if f'delete_token_{paste_id}' in session:
                session.pop(f'delete_token_{paste_id}')
            # Remove the show_token_once flag if it exists
            if f'show_token_once_{paste_id}' in session:
                session.pop(f'show_token_once_{paste_id}')
            flash('Paste deleted successfully', 'success')
        else:
            flash('Failed to delete paste. Invalid token or paste not found.', 'error')
        
        return redirect(url_for('index'))
    
    @app.template_filter('format_timestamp')
    def format_timestamp(timestamp):
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return 'Never'
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {str(e)}")
        return render_template('500.html'), 500
    
    # Clean up expired pastes on startup
    expired_count = db.cleanup_expired()
    logger.info(f"Startup cleanup: removed {expired_count} expired pastes")
    
    return app, db

# Create the Flask application
app, db = create_app()

# CLI commands
@app.cli.command('cleanup')
def cleanup_expired():
    """Clean up expired pastes."""
    count = db.cleanup_expired()
    print(f"Removed {count} expired pastes.")

if __name__ == '__main__':
    # Run the application
    app.run(host=app.config['HOST'], port=app.config['PORT'])
