from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime


class FieldStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    CONFIRMED = "CONFIRMED"
    AMBIGUOUS = "AMBIGUOUS"
    CONTRADICTORY = "CONTRADICTORY"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Executor(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None

    def is_complete(self) -> bool:
        return bool(self.name and self.relationship)


class SpecificGift(BaseModel):
    item: str
    recipient_name: Optional[str] = None
    relationship: Optional[str] = None
    description: str


class StructuredState(BaseModel):
    session_id: Optional[str] = None
    full_name: Optional[str] = None
    home_address: Optional[str] = None
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children: List[str] = Field(default_factory=list)
    executor: Executor = Field(default_factory=Executor)
    specific_gifts: List[Union[SpecificGift, str, Dict[str, Any]]] = Field(default_factory=list)
    additional_wishes: Optional[Union[str, List[str]]] = None

    # Status tracking per field - Section 9 & 10
    field_statuses: Dict[str, FieldStatus] = Field(default_factory=lambda: {
        "full_name": FieldStatus.UNKNOWN,
        "home_address": FieldStatus.UNKNOWN,
        "covers_worldwide_assets": FieldStatus.UNKNOWN,
        "has_children": FieldStatus.UNKNOWN,
        "children": FieldStatus.UNKNOWN,
        "executor.name": FieldStatus.UNKNOWN,
        "executor.relationship": FieldStatus.UNKNOWN,
        "specific_gifts": FieldStatus.UNKNOWN,
        "additional_wishes": FieldStatus.UNKNOWN,
    })

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_field_confirmed(self, field_name: str) -> bool:
        """Check if field is either CONFIRMED or NOT_APPLICABLE"""
        status = self.field_statuses.get(field_name, FieldStatus.UNKNOWN)
        return status in (FieldStatus.CONFIRMED, FieldStatus.NOT_APPLICABLE)

    def update_field_statuses(self):
        """Update statuses based on presence of values and business validation"""
        if self.full_name and len(self.full_name.strip()) >= 2:
            self.field_statuses["full_name"] = FieldStatus.CONFIRMED
        elif self.field_statuses.get("full_name") not in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            self.field_statuses["full_name"] = FieldStatus.UNKNOWN

        if self.home_address and len(self.home_address.strip()) >= 3:
            self.field_statuses["home_address"] = FieldStatus.CONFIRMED
        elif self.field_statuses.get("home_address") not in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            self.field_statuses["home_address"] = FieldStatus.UNKNOWN

        if self.covers_worldwide_assets is not None:
            self.field_statuses["covers_worldwide_assets"] = FieldStatus.CONFIRMED
        elif self.field_statuses.get("covers_worldwide_assets") not in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            self.field_statuses["covers_worldwide_assets"] = FieldStatus.UNKNOWN

        if self.has_children is not None:
            self.field_statuses["has_children"] = FieldStatus.CONFIRMED
            if not self.has_children:
                self.children = []
                self.field_statuses["children"] = FieldStatus.NOT_APPLICABLE
            else:
                if len(self.children) > 0:
                    self.field_statuses["children"] = FieldStatus.CONFIRMED
                else:
                    self.field_statuses["children"] = FieldStatus.UNKNOWN
        elif self.field_statuses.get("has_children") not in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            self.field_statuses["has_children"] = FieldStatus.UNKNOWN
            self.field_statuses["children"] = FieldStatus.UNKNOWN

        if self.executor.name:
            self.field_statuses["executor.name"] = FieldStatus.CONFIRMED
        elif self.field_statuses.get("executor.name") not in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            self.field_statuses["executor.name"] = FieldStatus.UNKNOWN

        if self.executor.relationship:
            self.field_statuses["executor.relationship"] = FieldStatus.CONFIRMED
        elif self.field_statuses.get("executor.relationship") not in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            self.field_statuses["executor.relationship"] = FieldStatus.UNKNOWN

        # specific_gifts
        if self.field_statuses.get("specific_gifts") not in (FieldStatus.CONFIRMED, FieldStatus.NOT_APPLICABLE, FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            if len(self.specific_gifts) > 0:
                self.field_statuses["specific_gifts"] = FieldStatus.CONFIRMED

        # additional_wishes
        if self.field_statuses.get("additional_wishes") not in (FieldStatus.CONFIRMED, FieldStatus.NOT_APPLICABLE, FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
            if self.additional_wishes:
                self.field_statuses["additional_wishes"] = FieldStatus.CONFIRMED

    def get_missing_fields(self) -> List[str]:
        """Returns list of essential fields that are still unknown or unresolved"""
        missing = []
        field_order = [
            "full_name",
            "home_address",
            "covers_worldwide_assets",
            "has_children",
            "children",
            "executor.name",
            "executor.relationship",
            "specific_gifts",
            "additional_wishes",
        ]

        for field in field_order:
            if field == "children" and self.has_children is False:
                continue
            status = self.field_statuses.get(field, FieldStatus.UNKNOWN)
            if status != FieldStatus.CONFIRMED and status != FieldStatus.NOT_APPLICABLE:
                missing.append(field)

        return missing

    def is_interview_complete(self) -> bool:
        """Interview is complete only when all applicable fields are CONFIRMED or NOT_APPLICABLE"""
        return len(self.get_missing_fields()) == 0

    def get_completion_percentage(self) -> int:
        """Calculate intake completion percentage across key sections"""
        total_steps = 7
        completed = 0
        if self.is_field_confirmed("full_name"):
            completed += 1
        if self.is_field_confirmed("home_address"):
            completed += 1
        if self.is_field_confirmed("covers_worldwide_assets"):
            completed += 1
        if self.is_field_confirmed("has_children") and (not self.has_children or self.is_field_confirmed("children")):
            completed += 1
        if self.is_field_confirmed("executor.name") and self.is_field_confirmed("executor.relationship"):
            completed += 1
        if self.is_field_confirmed("specific_gifts"):
            completed += 1
        if self.is_field_confirmed("additional_wishes"):
            completed += 1

        return int((completed / total_steps) * 100)

    def get_formatted_gifts(self) -> List[str]:
        """Return human-readable list of gift descriptions"""
        formatted = []
        for g in self.specific_gifts:
            if isinstance(g, SpecificGift):
                formatted.append(g.description)
            elif isinstance(g, dict):
                formatted.append(g.get("description", f"{g.get('item', 'Gift')} to {g.get('recipient_name', 'recipient')}"))
            else:
                formatted.append(str(g))
        return formatted

    def get_formatted_wishes(self) -> Optional[str]:
        """Return string representation of additional wishes"""
        if isinstance(self.additional_wishes, list):
            return "\n".join(self.additional_wishes) if self.additional_wishes else None
        return self.additional_wishes

    def to_clean_dict(self) -> Dict[str, Any]:
        """Return representation matching standard state contract for API and frontend"""
        return {
            "full_name": self.full_name,
            "home_address": self.home_address,
            "covers_worldwide_assets": self.covers_worldwide_assets,
            "has_children": self.has_children,
            "children": self.children,
            "executor": {
                "name": self.executor.name,
                "relationship": self.executor.relationship
            },
            "specific_gifts": self.get_formatted_gifts(),
            "additional_wishes": self.get_formatted_wishes(),
            "gifts_and_wishes": {
                "specific_gifts": [
                    g.model_dump() if isinstance(g, SpecificGift) else g
                    for g in self.specific_gifts
                ],
                "additional_wishes": (
                    self.additional_wishes if isinstance(self.additional_wishes, list)
                    else ([self.additional_wishes] if self.additional_wishes else [])
                )
            }
        }


class StateUpdateRequest(BaseModel):
    """Payload for PATCH /api/sessions/{session_id}/state"""
    full_name: Optional[str] = None
    home_address: Optional[str] = None
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children: Optional[List[str]] = None
    executor: Optional[Dict[str, Optional[str]]] = None
    specific_gifts: Optional[Union[List[str], List[Dict[str, Any]]]] = None
    additional_wishes: Optional[Union[str, List[str]]] = None
