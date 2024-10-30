from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os
from fastapi import Request

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ask your CSV</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h1 {
                color: #333;
            }
            form {
                margin-bottom: 20px;
            }
            input[type="text"], input[type="file"], input[type="submit"] {
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Ask your CSV 📈</h1>
        <form action="/upload/" method="post" enctype="multipart/form-data">
            <label for="file">Upload a CSV file:</label>
            <input type="file" name="file" accept=".csv" required><br><br>

            <label for="question">Ask a question about your CSV:</label>
            <input type="text" name="question" required><br><br>

            <input type="submit" value="Submit">
        </form>
        {% if answer %}
            <h2>Answer:</h2>
            <p>{{ answer }}</p>
        {% endif %}
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/upload/")
async def upload_file(
    request: Request, 
    file: UploadFile = File(...), 
    question: str = Form(...)
):
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        return HTMLResponse(content="OPENAI_API_KEY is not set")

    # Create the agent using the uploaded CSV file
    agent = create_csv_agent(OpenAI(temperature=0), file.file, verbose=True)

    # Run the agent with the user's question
    answer = agent.run(question)

    # Render the HTML response with the answer
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ask your CSV</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{
                color: #333;
            }}
            form {{
                margin-bottom: 20px;
            }}
            input[type="text"], input[type="file"], input[type="submit"] {{
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>Ask your CSV 📈</h1>
        <form action="/upload/" method="post" enctype="multipart/form-data">
            <label for="file">Upload a CSV file:</label>
            <input type="file" name="file" accept=".csv" required><br><br>

            <label for="question">Ask a question about your CSV:</label>
            <input type="text" name="question" required><br><br>

            <input type="submit" value="Submit">
        </form>
        <h2>Answer:</h2>
        <p>{answer}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
