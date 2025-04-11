"""Module containing simplified database models for AI processing."""

from app.models.database import AbcSubmissions, AbsSubmissions, OasmnrSubmissions


class SimplifiedOasmnr(OasmnrSubmissions):
    """Simplified OASMNR model with essential fields for AI processing."""

    __tablename__ = None  # Use parent's table

    # Explicitly declare we want to inherit these columns
    __mapper_args__ = {
        "polymorphic_identity": "simplified_oasmnr",
        "include_properties": [
            "id",
            "patient_id",
            "time_of_behaviour",
            "behaviour",
            "severity",
            "antecedent",
            "intervention",
            "recordings",
            "status",
            "assessment_type",
            "contributing_factors",
            "antecedent_other",
            "intervention_other",
            "severity_score",
            "intrusiveness",
        ],
    }


class SimplifiedAbc(AbcSubmissions):
    """Simplified ABC model with essential fields for AI processing."""

    __tablename__ = None  # Use parent's table

    # Explicitly declare we want to inherit these columns
    __mapper_args__ = {
        "polymorphic_identity": "simplified_oasmnr",
        "include_properties": [
            "id",
            "patient_id",
            "severity",
            "occurred_at",
            "status",
            "additional_comments",
            "actions_taken",
            "before_events",
            "behaviour",
            "environment",
            "perceived_feelings",
            "location",
            "people_present",
            "restraint_techniques",
        ],
    }


class SimplifiedAbs(AbsSubmissions):
    """Simplified ABS model with essential fields for AI processing."""

    __tablename__ = None  # Use parent's table

    # Explicitly declare we want to inherit these columns
    __mapper_args__ = {
        "polymorphic_identity": "simplified_abs",
        "include_properties": [
            "id",
            "patient_id",
            "anger",
            "attention",
            "emotion_trigger",
            "impulsivity",
            "fluctuating_mood",
            "pulling_equipment",
            "repetitive_behaviour",
            "restlessness",
            "self_abusiveness",
            "self_stimulation",
            "talking",
            "uncooperative",
            "violence",
            "wandering",
            "observation_start",
            "observation_location",
            "status",
            "updated_at",
            "additional_comments",
            "score",
            "severity",
        ],
    }
