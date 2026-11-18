from pydantic import BaseModel, Field
from typing import Optional

class SolicitudInput(BaseModel):
    compania: str = Field(..., description="Nombre de la compañía cliente")
    solicitud_id: str = Field(..., description="Identificador único de la solicitud")
    solicitud_descripcion: str = Field(..., description="Texto libre ingresado por el usuario")

class SolicitudOutput(BaseModel):
    compania: str
    solicitud_id: str
    solicitud_fecha: str
    solicitud_tipo: Optional[str] = None
    solicitud_prioridad: Optional[str] = None
    solicitud_id_cliente: Optional[str] = None
    solicitud_tipo_id_cliente: Optional[str] = None
    solicitud_id_plataforma_externa: Optional[str] = None
    proximo_paso: str
    justificacion: str
    estado: str
