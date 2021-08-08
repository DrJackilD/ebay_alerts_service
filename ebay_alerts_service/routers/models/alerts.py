from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel, EmailStr


class CreateAlert(BaseModel):
    email: EmailStr
    """Target email to send alert"""
    phrase: str
    """Search phrase for eBay API"""
    interval: Literal[2, 10, 30]
    """Interval between emails (in minutes)"""


class CreateAlertResponse(BaseModel):
    id: int


class UpdateAlert(BaseModel):
    email: Optional[EmailStr]
    phrase: Optional[str]
    interval: Optional[Literal[2, 10, 30]]

    def get_updated(self) -> Dict[str, Union[EmailStr, str, int]]:
        updated = {}
        if self.email:
            updated["email"] = self.email
        if self.phrase:
            updated["phrase"] = self.phrase
        if self.interval:
            updated["interval"] = self.interval
        return updated


class AlertResponse(BaseModel):
    id: int
    email: EmailStr
    phrase: str
    interval: int

    class Config:
        orm_mode = True
