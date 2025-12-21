"""Data models"""

from models import ModelBase
from sqlalchemy.orm import Mapped, mapped_column


class StructuredData(ModelBase):
    """A model for structured data"""

    __tablename__ = "structured_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    col_int: Mapped[int] = mapped_column()
    col_str: Mapped[str] = mapped_column()
    col_bool: Mapped[bool] = mapped_column()
