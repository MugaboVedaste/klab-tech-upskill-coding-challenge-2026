from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    """Same opaque-token auth as DRF's TokenAuthentication, but clients
    send it as `Authorization: Bearer <token>` instead of `Token <token>`.
    """

    keyword = "Bearer"
