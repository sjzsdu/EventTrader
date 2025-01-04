from sqlalchemy.orm import Session

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def commit(self):
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def close(self):
        self.db.close()
