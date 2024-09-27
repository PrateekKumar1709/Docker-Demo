from flask import Flask, render_template_string
import requests

app = Flask(__name__)

@app.route('/')
def cat_gif():
    """
    Serve a random cat GIF from the Cataas API.

    This function makes a GET request to the Cataas API to fetch a random cat GIF URL.
    The GIF URL is then embedded in an HTML page, which is rendered and returned to the user.

    Returns:
        str: HTML string containing the embedded GIF.

    API:
        - The Cataas (Cat as a Service) API is used to retrieve a random cat GIF.
    """
    
    # Fetch a random cat GIF from the Cataas API
    response = requests.get('https://cataas.com/cat/gif')
    gif_url = response.url  # Get the URL of the fetched GIF

    # HTML template with embedded GIF
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Random Cat GIF</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f0f0f0; }
            h1 { color: #333; }
            img { max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Random Cat GIF</h1>
            <img src="{{ gif_url }}" alt="Random Cat GIF">
            <p>Reload the page for a new cat GIF!</p>
        </div>
    </body>
    </html>
    '''
    
    # Render the HTML template with the fetched GIF URL
    return render_template_string(html, gif_url=gif_url)

if __name__ == '__main__':
    """
    Main entry point of the application.

    This runs the Flask web server, which listens on all available network interfaces
    (host='0.0.0.0') on port 5000. It allows external requests to access the cat GIF service.
    
    Example:
        You can access the service by visiting http://localhost:5000 in your browser
        if running locally, or the appropriate IP/port if running in a container.
    """
    app.run(host='0.0.0.0', port=5000)
