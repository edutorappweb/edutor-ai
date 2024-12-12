from fastapi import FastAPI, HTTPException, File, UploadFile, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Services
from services.gemini import handle_file_upload_to_gemini
from services.helper import file_prepare_chat_history

# Import from Controller
from controller.search_category import category_search_order
from controller.quiz_explainer import QuizExplainer
from controller.talk_with_pdf import generate_response
from controller.text_to_speech import synthesize_speech
from controller.podcast import get_podcast

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

class ExplainerRequest(BaseModel):
    quiz: str
    explanationLength: str
    toneId: int
    history: str = None
    quizsDetails: str = None

class TalkWithPdfRequest(BaseModel):
    prompt: int
    fileDetails: str
    history: list

class SynthesizeRequest(BaseModel):
    text_block: str
    language_code: str

class GetPodcastRequest(BaseModel):
    prompt: str
    fileDetails: str
    history: list

@app.get("/")
async def home():
    return "Hello, From Jaydipsinh Solanki! 😊"

@app.post("/search-category")
async def search_category(request: SearchRequest):
    try:
        result = category_search_order(request.query)
        return {"category": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/quiz-explainer")
async def quiz_explainer(request: ExplainerRequest):
    try:
        result = QuizExplainer(
            request.quiz,
            request.explanationLength,
            request.toneId,
            request.history,
            request.quizsDetails
        )
        return result
    except HTTPException as e:
        raise e

@app.post("/talk-with-file")
async def talk_with_pdf(request: TalkWithPdfRequest):
    try:
        response = generate_response(
            request.prompt,
            request.fileDetails,
            request.history
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/text-to-speech")
async def synthesize_speech_endpoint(request: SynthesizeRequest):
    try:
        audio_stream = synthesize_speech(
            request.text_block,
            request.language_code    
        )

        return StreamingResponse(audio_stream, media_type="audio/mpeg", headers={"Content-Disposition": "attachment; filename=output.mp3"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-file")
async def upload_to_gemini_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to handle file upload and pass to Gemini.
    """
    try:
        file_url = handle_file_upload_to_gemini(file, mime_type="image/jpeg")
        chat_history = file_prepare_chat_history(file_url)
        history_single_line = str(chat_history).replace("\n", " ").replace("  ", " ")
        return {"history":history_single_line}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-podcast")
async def generate_podcast(request: GetPodcastRequest):
    try:
        podcast_data = get_podcast(
            prompt=request.prompt,
            history=request.history,
            file_details=request.fileDetails
        )
        
        if podcast_data and podcast_data.get("audio"):
            headers = {
                "Content-Disposition": "attachment; filename=generated_podcast.mp3"
            }
            return Response(
                content=podcast_data["audio"],
                media_type="audio/mpeg",
                headers=headers
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Podcast generation failed. No audio content returned."
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
