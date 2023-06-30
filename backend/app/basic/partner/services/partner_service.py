from app.basic.partner.models import Partner
from app.basic.partner.schemas import PartnerCreateScheme, PartnerUpdateScheme
from core.db.session import session
from core.service.base import BaseService


class PartnerService(BaseService[Partner, PartnerCreateScheme, PartnerUpdateScheme]):
    def __init__(self, request, db_session=session):
        super(PartnerService, self).__init__(request, Partner, db_session)


