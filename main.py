from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from langchain.agents import create_csv_agent  # Use the correct import
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_file(
    request: Request, 
    file: UploadFile = File(...), 
    question: str = Form(...)
):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Use environment variable

    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY is not set"}

    try:
        # Create the agent using the uploaded CSV file
        agent = create_csv_agent(OpenAI(temperature=0), file.file, verbose=True)

        # Run the agent with the user's question
        answer = agent.run(question)
    except Exception as e:
        return {"error": str(e)}

    return templates.TemplateResponse("index.html", {"request": request, "answer": answer})

# HTML code embedded as a string
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ask your CSV</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css">
</head>
<body>
    <div class="ui container">
        <h2>Ask your CSV 📈</h2>
        <form action="/upload/" method="post" enctype="multipart/form-data" class="ui form">
            <div class="field">
                <label for="file">Upload CSV File</label>
                <input type="file" name="file" accept=".csv" required>
            </div>
            <div class="field">
                <label for="question">Ask a question about your CSV</label>
                <input type="text" name="question" required>
            </div>
            <button type="submit" class="ui button">Submit</button>
        </form>
        {% if answer %}
        <div class="ui message">
            <h3>Answer:</h3>
            <p>{{ answer }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Write HTML to a file (only if it doesn't exist)
if not os.path.exists("templates"):
    os.makedirs("templates")

with open("templates/index.html", "w") as f:
    f.write(html_content)

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
