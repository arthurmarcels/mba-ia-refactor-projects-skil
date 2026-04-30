from models import pedido_model

DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]


def _discount_for(faturamento):
    for threshold, rate in DISCOUNT_TIERS:
        if faturamento > threshold:
            return faturamento * rate
    return 0


def relatorio_vendas():
    s = pedido_model.stats()
    faturamento = s["faturamento"]
    desconto = _discount_for(faturamento)
    total_pedidos = s["total"]
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": s["pendentes"],
        "pedidos_aprovados": s["aprovados"],
        "pedidos_cancelados": s["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
