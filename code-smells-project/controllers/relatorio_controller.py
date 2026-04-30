from services import relatorio_service


def relatorio_vendas():
    return {"dados": relatorio_service.relatorio_vendas(), "sucesso": True}, 200
