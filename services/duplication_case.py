import hashlib

PROCESSED_REQUESTS_CACHE = set()

def verificar_caso_duplicado(compania: str, descripcion: str) -> bool:
    # Valida si la solicitud ya existe para evitar duplicados.
    raw_data = f"{compania}:{descripcion.strip().lower()}"
    case_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
    
    if case_hash in PROCESSED_REQUESTS_CACHE:
        return True
    
    PROCESSED_REQUESTS_CACHE.add(case_hash)
    return False
