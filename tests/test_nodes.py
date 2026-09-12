import pytest
from src.baseera.nodes import ClaimExtraction

def test_claim_extraction_schema():
    claim = ClaimExtraction(
        claim_id="FIN-001",
        claim="STC revenue increased by 10%",
        evidence="Annual Report",
        source="stc.com"
    )
    assert claim.claim_id == "FIN-001"