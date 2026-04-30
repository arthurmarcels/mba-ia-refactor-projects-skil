class ValidationError(Exception):
    """Erro de validação convertido pelo middleware em resposta 400."""


CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]
MIN_NOME_LEN = 2
MAX_NOME_LEN = 200
MIN_SENHA_LEN = 6


def validate_produto_payload(data):
    if not data:
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in data:
            raise ValidationError(f"{campo.capitalize()} é obrigatório")

    nome = data.get("nome")
    preco = data.get("preco")
    estoque = data.get("estoque")
    categoria = data.get("categoria", "geral")

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if len(nome) < MIN_NOME_LEN:
        raise ValidationError("Nome muito curto")
    if len(nome) > MAX_NOME_LEN:
        raise ValidationError("Nome muito longo")
    if not isinstance(preco, (int, float)) or isinstance(preco, bool):
        raise ValidationError("Preço inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if not isinstance(estoque, int) or isinstance(estoque, bool):
        raise ValidationError("Estoque inválido")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError(
            f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}"
        )


def validate_usuario_payload(data):
    if not data:
        raise ValidationError("Dados inválidos")
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip()
    senha = data.get("senha") or ""
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if "@" not in email or "." not in email:
        raise ValidationError("Email inválido")
    if len(senha) < MIN_SENHA_LEN:
        raise ValidationError(
            f"Senha precisa ter pelo menos {MIN_SENHA_LEN} caracteres"
        )
