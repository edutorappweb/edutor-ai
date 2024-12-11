# EdutorAI - Shaping the Future of Education

EdutorAI is an innovative educational platform leveraging advanced AI to enhance the learning experience. - ***Making Content Truly Intelligent.***

## Basic Requirements

-   Python 3.12+
-   API keys for:
    -   Gemini
    -   Groq
    -   ElevenLabs (for podcast generation)
    -   Google Cloud Text-to-Speech API enabled

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/chiragjoshi12/NewEdutorAI.git
    cd NewEdutorAI
    ```

2. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**

    -   Create a `.env` file in the root directory of the project.
    -   Add the following environment variables, replacing the placeholders with your actual API keys:

    ```
    GEMINI_API_KEY=<gemini_api_key>
    GROQ_API_KEY=<groq_api_key>
    ELEVENLABS_API_KEY=<elevenlabs_api_key>
    ```

    -   Add your Google Cloud credentials in `controller/keys.json`. You can download this from your Google Cloud project. Make sure you have the Text-to-Speech API enabled in your project.

## Running the Application

1. **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

    The `--reload` flag enables hot reloading, so the server will automatically restart when you make changes to the code.

2. **Access the API:**

    The API will be accessible at `http://localhost:8000`.

## Deployment Requirements

1. Installation Command:
    ```bash
    pip install -r requirements.txt
    ```

2. Production Deployment
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8000
    ```