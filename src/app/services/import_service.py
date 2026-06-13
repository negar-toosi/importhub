from src.core.database import SessionDep
from src.app.models import Import
from src.app.utils.enums import ImportStatus

class ImportServices:

    @staticmethod
    def create_import(session: SessionDep) -> Import:
        record = Import(status=ImportStatus.PENDING)
        session.add(record)
        session.commit()
        session.refresh(record)
        
        return record