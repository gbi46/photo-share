from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional

class TagsShortResponse(BaseModel):
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)