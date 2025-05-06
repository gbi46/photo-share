from pydantic import BaseModel
from pydantic.config import ConfigDict

class RoleResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
