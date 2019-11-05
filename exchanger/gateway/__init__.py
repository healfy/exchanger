wallets_service_gw = None
trx_service_gw = None


def start_remote_gateways():
    """Create remote services gateway instances with clients."""
    from exchanger import wallets_gateway, transactions_gateway
    global wallets_service_gw, trx_service_gw

    wallets_service_gw = wallets_gateway.WalletsServiceGateway()
    trx_service_gw = transactions_gateway.TransactionsServiceGateway()

    return wallets_service_gw, trx_service_gw
