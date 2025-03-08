# Pastebin Web Application

A simple and elegant pastebin web application built with Flask and SQLite.

## Features

- Create text pastes with customizable expiration times
- View pastes in both raw text and formatted HTML modes
- Line numbering for easy reference
- Delete pastes using a secret token
- Recent pastes displayed on the home page
- Responsive design for mobile and desktop

## Installation

1. Clone the repository or download the source code
2. Create a virtual environment (recommended)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python app.py
```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

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
│   └── view.html          # View paste
└── requirements.txt       # Python dependencies
```

## Database

The application uses SQLite for data storage. The database file `pastebin.db` will be created automatically in the application root directory when the application is first run.

## Cleanup

Expired pastes are automatically cleaned up when the application starts. You can also manually clean up expired pastes using the Flask CLI:

```bash
flask cleanup
```
