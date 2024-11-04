from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from datetime import datetime

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title:Mapped[str] = mapped_column(nullable=False)
    description:Mapped[str] = mapped_column(nullable=False)
    completed_at:Mapped[datetime] = mapped_column(nullable=True)

    def is_complete(self):
        if not self.completed_at:
            return False
        return True
    
    def to_dict(self):
        return  {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete":self.is_complete()
                }        

