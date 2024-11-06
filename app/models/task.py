from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey
from typing import Optional
from ..db import db
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .goal import Goal

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title:Mapped[str] = mapped_column(nullable=False)
    description:Mapped[str] = mapped_column(nullable=False)
    completed_at:Mapped[datetime] = mapped_column(nullable=True)
    goal_id:Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal:Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    def is_complete(self):
        if not self.completed_at:
            return False
        return True
    
    def to_dict(self):
        return  {
                "id": self.id,
                "goal_id":self.goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete":self.is_complete()
                }        

    @classmethod
    def from_dict(cls,task_data):
        return cls(
            title=task_data["title"],
            description=task_data["description"]
        )