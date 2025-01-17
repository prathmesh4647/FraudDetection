from flask import Flask, request, render_template, redirect, flash
import pandas as pd
import os

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = 'your_secret_key'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_file(file):
    import pandas as pd
    import os

    # Create a temporary directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Save the uploaded file to a temporary location
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    # Read the file into a DataFrame
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading the file: {e}")

    # Log original column names with debug info
    print("Original Columns with Debug Info:", [(col, repr(col)) for col in df.columns])

    # Standardize column names
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(" ", "").str.replace("_", "")
    )
    print("Cleaned Columns:", df.columns.tolist())

    # Define required columns
    required_columns = [
        "type", "amount", "nameorig", "oldbalanceorg", "newbalanceorg",
        "namedest", "oldbalancedest", "newbalancedest"
    ]

    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    print("Missing Columns (Post-Clean):", missing_columns)

    # If missing columns, raise an error
    if missing_columns:
        raise ValueError(f"The uploaded file is missing the required columns: {', '.join(missing_columns)}")

    # Add a mock 'isfraudprediction' column for testing (replace with actual logic)
    df['isfraudprediction'] = df['amount'].apply(lambda x: 1 if x > 100 else 0)

    # Convert DataFrame to a list of dictionaries for rendering in the template
    suspicious_data = df.to_dict(orient='records')
    return suspicious_data



@app.route('/')
def index():
    return render_template('index.html')  # Upload form

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Process the file and generate suspicious data
        suspicious_data = process_file(file)  # Process file to get suspicious data
        print("Suspicious Data:", suspicious_data)  # Debugging line
        return render_template('result.html', filename=file.filename, suspicious=suspicious_data)
    
    flash('Invalid file type. Please upload a CSV file.')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
