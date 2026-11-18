# BPO Microservicio de Automatización IA

Microservicio transversal desarrollado en **FastAPI** diseñado para automatizar la recepción, validación, clasificación mediante Inteligencia Artificial (Groq) y enrutamiento de solicitudes de atención al cliente para múltiples compañías BPO.

---

## Características Principales

* **Validación de Empresas:** Verifica si la compañía cliente existe y se encuentra activa en la parametrización (`companias_config.json`).
* **Control de Duplicidad:** Genera un *hash* SHA-256 por compañía y descripción para evitar el procesamiento de solicitudes idénticas.
* **Clasificación y Extracción con IA:** Utiliza la API de **Groq** (`openai/gpt-oss-120b`) para:
  * Evaluar si la descripción cuenta con información suficiente.
  * Clasificar la solicitud estrictamente dentro de las categorías permitidas por cada empresa.
  * Extraer el tipo y número de documento del cliente.
  * Generar una justificación contextualizada teniendo en cuenta el comentario proporcionado que viene en texto libre.
  * *Mecanismo de respaldo:* Si la API de IA falla, asigna automáticamente una categoría por defecto configurada para la compañía.
* **Priorización Dinámica:** Soporta reglas de prioridad estáticas (configuradas por listas en JSON) o delegación a microservicios externos (ej. *Mensajería del Valle*).
* **Enrutamiento y Tolerancia a Fallos:** Determina si el caso se resuelve directamente o requiere derivación a una plataforma externa, implementando un decorador de reintentos exponenciales (`@retry_external_platform`).

---

## Estructura del Proyecto

```text
bpo-microservicio-ia/
├── main.py                     # Punto de entrada de la aplicación FastAPI
├── requirements.txt            # Dependencias del proyecto
├── .env                        # Variables de entorno (GROQ_API_KEY)
├── models/
│   └── schemas.py              # Modelos Pydantic de entrada y salida
├── rules/
│   └── companias_config.json   # Parametrización de reglas por compañía
├── services/
│   ├── duplication_case.py     # Lógica de detección de casos duplicados
│   ├── ia_clasificador.py      # Integración con Groq y servicio externo de prioridad
│   └── solicitud.py            # Orquestador principal del flujo BPO
└── utils/
    └── base_platform.py        # Logging, decorador de reintentos y conexión externa
```

---

## Requisitos Previos

* **Python 3.9** o superior.
* Una clave de API válida de **Groq** (`GROQ_API_KEY`).

---

## Instalación y Ejecución Local

Seqguir estos pasos para levantar el entorno en la máquina local:

### 1. Clonar o ubicar el proyecto
Abrir una terminal y situarse en la carpeta raíz del proyecto:
```bash
cd bpo_ia_service
```

### 2. Crear y activar un entorno virtual
Se recomienda aislar las dependencias del proyecto:

* **En Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **En macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
Con el entorno virtual activo, instalar los paquetes requeridos:
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear un archivo llamado `.env` en la raíz del proyecto (junto a `main.py`) y agregar la llave de Groq:
```env
GROQ_API_KEY=tu_clave_api_de_groq_aqui
```

### 5. Iniciar el servidor
Ejecutar la aplicación usando Python o Uvicorn directamente:
```bash
python main.py
```
O alternativamente
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

El servicio estará disponible en: `http://127.0.0.1:8000`

---

## 🧪 Pruebas y Documentación Interactiva

Una vez iniciado el servidor, puedes probar el endpoint directamente desde la interfaz interactiva de **Swagger UI** generada por FastAPI:

**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Ejemplo de Petición (`POST /api/v1/solicitudes/procesar`)

**Compañías parametrizadas actualmente:** `GASES DEL ORINOCO`, `MENSAJERIA DEL VALLE`, `FINANCIERA`.

#### Request Body (JSON):
```json
{
  "compania": "GASES DEL ORINOCO",
  "solicitud_id": "SOL-2026-001",
  "solicitud_descripcion": "Hola, soy Juan Pérez con CC 1020304050. Desde ayer en la noche tenemos un fuerte olor a gas cerca al medidor de mi casa y necesitamos revisión urgente."
}
```

#### Response Body Esperado (JSON):
```json
{
  "compania": "GASES DEL ORINOCO",
  "solicitud_id": "SOL-2026-001",
  "solicitud_fecha": "2026-11-18",
  "solicitud_tipo": "Incidente técnico",
  "solicitud_prioridad": "Alta",
  "solicitud_id_cliente": "CC",
  "solicitud_tipo_id_cliente": "1020304050",
  "solicitud_id_plataforma_externa": "EXT-GAS-4829104",
  "proximo_paso": "GESTIÓN EXTERNA",
  "justificacion": "El cliente reporta un fuerte olor a gas cerca al medidor desde la noche anterior y solicita revisión urgente.",
  "estado": "pendiente"
}
```