import json
import os
from datetime import datetime
from services.ia_clasificador import clasificar_con_ia, consultar_servicio_externo_mensajeria
from services.duplication_case import verificar_caso_duplicado
from utils.base_platform import retry_external_platform, simular_conexion_plataforma_cliente, logger

def cargar_configuracion():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_configuracion = os.path.normpath(os.path.join(directorio_actual, "../rules/companias_config.json"))
    with open(ruta_configuracion, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

@retry_external_platform(max_retries=3)
def crear_caso_externo_seguro(compania: str, solicitud_id: str) -> str:
    return simular_conexion_plataforma_cliente(compania, solicitud_id)

def procesar_solicitud_bpo(data) -> dict:
    parametros_empresa = cargar_configuracion()
    
    # Validación de empresa no parametrizada
    if data.compania not in parametros_empresa or not parametros_empresa[data.compania].get("activo", False):
        logger.error(f"Intento de procesamiento para compañía no parametrizada: {data.compania}")
        return {
            "compania": data.compania,
            "solicitud_id": data.solicitud_id,
            "solicitud_fecha": datetime.now().strftime("%Y-%m-%d"),
            "proximo_paso": "CIERRE_POR_EMPRESA_NO_PARAMETRIZADA",
            "justificacion": f"La compañía '{data.compania}' no se encuentra registrada o activa en el sistema.",
            "estado": "cerrado"
        }

    conf_compania = parametros_empresa[data.compania]

    # Verificación de casos duplicados
    if verificar_caso_duplicado(data.compania, data.solicitud_descripcion):
        return {
            "compania": data.compania,
            "solicitud_id": data.solicitud_id,
            "solicitud_fecha": datetime.now().strftime("%Y-%m-%d"),
            "proximo_paso": "CIERRE_POR_DUPLICIDAD",
            "justificacion": "Se detectó una solicitud idéntica ya registrada previamente.",
            "estado": "cerrado"
        }

    # Categorías permitidas del archivo de configuración
    categorias_permitidas = conf_compania.get("categorias_permitidas", [])

    # Verificar si la información suministrada es suficiente o no.
    resultado_ia = clasificar_con_ia(data.solicitud_descripcion, data.compania, categorias_permitidas)
    
    if resultado_ia.get("informacion_insuficiente", False):
        return {
            "compania": data.compania,
            "solicitud_id": data.solicitud_id,
            "solicitud_fecha": datetime.now().strftime("%Y-%m-%d"),
            "solicitud_tipo": resultado_ia.get("solicitud_tipo", "Desconocido"),
            "proximo_paso": "CIERRE_POR_INFORMACION_INSUFICIENTE",
            "justificacion": "Información incompleta o faltante.",
            "estado": "cerrado"
        }

    # Datos adicionales respecto a la solicitud y el cliente
    tipo_solicitud = resultado_ia.get("solicitud_tipo")
    justificacion = resultado_ia.get("justificacion")
    tipo_doc_cliente = resultado_ia.get("tipo_doc_cliente", "CC")
    num_doc_cliente = resultado_ia.get("num_doc_cliente", "No especificado")

    # Determinar la prioridad del caso, evaluando si se delega a un servicio externo 
    # o si se resuelve localmente mediante las listas parametrizadas en el JSON.
    if conf_compania.get("utiliza_servicio_externo_prioridad", False):
        prioridad = consultar_servicio_externo_mensajeria(
            tipo_doc_cliente, 
            num_doc_cliente, 
            tipo_solicitud
        )
        justificacion += f" [Prioridad calculada vía microservicio externo de {data.compania}]"
    else:
        # Si usa la regla por listas en el JSON
        prioridades_dict = conf_compania.get("prioridades", {})
        
        # Valor por defecto de seguridad
        prioridad = "Media" 
        
        # Buscar en qué lista se encuentra el tipo de solicitud
        for nivel, lista_categorias in prioridades_dict.items():
            if tipo_solicitud in lista_categorias:
                prioridad = nivel
                break

    # Evaluar si la categoría clasificada requiere derivación externa 
    # según las políticas configuradas en el archivo JSON de la compañía.
    delegaciones_externas = conf_compania.get("delegacion_externa", [])
    
    if tipo_solicitud in delegaciones_externas:
        proximo_paso = "GESTIÓN EXTERNA"
        id_externo = crear_caso_externo_seguro(data.compania, data.solicitud_id)
        estado = "pendiente"
    else:
        proximo_paso = "RESPUESTA DIRECTA"
        id_externo = None
        estado = "resuelto"

    return {
        "compania": data.compania,
        "solicitud_id": data.solicitud_id,
        "solicitud_fecha": datetime.now().strftime("%Y-%m-%d"),
        "solicitud_tipo": tipo_solicitud,
        "solicitud_prioridad": prioridad,
        "solicitud_id_cliente": tipo_doc_cliente,
        "solicitud_tipo_id_cliente": num_doc_cliente,
        "solicitud_id_plataforma_externa": id_externo,
        "proximo_paso": proximo_paso,
        "justificacion": justificacion,
        "estado": estado
    }