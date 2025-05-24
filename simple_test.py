from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Test</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px;
                line-height: 1.6;
            }
            h1 { color: #4a6ee0; }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Perito IA - Simple Test Page</h1>
            <p>If you can see this page, the Flask application is working correctly.</p>
            <p>This is a static HTML response without using templates.</p>
            <hr>
            <h2>UI Enhancements Summary</h2>
            <ul>
                <li>Modern dashboard design with improved metrics display</li>
                <li>Enhanced laudo list with better visual hierarchy</li>
                <li>Improved laudo view with interactive elements</li>
                <li>Comprehensive design system with consistent styling</li>
            </ul>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5002)
