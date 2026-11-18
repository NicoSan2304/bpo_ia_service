import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
cliente = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def consultar_servicio_externo_mensajeria(tipo_doc: str, num_doc: str, tipo_solicitud: str) -> str:
    # Simula el microservicio externo de priorización del cliente 'MENSAJERIA DEL VALLE'.
    # Se consulta con tipo_doc y num_doc en el servicio externo por eso se ingresan las variables a pesar de no usarlas en la lógica actual.
    if tipo_solicitud in ["Entrega fallida", "Demora en ruta"]:
        return "Alta"
    elif tipo_solicitud == "Reclamo general":
        return "Media"
    return "Baja"

def clasificar_con_ia(descripcion: str, compania: str, categorias_permitidas: list) -> dict:
    
    categorias_str = ", ".join([f"'{cat}'" for cat in categorias_permitidas])
    
    prompt = f"""
    Analiza la siguiente solicitud para la empresa {compania}:
    "{descripcion}"

    Realiza lo siguiente:
    1. Valida si cuenta con información mínima (qué pasó, cuándo, qué necesita). Si falta, pon 'informacion_insuficiente': true.
    2. Clasifica la solicitud seleccionando OBLIGATORIAMENTE una de las siguientes categorías permitidas para esta compañía: [{categorias_str}]. No inventes categorías nuevas.
    3. Extrae el tipo de documento del cliente (ej. CC, CE, NIT) y el número de documento si se mencionan en el texto.
    4. Redacta una justificación breve basada en el texto incorporando información de la solicitud.

    Responde estrictamente en formato JSON válido con las llaves exactas:
    "informacion_insuficiente" (bool),
    "solicitud_tipo" (str),
    "tipo_doc_cliente" (str),
    "num_doc_cliente" (str),
    "justificacion" (str)
    """
    try:
        data_modelo = cliente.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(data_modelo.choices[0].message.content)
    except Exception as e:
        print(f"ERROR DETALLADO EN GROQ API: {str(e)}")
        # Categoría de respaldo tomada de las permitidas si llega a fallar la IA
        cat_respaldo = categorias_permitidas[0] if categorias_permitidas else "Incidente técnico"
        return {
            "informacion_insuficiente": False,
            "solicitud_tipo": cat_respaldo,
            "tipo_doc_cliente": None, 
            "num_doc_cliente": None,
            "justificacion": f"Clasificado por regla de respaldo debido a fallo temporal de IA."
        }