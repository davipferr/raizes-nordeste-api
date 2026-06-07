import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual, requer_perfis
from src.api.schemas.schema_produto import RequisicaoCriarProduto, RequisicaoAtualizarProduto, RespostaProduto
from src.api.schemas.schema_paginacao import RespostaPaginada
from src.api.respostas_erro import (
    NAO_AUTENTICADO, PERMISSAO_NEGADA, PRODUTO_NAO_ENCONTRADO, VALIDACAO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.produtos.gerenciar_produtos import (
    listar_produtos, obter_produto, criar_produto, atualizar_produto
)
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/produtos", tags=["Produtos"])

@roteador.get("", response_model=RespostaPaginada[RespostaProduto], summary="Listar produtos",
              description=(
                  "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
                  "**Perfis permitidos:** Todos (ADMIN, GERENTE, COZINHA, ATENDENTE, CLIENTE).\n\n"
                  "Suporta filtro por `categoria` e paginação via `pagina` e `limite`."
              ),
              responses={**NAO_AUTENTICADO, **ERRO_INTERNO})
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    categoria: str | None = Query(None),
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    itens, total = listar_produtos(sessao, pagina, limite, categoria)
    return RespostaPaginada(itens=itens, total=total, pagina=pagina, limite=limite, paginas=math.ceil(total / limite) or 1)

@roteador.get("/{produto_id}", response_model=RespostaProduto, summary="Obter produto por ID",
              description=(
                  "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
                  "**Perfis permitidos:** Todos (ADMIN, GERENTE, COZINHA, ATENDENTE, CLIENTE)."
              ),
              responses={**NAO_AUTENTICADO, **PRODUTO_NAO_ENCONTRADO, **ERRO_INTERNO})
def obter(
    produto_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    return obter_produto(sessao, produto_id)

@roteador.post("", response_model=RespostaProduto, status_code=201, summary="Criar produto",
               description=(
                   "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
                   "**Perfis permitidos:** `ADMIN`, `GERENTE`."
               ),
               responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **VALIDACAO, **ERRO_INTERNO})
def criar(
    dados: RequisicaoCriarProduto,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    return criar_produto(sessao, dados.nome, dados.descricao, dados.preco, dados.categoria)

@roteador.put("/{produto_id}", response_model=RespostaProduto, summary="Atualizar produto",
              description=(
                  "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
                  "**Perfis permitidos:** `ADMIN`, `GERENTE`."
              ),
              responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **PRODUTO_NAO_ENCONTRADO, **VALIDACAO, **ERRO_INTERNO})
def atualizar(
    produto_id: int,
    dados: RequisicaoAtualizarProduto,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    return atualizar_produto(sessao, produto_id, dados.model_dump(exclude_none=True))

@roteador.delete("/{produto_id}", status_code=204, summary="Desativar produto",
                 description=(
                     "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
                     "**Perfis permitidos:** `ADMIN`.\n\n"
                     "Realiza desativação lógica (soft delete): o produto não é excluído do banco, apenas marcado como inativo."
                 ),
                 responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **PRODUTO_NAO_ENCONTRADO, **ERRO_INTERNO})
def desativar(
    produto_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN)),
):
    atualizar_produto(sessao, produto_id, {"ativo": False})
