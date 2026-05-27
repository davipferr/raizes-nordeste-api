import enum

class TipoTransacaoFidelidade(str, enum.Enum):
    GANHO = "GANHO"
    RESGATADO = "RESGATADO"
