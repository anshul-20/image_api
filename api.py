from flask import Flask, jsonify
from datetime import datetime
import mysql.connector  
import sys  
import os   


db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

app = Flask(__name__)

def get_images_from_db():
    """
    Connects to the MySQL database and fetches the list of active image URLs.
    Returns a list of URLs, or None if an error occurs.
    """
    your_image_list = []

    if not all([db_config['user'], db_config['password'], db_config['host'], db_config['database']]):
         print("Error: Missing database environment variables.", file=sys.stderr)
         return None
         
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute query to get all active images
        query = "SELECT url FROM app_images WHERE is_active = TRUE"
        cursor.execute(query)

        # Fetch all results
        results = cursor.fetchall()

        # Flatten the list of tuples into a simple list of strings
        your_image_list = [item[0] for item in results]

    except mysql.connector.Error as err:
        print(f"Error connecting to or querying MySQL: {err}", file=sys.stderr)
        return None  
    finally:
     
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    return your_image_list


@app.route('/api/app-info', methods=['GET'])
def get_app_info():
    """
    This is the main API endpoint.
    It returns a JSON object with the image URL and download link.
    """

    your_image_list = get_images_from_db()

    current_week_number = datetime.now().isocalendar()[1]

    if not your_image_list:
        selected_image_url = "https://placehold.co/800x600/FF0000/FFFFFF?text=Database+Error+or+No+Images"
    else:
        number_of_images = len(your_image_list)
        
        image_index = (current_week_number - 1) % number_of_images
        selected_image_url = your_image_list[image_index]


    download_link = os.environ.get('DOWNLOAD_LINK', "https.example.com/downloads/my-awesome-app-v1.0.apk")

    app_data = {
        "imageUrl": selected_image_url,
        "downloadLink": download_link
    }

    return jsonify(app_data)

if __name__ == '__main__':
    print("Starting Flask server for LOCAL testing...")
    print("NOTE: Make sure you have set your environment variables (DB_USER, etc.) in this terminal.")
    app.run(debug=True, host='0.0.0.0', port=5000)