from flask import Flask, render_template_string
import requests
import redis
import os

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/')
def cat_gif():
    """
    Serve a random cat GIF, either from the cache (Redis) or via an API call.
    
    This function attempts to retrieve a cached GIF URL from Redis. If the cache is empty,
    it fetches a new random cat GIF from the Cataas API. The fetched or cached GIF URL is
    then stored in Redis for future use. The function also maintains and updates Redis-based
    statistics for cache hits and API calls.
    
    Returns:
        str: HTML string containing the embedded GIF and Redis statistics.

    Redis keys used:
    - 'recent_gifs': A list of recently cached GIF URLs.
    - 'cache_hits': A counter for the number of times a GIF was served from cache.
    - 'api_calls': A counter for the number of times the Cataas API was called.
    """
    
    # Try to get a cached GIF URL from Redis
    cached_gif = redis_client.rpop('recent_gifs')
    if cached_gif:
        gif_url = cached_gif.decode('utf-8')  # Decode the cached URL from bytes to a string
        gif_source = "Cache"  # Mark the source as cache
    else:
        # Fetch a new random cat GIF from the Cataas API
        response = requests.get('https://cataas.com/cat/gif')
        gif_url = response.url  # Get the URL of the fetched GIF
        gif_source = "API"  # Mark the source as API

    # Store the GIF URL in Redis
    redis_client.lpush('recent_gifs', gif_url)
    redis_client.ltrim('recent_gifs', 0, 9)  # Keep only the 10 most recent GIFs in the cache

    # Get Redis statistics
    cache_hits = redis_client.get('cache_hits')
    cache_hits = int(cache_hits) if cache_hits else 0
    api_calls = redis_client.get('api_calls')
    api_calls = int(api_calls) if api_calls else 0

    # Update statistics based on the source of the GIF
    if gif_source == "Cache":
        redis_client.incr('cache_hits')  # Increment cache hits
        cache_hits += 1
    else:
        redis_client.incr('api_calls')  # Increment API calls
        api_calls += 1

    # Get the number of cached GIFs in Redis
    cached_gifs_count = redis_client.llen('recent_gifs')

    # HTML template with embedded GIF and statistics
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
            .stats { margin-top: 20px; background-color: #fff; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Random Cat GIF</h1>
            <img src="{{ gif_url }}" alt="Random Cat GIF">
            <p>Reload the page for a new cat GIF!</p>
            <div class="stats">
                <h2>Redis Statistics</h2>
                <p>Source: {{ gif_source }}</p>
                <p>Cache Hits: {{ cache_hits }}</p>
                <p>API Calls: {{ api_calls }}</p>
                <p>Cached GIFs: {{ cached_gifs_count }}/10</p>
            </div>
        </div>
    </body>
    </html>
    '''
    # Render the HTML template with the GIF URL and Redis statistics
    return render_template_string(html, gif_url=gif_url, gif_source=gif_source,
                                  cache_hits=cache_hits, api_calls=api_calls,
                                  cached_gifs_count=cached_gifs_count)


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
