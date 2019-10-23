wallets_service_gw = None


def start_remote_gateways():
    """Create remote services gateway instances with clients."""
    from exchanger import wallets_gateway
    global wallets_service_gw
    wallets_service_gw = wallets_gateway.WalletsServiceGateway()
    return wallets_service_gw
