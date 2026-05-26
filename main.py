from src.api.configuracao import criar_app

app = criar_app()

@app.get("/", tags=["Saúde"])
def verificar_saude():
    return {"status": "online", "servico": "API Raízes do Nordeste", "versao": "1.0.0"}
