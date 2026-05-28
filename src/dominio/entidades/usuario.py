from dataclasses import dataclass
from datetime import datetime
from src.dominio.enums import PerfilUsuario

@dataclass
class EntidadeUsuario:
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    consentimento_lgpd: bool
    criado_em: datetime
    data_consentimento: datetime | None = None
