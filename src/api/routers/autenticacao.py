from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual
from src.api.schemas.schema_autenticacao import (
    RequisicaoLogin, RequisicaoRegistro, RespostaLogin, RespostaUsuarioPublico
)
from src.api.respostas_erro import (
    CREDENCIAIS_INVALIDAS, EMAIL_JA_CADASTRADO, NAO_AUTENTICADO, VALIDACAO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.autenticacao.autenticar_usuario import autenticar_usuario
from src.aplicacao.casos_uso.autenticacao.registrar_usuario import registrar_usuario
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/auth", tags=["Autenticação"])

@roteador.post("/login", response_model=RespostaLogin, summary="Autenticar usuário",
               description=(
                   "**Autenticação:** Pública — não requer token JWT.\n\n"
                   "Retorna um token JWT que deve ser enviado nas requisições protegidas "
                   "no header `Authorization: Bearer <token>`."
               ),
               responses={**CREDENCIAIS_INVALIDAS, **VALIDACAO, **ERRO_INTERNO})
def login(requisicao: RequisicaoLogin, request: Request, sessao: Session = Depends(obter_db)):
    resultado = autenticar_usuario(sessao, requisicao.email, requisicao.senha)
    usuario: ModeloUsuario = resultado["usuario"]
    registrar_acao(
        sessao, "LOGIN_USUARIO", "usuarios", str(usuario.id),
        usuario_id=usuario.id, ip_origem=request.client.host if request.client else None
    )
    sessao.commit()
    return resultado

@roteador.post("/registrar", response_model=RespostaUsuarioPublico, status_code=201,
               summary="Registrar novo usuário",
               description=(
                   "**Autenticação:** Pública — não requer token JWT.\n\n"
                   "Cria uma nova conta de usuário. O perfil padrão é `CLIENTE`; "
                   "perfis administrativos (`ADMIN`, `GERENTE`, `COZINHA`, `ATENDENTE`) "
                   "podem ser informados no campo `perfil`."
               ),
               responses={**EMAIL_JA_CADASTRADO, **VALIDACAO, **ERRO_INTERNO})
def registrar(requisicao: RequisicaoRegistro, sessao: Session = Depends(obter_db)):
    usuario = registrar_usuario(
        sessao,
        nome=requisicao.nome,
        email=requisicao.email,
        senha=requisicao.senha,
        perfil=requisicao.perfil,
        consentimento_lgpd=requisicao.consentimento_lgpd,
    )
    return usuario

@roteador.get("/me", response_model=RespostaUsuarioPublico, summary="Dados do usuário autenticado",
              description=(
                  "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
                  "**Perfis permitidos:** Todos (ADMIN, GERENTE, COZINHA, ATENDENTE, CLIENTE).\n\n"
                  "Retorna os dados públicos do usuário dono do token."
              ),
              responses={**NAO_AUTENTICADO, **ERRO_INTERNO})
def perfil_atual(usuario: ModeloUsuario = Depends(obter_usuario_atual)):
    return usuario
