import re

def limpiar_json_response(response_text: str) -> str:
    patrones = [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
        r'(\{.*?\})'
    ]
    for pattern in patrones:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            return match.group(1)
    return response_text
