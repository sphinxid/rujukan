# Rujukan Web Application

A simple and elegant paste sharing web application built with Flask and SQLite.

## Features

- Create text pastes with customizable expiration times
- View pastes in both raw text and formatted HTML modes
- Line numbering for easy reference
- Delete pastes using a secret token
- Recent pastes displayed on the home page
- Responsive design for mobile and desktop
- Share links with copy-to-clipboard functionality
- CSRF protection for enhanced security

## Installation

1. Clone the repository or download the source code
2. Create a virtual environment (recommended)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Development Usage

1. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

2. Run the application in development mode:
```bash
python app.py
```

3. Open your web browser and navigate to `http://127.0.0.1:5000`

## Production Deployment

### Using Gunicorn (Recommended)

1. Install Gunicorn (included in requirements.txt)
2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file and set FLASK_ENV=production
```

3. Run with Gunicorn:
```bash
gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app
```

### Using Systemd Service

1. Copy the service file to systemd directory:
```bash
sudo cp rujukan.service /etc/systemd/system/
# Edit the file to update paths if necessary
```

2. Enable and start the service:
```bash
sudo systemctl enable rujukan
sudo systemctl start rujukan
```

3. Check status:
```bash
sudo systemctl status rujukan
```

### Using Nginx as a Reverse Proxy

For a production environment, it's recommended to use Nginx as a reverse proxy:

1. Install Nginx:
```bash
sudo apt update
sudo apt install nginx
```

2. Create a Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/rujukan
```

3. Add the following configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/rujukan /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## Expiration Options

Pastes can be set to expire after:
- 1 day
- 2 days
- 7 days (default)
- 1 month
- 3 months
- 6 months
- 1 year

## Project Structure

```
rujukan/
├── app.py                 # Main application file
├── config.py              # Configuration module
├── wsgi.py                # WSGI entry point for production
├── models/
│   └── database.py        # Database module for SQLite
├── static/
│   ├── css/
│   │   └── style.css      # CSS styles
│   └── js/
│       └── main.js        # JavaScript functionality
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── new.html           # Create new paste
│   ├── view.html          # View paste
│   ├── 404.html           # Not found error page
│   └── 500.html           # Server error page
├── data/                  # Database storage directory
├── logs/                  # Application logs directory
└── requirements.txt       # Python dependencies
```

## Database

The application uses SQLite for data storage. The database file `rujukan.db` will be created automatically in the `data` directory when the application is first run. If an old database file is detected, data will be automatically migrated.

## Cleanup

Expired pastes are automatically cleaned up when the application starts. You can also manually clean up expired pastes using the Flask CLI:

```bash
flask cleanup
```

## Security Features

- CSRF protection for all forms
- Secure session cookies
- Proper error handling
- Logging for monitoring and debugging
- Environment-based configuration
