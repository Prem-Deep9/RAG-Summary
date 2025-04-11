"""Module for retrieving and processing OASMNR and SASBA submissions from the database."""

from typing import Dict, List

import sqlalchemy.sql.functions
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simplified_models import SimplifiedAbc, SimplifiedAbs, SimplifiedOasmnr
from app.preprocessing.submissions import (
    preprocess_abc,
    preprocess_abs,
    preprocess_submissions,
)


async def get_oasmnrs(db_session: AsyncSession, patient_id: str) -> List[Dict]:
    """Retrieve and clean OASMNR submissions for a specific patient."""
    query = select(SimplifiedOasmnr).where(
        SimplifiedOasmnr.patient_id == patient_id,
        SimplifiedOasmnr.assessment_type == "oasmnr",
        SimplifiedOasmnr.status == "ACTIVE",
    )
    result = await db_session.execute(query)
    oasmnr_submissions = result.scalars().all()
    return preprocess_submissions(oasmnr_submissions)


async def get_sasbas(db_session: AsyncSession, patient_id: str) -> List[Dict]:
    """Retrieve and clean SASBA submissions for a specific patient."""
    query = select(SimplifiedOasmnr).where(
        SimplifiedOasmnr.patient_id == patient_id,
        SimplifiedOasmnr.assessment_type == "sasba",
        SimplifiedOasmnr.status == "ACTIVE",
    )
    result = await db_session.execute(query)
    sasba_submissions = result.scalars().all()
    return preprocess_submissions(sasba_submissions)


async def get_abs(db_session: AsyncSession, patient_id: str) -> List[Dict]:
    """Retrieve and clean ABS submissions for a specific patient."""
    query = select(SimplifiedAbs).where(
        SimplifiedAbs.patient_id == patient_id,
        SimplifiedAbs.status == "ACTIVE",
    )
    result = await db_session.execute(query)
    abs_submissions = result.scalars().all()
    return preprocess_abs(abs_submissions)


async def get_abc(db_session: AsyncSession, patient_id: str) -> List[Dict]:
    """Retrieve and clean ABC submissions for a specific patient."""
    query = select(SimplifiedAbc).where(
        SimplifiedAbc.patient_id == patient_id,
        SimplifiedAbc.status == "ACTIVE",
    )
    result = await db_session.execute(query)
    abc_submissions = result.scalars().all()
    return preprocess_abc(abc_submissions)


async def get_ai_tags(db_session: AsyncSession, patient_id: str):
    """Retrieve AI tags for a specific patient."""
    oasmnr_count_query = select(
        sqlalchemy.sql.functions.sum(SimplifiedOasmnr.recordings)
    ).where(
        SimplifiedOasmnr.patient_id == patient_id,
        SimplifiedOasmnr.assessment_type == "oasmnr",
        SimplifiedOasmnr.status == "ACTIVE",
    )

    sasba_count_query = select(
        sqlalchemy.sql.functions.sum(SimplifiedOasmnr.recordings)
    ).where(
        SimplifiedOasmnr.patient_id == patient_id,
        SimplifiedOasmnr.assessment_type == "sasba",
        SimplifiedOasmnr.status == "ACTIVE",
    )

    abs_count_query = (
        select(sqlalchemy.sql.functions.count())
        .select_from(SimplifiedAbs)
        .where(
            SimplifiedAbs.patient_id == patient_id,
            SimplifiedAbs.status == "ACTIVE",
        )
    )

    abc_count_query = (
        select(sqlalchemy.sql.functions.count())
        .select_from(SimplifiedAbc)
        .where(
            SimplifiedAbc.patient_id == patient_id,
            SimplifiedAbc.status == "ACTIVE",
        )
    )

    oasmnr_count = await db_session.scalar(oasmnr_count_query)
    sasba_count = await db_session.scalar(sasba_count_query)
    abs_count = await db_session.scalar(abs_count_query)
    abc_count = await db_session.scalar(abc_count_query)

    tags = {}
    if oasmnr_count:
        tags["oasmnr_count"] = oasmnr_count
    if sasba_count:
        tags["sasba_count"] = sasba_count
    if abs_count:
        tags["abs_count"] = abs_count
    if abc_count:
        tags["abc_count"] = abc_count

    return tags
