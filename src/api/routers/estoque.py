from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import requer_perfis
from src.api.schemas.schema_estoque import RequisicaoMovimentacaoEstoque, RespostaEstoque
from src.api.respostas_erro import (
    NAO_AUTENTICADO, PERMISSAO_NEGADA, UNIDADE_OU_PRODUTO_NAO_ENCONTRADO,
    ESTOQUE_INSUFICIENTE, VALIDACAO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.estoque.entrada_estoque import registrar_entrada
from src.aplicacao.casos_uso.estoque.saida_estoque import registrar_saida, consultar_estoque_unidade
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/estoque", tags=["Estoque"])

@roteador.get("/{unidade_id}", response_model=list[RespostaEstoque], summary="Consultar estoque por unidade",
              responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **ERRO_INTERNO})
def consultar(
    unidade_id: int,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(requer_perfis(
        PerfilUsuario.ADMIN, PerfilUsuario.GERENTE, PerfilUsuario.ATENDENTE
    )),
):
    return consultar_estoque_unidade(sessao, unidade_id)

@roteador.post("/entrada", response_model=RespostaEstoque, status_code=201,
               summary="Registrar entrada de estoque",
               responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **UNIDADE_OU_PRODUTO_NAO_ENCONTRADO, **VALIDACAO, **ERRO_INTERNO})
def entrada(
    dados: RequisicaoMovimentacaoEstoque,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    estoque = registrar_entrada(sessao, dados.unidade_id, dados.produto_id, dados.quantidade, usuario.id, dados.motivo)
    from src.infraestrutura.banco.modelos import ModeloProduto
    produto = sessao.query(ModeloProduto).get(estoque.produto_id)
    return RespostaEstoque(
        produto_id=estoque.produto_id,
        produto_nome=produto.nome,
        unidade_id=estoque.unidade_id,
        quantidade=estoque.quantidade,
        minimo_alerta=estoque.minimo_alerta,
        em_alerta=estoque.quantidade <= estoque.minimo_alerta,
        atualizado_em=estoque.atualizado_em,
    )

@roteador.post("/saida", response_model=RespostaEstoque, status_code=201,
               summary="Registrar saída manual de estoque",
               responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **ESTOQUE_INSUFICIENTE, **VALIDACAO, **ERRO_INTERNO})
def saida(
    dados: RequisicaoMovimentacaoEstoque,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)),
):
    estoque = registrar_saida(sessao, dados.unidade_id, dados.produto_id, dados.quantidade, usuario.id, dados.motivo)
    from src.infraestrutura.banco.modelos import ModeloProduto
    produto = sessao.query(ModeloProduto).get(estoque.produto_id)
    return RespostaEstoque(
        produto_id=estoque.produto_id,
        produto_nome=produto.nome,
        unidade_id=estoque.unidade_id,
        quantidade=estoque.quantidade,
        minimo_alerta=estoque.minimo_alerta,
        em_alerta=estoque.quantidade <= estoque.minimo_alerta,
        atualizado_em=estoque.atualizado_em,
    )
