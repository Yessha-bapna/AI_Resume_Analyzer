from __init__ import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5001))
    
    # Run in production mode on Render
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
