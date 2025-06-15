# arquivo: aigrox_api.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import openai
import uvicorn
import logging
import os
import re
from typing import Optional
from datetime import datetime

# Configuração avançada de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("aigrox_api.log"),
        logging.StreamHandler()
    ]
)
46
# Configurações de ambiente com fallback seguro
OPENAI_API_KEY =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
# Inicialização do app FastAPI com metadados completos
app = FastAPI(
    title="AIGROX Quantum Architect API",
    version="1.0.0",
    description="API de análise inteligente de código com capacidades quânticas",
    contact={
        "name": "Suporte AIGROX",
        "email": "suporte@aigrox.com"
    },
    license_info={
        "name": "MIT",
    },
)

# Configuração de CORS mais segura (ajuste para produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrinja em produção
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-AIGROX-Version"]
)

# Modelo de entrada com validação avançada
class CodeRequest(BaseModel):
    content: str = Field(..., min_length=5, description="Código fonte para análise")
    linguagem: str = Field("python", description="Linguagem de programação do código")
    contexto: Optional[str] = Field(None, description="Contexto adicional para análise")
    nivel_analise: str = Field("padrao", description="Nível de análise: 'rapido', 'padrao' ou 'profundo'")

@app.post("/analisar", summary="Análise Inteligente de Código com AIGROX", response_description="Resultado da análise")
async def analisar_codigo(req: CodeRequest, request: Request):
    """
    Realiza análise inteligente de código utilizando o AIGROX Architect IA.
    
    Parâmetros:
    - código: Texto contendo o código fonte
    - linguagem: Linguagem de programação (default: python)
    - contexto: Informações adicionais sobre o código (opcional)
    
    Retorna:
    - análise estruturada com insights quânticos
    """
    try:
        # Validação avançada
        codigo = req.content.strip()
        if len(codigo) < 5:
            raise HTTPException(status_code=400, detail="Código muito curto para análise")
            
        # Segurança reforçada
        blacklist = [
            "os.system", "eval", "exec", "subprocess", 
            "rm -rf", "open(", "wget", "curl", "import os",
            "__import__", "lambda", "pickle"
        ]
        padroes_perigosos = re.compile(r"(\bimport\s+os\b|system\s*\()", re.IGNORECASE)
        
        if any(term.lower() in codigo.lower() for term in blacklist) or padroes_perigosos.search(codigo):
            logging.warning(f"Tentativa de código perigoso: {request.client.host}")
            raise HTTPException(status_code=403, detail="Código contém instruções potencialmente perigosas")

        # Prompt dinâmico para a IA AIGROX
        prompt_ia = f"""
        [AIGROX QUANTUM ARCHITECT ANALYSIS REQUEST]
        Data: {datetime.now().isoformat()}
        Language: {req.linguagem}
        Context: {req.contexto or 'Nenhum contexto adicional fornecido'}
        Analysis Level: {req.nivel_analise}
        
        [CODE TO ANALYZE]
        {codigo}
        
        [ANALYSIS INSTRUCTIONS]
        1. Realize análise estática do código
        2. Identifique padrões quânticos aplicáveis
        3. Sugira otimizações específicas
        4. Avalie complexidade algorítmica
        5. Verifique vulnerabilidades de segurança
        6. Proponha arquitetura alternativa se aplicável
        
        [RESPONSE FORMAT]
        - Resumo executivo
        - Pontos fortes
        - Oportunidades de melhoria
        - Risco quântico (1-5)
        - Recomendações específicas
        """

        # Chamada à API OpenAI com tratamento robusto
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é o AIGROX Quantum Architect, especialista em análise de código com visão quântica."},
                    {"role": "user", "content": prompt_ia}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analise = response.choices[0].message.content
            
            # Processamento adicional da resposta
            analise_estruturada = {
                "timestamp": datetime.now().isoformat(),
                "versao_api": app.version,
                "analise": analise,
                "metricas": {
                    "complexidade": "alta|media|baixa",  # Placeholder para métricas reais
                    "quantum_ready": bool(re.search(r"quantum|quântico", analise, re.IGNORECASE))
                }
            }
            
            return JSONResponse(content=analise_estruturada)
            
        except openai.error.OpenAIError as e:
            logging.error(f"Erro na API OpenAI: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Erro no serviço de IA: {str(e)}")

    except Exception as e:
        logging.exception("Erro inesperado na análise")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Health Check endpoint
@app.get("/health", tags=["Monitoramento"])
async def health_check():
    return {
        "status": "online",
        "versao": app.version,
        "timestamp": datetime.now().isoformat()
    }

# Documentação Swagger personalizada
app.openapi_tags = [{
    "name": "Análise",
    "description": "Endpoints para análise quântica de código"
}]

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        ssl_keyfile="key.pem",  # Configure para produção
        ssl_certfile="cert.pem"  # Configure para produção
    )