import logging
import time
from functools import wraps

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("BPO_BasePlatform")

def retry_external_platform(max_retries=3, delay=2):
    # Manejo de errores y reintentos ante fallas en plataformas externas.
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Falla al conectar con plataforma externa (Intento {attempts}/{max_retries}): {str(e)}")
                    if attempts == max_retries:
                        logger.error("Error crítico: La plataforma externa no respondió tras agotar los reintentos.")
                        raise Exception("PLATFORM_UNAVAILABLE")
                    time.sleep(delay * attempts)
        return wrapper
    return decorator

def simular_conexion_plataforma_cliente(compania: str, solicitud_id: str) -> str:
    # Simula la creación del caso en la plataforma externa retornando un ID ficticio.
    id_ficticio = f"EXT-{compania[:3].upper()}-{abs(hash(solicitud_id)) % 10000000}"
    logger.info(f"Caso creado exitosamente en plataforma externa para {compania} con ID: {id_ficticio}")
    return id_ficticio
