import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual, requer_perfis
from src.api.schemas.schema_produto import RequisicaoCriarProduto, RequisicaoAtualizarProduto, RespostaProduto
from src.api.schemas.schema_paginacao import RespostaPaginada
from src.aplicacao.casos_uso.produtos.gerenciar_produtos import (
    listar_produtos, obter_produto, criar_produto, atualizar_produto
)
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/produtos", tags=["Produtos"])

@roteador.get("", response_model=RespostaPaginada[RespostaProduto], summary="Listar produtos")
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    categoria: str | None = Query(None),
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    itens, total = listar_produtos(sessao, pagina, limite, categoria)
    return RespostaPaginada(itens=itens, total=total, pagina=pagina, limite=limite, paginas=math.ceil(total / limite) or 1)

@roteador.get("/{produto_id}", response_model=RespostaProduto, summary="Obter produto por ID")
def obter(
    produto_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    return obter_produto(sessao, produto_id)

@roteador.post("", response_model=RespostaProduto, status_code=201, summary="Criar produto")
def criar(
    dados: RequisicaoCriarProduto,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    return criar_produto(sessao, dados.nome, dados.descricao, dados.preco, dados.categoria)

@roteador.put("/{produto_id}", response_model=RespostaProduto, summary="Atualizar produto")
def atualizar(
    produto_id: int,
    dados: RequisicaoAtualizarProduto,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    return atualizar_produto(sessao, produto_id, dados.model_dump(exclude_none=True))

@roteador.delete("/{produto_id}", status_code=204, summary="Desativar produto")
def desativar(
    produto_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN)),
):
    atualizar_produto(sessao, produto_id, {"ativo": False})
