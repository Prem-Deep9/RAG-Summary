import json
import os
from pathlib import Path


# Convert submissions to dictionaries
def load_mappings():
    """Load mapping configurations from JSON file."""
    # Get the directory containing this file
    current_dir = Path(__file__).parent
    # Go up one level to app directory, then into config
    mapping_path = current_dir.parent / "config" / "mapping.json"

    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping file not found at {mapping_path}")

    with open(mapping_path, encoding="utf-8") as f:
        return json.load(f)


def preprocess_submissions(submissions):
    """Process and map submission values to their corresponding display values."""
    mappings = load_mappings()

    submissions_dict = [
        {k: v for k, v in submission.__dict__.items() if not k.startswith("_")}
        for submission in submissions
    ]

    for submission in submissions_dict:
        # Map contributing factors
        if submission.get("contributing_factors"):
            submission["contributing_factors"] = [
                mappings["contributing_factors_map"].get(factor, factor)
                for factor in submission["contributing_factors"]
            ]

        # Map other fields
        submission["behaviour"] = mappings["behaviour_map"].get(
            submission.get("behaviour"), submission.get("behaviour")
        )
        submission["antecedent"] = mappings["antecedent_map"].get(
            submission.get("antecedent"), submission.get("antecedent")
        )
        submission["intervention"] = mappings["intervention_map"].get(
            submission.get("intervention"), submission.get("intervention")
        )

    return submissions_dict


def preprocess_abc(submissions):
    """Process and map ABC submission values to their corresponding display values."""
    mappings = load_mappings()

    submissions_dict = [
        {k: v for k, v in submission.__dict__.items() if not k.startswith("_")}
        for submission in submissions
    ]

    for submission in submissions_dict:
        submission["severity"] = mappings["abc_severity_map"].get(
            submission.get("severity"), submission.get("severity")
        )

    return submissions_dict


def preprocess_abs(submissions):
    """Process and map ABS submission values to their corresponding display values."""
    mappings = load_mappings()

    submissions_dict = [
        {k: v for k, v in submission.__dict__.items() if not k.startswith("_")}
        for submission in submissions
    ]

    for submission in submissions_dict:
        submission["anger"] = mappings["abs_scale_map"].get(
            submission.get("anger"), submission.get("anger")
        )
        submission["attention"] = mappings["abs_scale_map"].get(
            submission.get("attention"), submission.get("attention")
        )
        submission["emotion_trigger"] = mappings["abs_scale_map"].get(
            submission.get("emotion_trigger"), submission.get("emotion_trigger")
        )
        submission["impulsivity"] = mappings["abs_scale_map"].get(
            submission.get("impulsivity"), submission.get("impulsivity")
        )
        submission["fluctuating_mood"] = mappings["abs_scale_map"].get(
            submission.get("fluctuating_mood"), submission.get("fluctuating_mood")
        )
        submission["pulling_equipment"] = mappings["abs_scale_map"].get(
            submission.get("pulling_equipment"), submission.get("pulling_equipment")
        )
        submission["repetitive_behaviour"] = mappings["abs_scale_map"].get(
            submission.get("repetitive_behaviour"),
            submission.get("repetitive_behaviour"),
        )
        submission["restlessness"] = mappings["abs_scale_map"].get(
            submission.get("restlessness"), submission.get("restlessness")
        )
        submission["self_abusiveness"] = mappings["abs_scale_map"].get(
            submission.get("self_abusiveness"), submission.get("self_abusiveness")
        )
        submission["self_stimulation"] = mappings["abs_scale_map"].get(
            submission.get("self_stimulation"), submission.get("self_stimulation")
        )
        submission["talking"] = mappings["abs_scale_map"].get(
            submission.get("talking"), submission.get("talking")
        )
        submission["uncooperative"] = mappings["abs_scale_map"].get(
            submission.get("uncooperative"), submission.get("uncooperative")
        )
        submission["violence"] = mappings["abs_scale_map"].get(
            submission.get("violence"), submission.get("violence")
        )
        submission["wandering"] = mappings["abs_scale_map"].get(
            submission.get("wandering"), submission.get("wandering")
        )

    return submissions_dict
