"""Claim verification and contradiction detection."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.research import Claim, Source
from app.services.synthesis_service import generate_text


async def verify_claims_against_sources(
    db: Session, project_id: UUID, sources: list[Source]
) -> None:
    """Cross-reference claims and flag contradictions."""
    claims = (
        db.query(Claim)
        .filter(Claim.project_id == project_id)
        .all()
    )

    source_map = {s.id: s for s in sources}

    for claim in claims:
        verified = []
        contradictions = []
        for source in sources:
            if source.id == claim.source_id:
                continue
            # Simple heuristic: if claim text appears in source text
            if claim.claim_text.lower() in source.full_text.lower():
                verified.append(source.id)
            else:
                # Ask LLM to check for contradiction
                prompt = (
                    f"Does the following source text contradict the claim?\n\n"
                    f"Claim: {claim.claim_text}\n\n"
                    f"Source text (excerpt): {source.full_text[:4000]}\n\n"
                    f"Answer ONLY 'yes', 'no', or 'uncertain'."
                )
                answer = await generate_text(prompt)
                answer_clean = answer.strip().lower()
                if "yes" in answer_clean:
                    contradictions.append({
                        "source_id": str(source.id),
                        "reason": "LLM flagged contradiction",
                    })
                elif "no" in answer_clean:
                    verified.append(source.id)

        claim.verified_against_sources = verified
        claim.contradiction_flags = contradictions
        if verified:
            claim.confidence = min(1.0, 0.5 + 0.1 * len(verified))
        if contradictions:
            claim.confidence = max(0.0, claim.confidence - 0.2 * len(contradictions))

    db.commit()
