from fastapi import FastAPI, HTTPException
from models.schemas import SolicitudInput, SolicitudOutput
from services.solicitud import procesar_solicitud_bpo

app = FastAPI(
    title="BPO Microservicio de Automatización IA",
    description="Microservicio transversal para automatización de solicitudes",
    version="1.0.0"
)

@app.post("/api/v1/solicitudes/procesar", response_model=SolicitudOutput)
def procesar_solicitud(input_data: SolicitudInput):
    try:
        resultado = procesar_solicitud_bpo(input_data)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)