import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual, requer_perfis
from src.api.schemas.schema_unidade import RequisicaoCriarUnidade, RequisicaoAtualizarUnidade, RespostaUnidade
from src.api.schemas.schema_paginacao import RespostaPaginada
from src.aplicacao.casos_uso.unidades.gerenciar_unidades import (
    listar_unidades, obter_unidade, criar_unidade, atualizar_unidade
)
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/unidades", tags=["Unidades"])

@roteador.get("", response_model=RespostaPaginada[RespostaUnidade], summary="Listar unidades da rede")
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    itens, total = listar_unidades(sessao, pagina, limite)
    return RespostaPaginada(itens=itens, total=total, pagina=pagina, limite=limite, paginas=math.ceil(total / limite) or 1)

@roteador.get("/{unidade_id}", response_model=RespostaUnidade, summary="Obter unidade por ID")
def obter(
    unidade_id: int,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    return obter_unidade(sessao, unidade_id)

@roteador.post("", response_model=RespostaUnidade, status_code=201, summary="Criar nova unidade")
def criar(
    dados: RequisicaoCriarUnidade,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN)),
):
    return criar_unidade(sessao, dados.nome, dados.endereco, dados.cidade, dados.estado)

@roteador.put("/{unidade_id}", response_model=RespostaUnidade, summary="Atualizar unidade")
def atualizar(
    unidade_id: int,
    dados: RequisicaoAtualizarUnidade,
    sessao: Session = Depends(obter_db),
    _usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    return atualizar_unidade(sessao, unidade_id, dados.model_dump(exclude_none=True))
