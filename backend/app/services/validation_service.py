import logging
from typing import Dict, Any, Tuple, List, Optional
from app.models.state import StructuredState, FieldStatus, SpecificGift, Executor
from app.models.gemini import GeminiExtractionResult, ExtractedInformation, UserIntent

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Business rule validation layer.
    Enforces semantic invariants, boolean normalization, child rules,
    gift rules, and rejects invalid or hallucinated data.
    """

    @classmethod
    def validate_and_clean_updates(cls, raw_updates: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validates candidate updates against business schema rules.
        Maintains backward compatibility with tests and raw dictionary callers.
        """
        cleaned: Dict[str, Any] = {}
        errors: List[str] = []

        if not isinstance(raw_updates, dict):
            return {}, ["Updates payload must be a key-value dictionary."]

        # 1. Full Name
        if "full_name" in raw_updates:
            val = raw_updates["full_name"]
            if val is not None:
                if isinstance(val, str) and len(val.strip()) >= 2:
                    cleaned["full_name"] = val.strip()
                else:
                    errors.append("Full name must be a valid string of at least 2 characters.")

        # 2. Home Address
        if "home_address" in raw_updates:
            val = raw_updates["home_address"]
            if val is not None:
                if isinstance(val, str) and len(val.strip()) >= 3:
                    cleaned["home_address"] = val.strip()
                else:
                    errors.append("Home address must be a valid string of at least 3 characters.")

        # 3. Covers Worldwide Assets
        if "covers_worldwide_assets" in raw_updates:
            val = raw_updates["covers_worldwide_assets"]
            if val is not None:
                if isinstance(val, bool):
                    cleaned["covers_worldwide_assets"] = val
                elif isinstance(val, str):
                    if val.lower() in ["true", "yes", "worldwide"]:
                        cleaned["covers_worldwide_assets"] = True
                    elif val.lower() in ["false", "no", "domestic"]:
                        cleaned["covers_worldwide_assets"] = False
                    else:
                        errors.append("covers_worldwide_assets must be a boolean.")
                else:
                    errors.append("covers_worldwide_assets must be a boolean.")

        # 4. Has Children & Children
        if "has_children" in raw_updates:
            val = raw_updates["has_children"]
            if val is not None:
                if isinstance(val, bool):
                    cleaned["has_children"] = val
                elif isinstance(val, str):
                    cleaned["has_children"] = val.lower() in ["true", "yes"]
                else:
                    errors.append("has_children must be a boolean.")

        if "children" in raw_updates:
            val = raw_updates["children"]
            if isinstance(val, list):
                clean_children = [str(c).strip() for c in val if str(c).strip()]
                cleaned["children"] = clean_children
                if len(clean_children) > 0 and raw_updates.get("has_children") is not False:
                    cleaned["has_children"] = True
            elif isinstance(val, str) and val.strip():
                cleaned["children"] = [val.strip()]
                if raw_updates.get("has_children") is not False:
                    cleaned["has_children"] = True

        # If has_children explicitly set to False, enforce empty children list
        if raw_updates.get("has_children") is False or str(raw_updates.get("has_children")).lower() in ["false", "no"]:
            cleaned["has_children"] = False
            cleaned["children"] = []

        # 5. Executor
        if "executor" in raw_updates:
            val = raw_updates["executor"]
            if isinstance(val, dict):
                exec_dict = {}
                if "name" in val and val["name"]:
                    exec_dict["name"] = str(val["name"]).strip()
                if "relationship" in val and val["relationship"]:
                    exec_dict["relationship"] = str(val["relationship"]).strip().lower()
                cleaned["executor"] = exec_dict

        # 6. Specific Gifts
        if "specific_gifts" in raw_updates:
            val = raw_updates["specific_gifts"]
            if isinstance(val, list):
                cleaned_gifts = []
                for g in val:
                    if isinstance(g, SpecificGift):
                        cleaned_gifts.append(g)
                    elif isinstance(g, dict) and "item" in g and "description" in g:
                        cleaned_gifts.append(SpecificGift(**g))
                    elif str(g).strip():
                        cleaned_gifts.append(str(g).strip())
                cleaned["specific_gifts"] = cleaned_gifts
            elif isinstance(val, str) and val.strip():
                cleaned["specific_gifts"] = [val.strip()]

        # 7. Additional Wishes
        if "additional_wishes" in raw_updates:
            val = raw_updates["additional_wishes"]
            if val is not None:
                if isinstance(val, list):
                    cleaned["additional_wishes"] = [str(w).strip() for w in val if str(w).strip()]
                elif isinstance(val, str):
                    cleaned["additional_wishes"] = val.strip()
                else:
                    cleaned["additional_wishes"] = str(val)

        return cleaned, errors

    @classmethod
    def process_extraction(
        cls,
        extraction: GeminiExtractionResult,
        current_state: StructuredState,
        last_target_field: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, FieldStatus], List[str], bool, Optional[str], List[str]]:
        """
        Validates Gemini extraction result against business rules.
        Returns:
            (validated_updates, status_updates, validation_errors, needs_clarification, clarification_question, quick_replies)
        """
        validated_updates: Dict[str, Any] = {}
        status_updates: Dict[str, FieldStatus] = {}
        errors: List[str] = []
        needs_clarification: bool = extraction.clarification_needed
        clarification_question: Optional[str] = (
            extraction.assistant_message
            or extraction.clarification_question
            or extraction.clarification_reason
        )
        quick_replies: List[str] = extraction.suggested_quick_replies or []

        info: ExtractedInformation = extraction.extracted_information

        # -------------------------------------------------------------
        # 1. Check for Irrelevant / Nonsense Answers
        # -------------------------------------------------------------
        if extraction.user_intent == UserIntent.IRRELEVANT or extraction.status == "invalid":
            if last_target_field:
                status_updates[last_target_field] = FieldStatus.UNKNOWN
            return {}, status_updates, ["The answer provided did not address the required information."], False, None, []

        # -------------------------------------------------------------
        # 2. Check for Ambiguity
        # -------------------------------------------------------------
        if extraction.ambiguous_fields:
            needs_clarification = True
            for amb_field in extraction.ambiguous_fields:
                status_updates[amb_field] = FieldStatus.AMBIGUOUS
                if amb_field == "has_children":
                    clarification_question = clarification_question or "Just to confirm, do you currently have any children?"
                    if not quick_replies:
                        quick_replies = ["No, I do not have children", "Yes, I have children"]
                elif amb_field == "covers_worldwide_assets":
                    clarification_question = clarification_question or "Could you clarify whether you would like this document to cover worldwide assets or domestic only?"
                    if not quick_replies:
                        quick_replies = ["Cover worldwide assets", "Cover domestic assets only"]

        # -------------------------------------------------------------
        # 3. Full Name
        # -------------------------------------------------------------
        if info.full_name is not None:
            name_str = info.full_name.strip()
            if len(name_str) >= 2:
                validated_updates["full_name"] = name_str
                status_updates["full_name"] = FieldStatus.CONFIRMED
            else:
                errors.append("Full name must be at least 2 characters.")

        # -------------------------------------------------------------
        # 4. Home Address
        # -------------------------------------------------------------
        if info.home_address is not None:
            addr_str = info.home_address.strip()
            if len(addr_str) >= 3:
                validated_updates["home_address"] = addr_str
                status_updates["home_address"] = FieldStatus.CONFIRMED
            else:
                errors.append("Home address must be at least 3 characters.")

        # -------------------------------------------------------------
        # 5. Covers Worldwide Assets
        # -------------------------------------------------------------
        if info.covers_worldwide_assets is not None:
            validated_updates["covers_worldwide_assets"] = bool(info.covers_worldwide_assets)
            status_updates["covers_worldwide_assets"] = FieldStatus.CONFIRMED

        # -------------------------------------------------------------
        # 6. Has Children & Children
        # -------------------------------------------------------------
        if info.has_children is not None:
            if not info.has_children:
                # Rule 1: If has_children is False, enforce empty children list and NOT_APPLICABLE
                validated_updates["has_children"] = False
                validated_updates["children"] = []
                status_updates["has_children"] = FieldStatus.CONFIRMED
                status_updates["children"] = FieldStatus.NOT_APPLICABLE
            else:
                validated_updates["has_children"] = True
                status_updates["has_children"] = FieldStatus.CONFIRMED
                if info.children and len(info.children) > 0:
                    clean_children = [str(c).strip() for c in info.children if str(c).strip()]
                    validated_updates["children"] = clean_children
                    status_updates["children"] = FieldStatus.CONFIRMED
                else:
                    # Rule 2: has_children is True, but names not yet provided
                    status_updates["children"] = FieldStatus.UNKNOWN
        elif info.children and len(info.children) > 0:
            clean_children = [str(c).strip() for c in info.children if str(c).strip()]
            validated_updates["has_children"] = True
            validated_updates["children"] = clean_children
            status_updates["has_children"] = FieldStatus.CONFIRMED
            status_updates["children"] = FieldStatus.CONFIRMED

        # -------------------------------------------------------------
        # 7. Executor
        # -------------------------------------------------------------
        if info.executor is not None:
            exec_updates: Dict[str, Any] = {}
            if info.executor.name and info.executor.name.strip():
                exec_updates["name"] = info.executor.name.strip()
                status_updates["executor.name"] = FieldStatus.CONFIRMED
            
            if info.executor.relationship and info.executor.relationship.strip():
                exec_updates["relationship"] = info.executor.relationship.strip().lower()
                status_updates["executor.relationship"] = FieldStatus.CONFIRMED

            if exec_updates:
                validated_updates["executor"] = exec_updates

        # Guard: If target field is additional_wishes, prevent items from being filed under specific_gifts
        if last_target_field == "additional_wishes":
            if info.specific_gifts and not info.additional_wishes:
                wishes_extracted = [g.description for g in info.specific_gifts]
                info.additional_wishes = wishes_extracted
                info.specific_gifts = []
            elif info.specific_gifts and info.additional_wishes:
                for g in info.specific_gifts:
                    if g.description not in info.additional_wishes:
                        info.additional_wishes.append(g.description)
                info.specific_gifts = []

        # -------------------------------------------------------------
        # 8. Specific Gifts
        # -------------------------------------------------------------
        if info.has_no_gifts:
            # Rule 3: User says "No gifts"
            validated_updates["specific_gifts"] = []
            status_updates["specific_gifts"] = FieldStatus.CONFIRMED
        elif info.specific_gifts and len(info.specific_gifts) > 0:
            gifts_list = []
            for g in info.specific_gifts:
                gift_obj = SpecificGift(
                    item=g.item,
                    recipient_name=g.recipient_name,
                    relationship=g.relationship,
                    description=g.description
                )
                gifts_list.append(gift_obj)

            if current_state.specific_gifts and not extraction.is_explicit_correction:
                existing_descs = {
                    (g.description if isinstance(g, SpecificGift) else str(g)).lower()
                    for g in current_state.specific_gifts
                }
                merged = list(current_state.specific_gifts)
                for new_g in gifts_list:
                    if new_g.description.lower() not in existing_descs:
                        merged.append(new_g)
                validated_updates["specific_gifts"] = merged
            else:
                validated_updates["specific_gifts"] = gifts_list
            status_updates["specific_gifts"] = FieldStatus.CONFIRMED

        # -------------------------------------------------------------
        # 9. Additional Wishes
        # -------------------------------------------------------------
        if info.has_no_additional_wishes:
            validated_updates["additional_wishes"] = "No additional wishes specified."
            status_updates["additional_wishes"] = FieldStatus.CONFIRMED
        elif info.additional_wishes and len(info.additional_wishes) > 0:
            wishes_list = [w.strip() for w in info.additional_wishes if w.strip()]
            new_text = "\n".join(wishes_list)
            if current_state.additional_wishes and not extraction.is_explicit_correction:
                existing = current_state.get_formatted_wishes() or ""
                if existing and existing != "No additional wishes specified.":
                    validated_updates["additional_wishes"] = f"{existing}\n{new_text}".strip()
                else:
                    validated_updates["additional_wishes"] = new_text
            else:
                validated_updates["additional_wishes"] = new_text
            status_updates["additional_wishes"] = FieldStatus.CONFIRMED

        return validated_updates, status_updates, errors, needs_clarification, clarification_question, quick_replies
