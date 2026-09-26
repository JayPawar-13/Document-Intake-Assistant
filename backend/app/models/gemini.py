from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class NextAction(str, Enum):
    ASK_NEXT_QUESTION = "ASK_NEXT_QUESTION"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    WAIT_FOR_CORRECTION = "WAIT_FOR_CORRECTION"
    INTERVIEW_COMPLETE = "INTERVIEW_COMPLETE"


class UserIntent(str, Enum):
    ANSWER = "answer"
    CORRECTION = "correction"
    REFUSAL = "refusal"
    DONT_KNOW = "dont_know"
    IRRELEVANT = "irrelevant"
    AMBIGUOUS = "ambiguous"
    CONTRADICTION = "contradiction"


class ExecutorExtraction(BaseModel):
    name: Optional[str] = Field(default=None, description="Full name of designated executor")
    relationship: Optional[str] = Field(default=None, description="Relationship of executor to user, e.g. brother, sister, friend")


class GiftExtraction(BaseModel):
    item: str = Field(description="Specific item or asset being gifted, e.g. watch, laptop, house")
    recipient_name: Optional[str] = Field(default=None, description="Name of the person receiving the gift")
    relationship: Optional[str] = Field(default=None, description="Relationship of the recipient to the user")
    description: str = Field(description="Complete plain-English description of the bequest, e.g. My watch should go to my brother Rohit.")


class ExtractedInformation(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Full legal name of the person creating the document")
    home_address: Optional[str] = Field(default=None, description="Complete home or residential address")
    covers_worldwide_assets: Optional[bool] = Field(default=None, description="True if document should cover assets worldwide, False if domestic only")
    has_children: Optional[bool] = Field(default=None, description="True if user currently has children, False if user does not have children")
    children: List[str] = Field(default_factory=list, description="List of children's names if stated")
    executor: Optional[ExecutorExtraction] = Field(default=None, description="Executor details if provided")
    specific_gifts: List[GiftExtraction] = Field(default_factory=list, description="Specific gifts or bequests to particular people")
    has_no_gifts: Optional[bool] = Field(default=None, description="True if user explicitly stated they have no specific gifts")
    additional_wishes: List[str] = Field(default_factory=list, description="List of additional personal wishes or funeral preferences")
    has_no_additional_wishes: Optional[bool] = Field(default=None, description="True if user explicitly stated they have no additional wishes")


class GeminiExtractionResult(BaseModel):
    status: str = Field(
        default="valid",
        description="Overall extraction status: 'valid', 'ambiguous', 'contradictory', 'invalid', 'incomplete', or 'correction'"
    )
    user_intent: UserIntent = Field(
        default=UserIntent.ANSWER,
        description="Classified user intent: answer, correction, refusal, dont_know, irrelevant, ambiguous, contradiction"
    )
    extracted_information: ExtractedInformation = Field(
        default_factory=ExtractedInformation,
        description="Information explicitly stated in user message"
    )
    ambiguous_fields: List[str] = Field(
        default_factory=list,
        description="Names of fields where user statement was vague or undecided (e.g. ['has_children'])"
    )
    contradictory_fields: List[str] = Field(
        default_factory=list,
        description="Names of fields conflicting with previous confirmed state without an explicit correction cue"
    )
    invalid_fields: List[str] = Field(
        default_factory=list,
        description="Fields for which the user gave an irrelevant or nonsense answer"
    )
    clarification_needed: bool = Field(
        default=False,
        description="True if clarification is required before updating state"
    )
    clarification_reason: Optional[str] = Field(
        default=None,
        description="Reason why clarification is needed"
    )
    is_explicit_correction: bool = Field(
        default=False,
        description="True if user explicitly signaled a correction (e.g. 'actually', 'instead of')"
    )
    suggested_quick_replies: List[str] = Field(
        default_factory=list,
        description="Helpful quick choice buttons for the user to clarify ambiguity"
    )
    assistant_message: Optional[str] = Field(
        default=None,
        description="Friendly response text"
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description="Clarification question to ask user if clarification is needed"
    )

    @property
    def needs_clarification(self) -> bool:
        return self.clarification_needed

    @property
    def is_correction(self) -> bool:
        return self.is_explicit_correction

    @property
    def updates(self) -> dict:
        res = {}
        info = self.extracted_information
        if info.full_name is not None:
            res["full_name"] = info.full_name
        if info.home_address is not None:
            res["home_address"] = info.home_address
        if info.covers_worldwide_assets is not None:
            res["covers_worldwide_assets"] = info.covers_worldwide_assets
        if info.has_children is not None:
            res["has_children"] = info.has_children
        if info.children:
            res["children"] = info.children
        if info.executor:
            res["executor"] = {
                "name": info.executor.name,
                "relationship": info.executor.relationship
            }
        if info.specific_gifts:
            res["specific_gifts"] = info.specific_gifts
        elif info.has_no_gifts:
            res["specific_gifts"] = []
        if info.additional_wishes:
            res["additional_wishes"] = info.additional_wishes
        elif info.has_no_additional_wishes:
            res["additional_wishes"] = "No additional wishes specified."
        return res
