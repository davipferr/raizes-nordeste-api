from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual, requer_perfis
from src.api.schemas.schema_produto import RespostaProdutoCardapio
from src.api.respostas_erro import (
    NAO_AUTENTICADO, PERMISSAO_NEGADA, UNIDADE_NAO_ENCONTRADA,
    UNIDADE_OU_PRODUTO_NAO_ENCONTRADO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.produtos.gerenciar_produtos import (
    listar_cardapio_unidade, adicionar_produto_cardapio, remover_produto_cardapio
)
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/cardapio", tags=["Cardápio"])

@roteador.get("/{unidade_id}", response_model=list[RespostaProdutoCardapio], summary="Cardápio da unidade",
              responses={**NAO_AUTENTICADO, **UNIDADE_NAO_ENCONTRADA, **ERRO_INTERNO})
def listar_cardapio(
    unidade_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    return listar_cardapio_unidade(sessao, unidade_id)

@roteador.post("/{unidade_id}/produtos/{produto_id}", status_code=204, summary="Adicionar produto ao cardápio",
               responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **UNIDADE_OU_PRODUTO_NAO_ENCONTRADO, **ERRO_INTERNO})
def adicionar(
    unidade_id: int,
    produto_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    adicionar_produto_cardapio(sessao, unidade_id, produto_id)

@roteador.delete("/{unidade_id}/produtos/{produto_id}", status_code=204, summary="Remover produto do cardápio",
                 responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **ERRO_INTERNO})
def remover(
    unidade_id: int,
    produto_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    remover_produto_cardapio(sessao, unidade_id, produto_id)
