import enum

class PerfilUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    COZINHA = "COZINHA"
    ATENDENTE = "ATENDENTE"
    CLIENTE = "CLIENTE"
