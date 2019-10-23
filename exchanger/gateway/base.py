import typing
import logging
from abc import ABC
from django.conf import settings

from retrying import retry
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger('exchanger')


class BaseGateway(ABC):
    """
    Base class for all remote gateways that are connected with this service
    """

    GW_ADDRESS: str
    ALLOWED_STATUTES: typing.Tuple[int]
    NAME: str
    MODULE: typing.Any
    ServiceStub: object
    LOGGER: logging.Logger = logger
    response_attr: str = 'header'

    @retry(stop_max_attempt_number=settings.REMOTE_OPERATION_ATTEMPT_NUMBER)
    def _base_request(self, request_message, request_method) -> \
            typing.Tuple[bool, typing.Union[str, typing.Dict[str, typing.Any]]]:
        """Perform remote request.
        Case 1: success - return tuple of True, parsed from message dictionary response;
        Case 2: fail - return tuple of False, error string message.

        :param request_message - message to send.
        :param request_method - stub method."""

        try:
            response = request_method(request_message,
                                      timeout=settings.GRPC_TIMEOUT)

            header = getattr(response, self.response_attr)
            status = header.status

            if status in self.ALLOWED_STATUTES:
                return True, MessageToDict(response,
                                           preserving_proto_field_name=True)
            text = f"Service {self.NAME}: {request_method._method} "\
                   f"method failed with error {header.description} "\
                   f"for data {request_message.__class__.__name__}: "\
                   f"{request_message}."

        except Exception as exc:

            text = f"{self.NAME} got error {exc}"

        logger.error(text)
        return False, {'error': text}
