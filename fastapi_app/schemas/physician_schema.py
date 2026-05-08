"""
schemas/physician.py — Pydantic response models for physician endpoints.

Pydantic schemas define the exact shape of what the API returns.

"""

from typing import Optional
from pydantic import BaseModel


class PhysicianStateSummary(BaseModel):
    """Summary of physician billing data for a specific state."""
    state: str
    total_providers: int
    total_services: float
    total_beneficiaries: int
    avg_medicare_payment: float
    avg_submitted_charge: float
    avg_payment_gap: float
    avg_medicare_coverage_pct: float


class SpecialtySummary(BaseModel):
    """Average Medicare payment by provider specialty/type."""
    provider_type: str
    provider_state: Optional[str] = None
    total_providers: int
    total_services: float
    avg_medicare_payment: float


class DrugVsNonDrug(BaseModel):
    """Breakdown of drug vs non-drug Medicare services."""
    hcpcs_drug_indicator: str
    total_services: float


class PhysicianList(BaseModel):
    """One physician in the state list."""
    npi: str
    provider_first_name: Optional[str] = None
    provider_last_name: Optional[str] = None
    provider_type: Optional[str] = None
    provider_city: Optional[str] = None
    provider_state: Optional[str] = None
    medicare_participating: Optional[str] = None
    total_services: float
    avg_medicare_payment: float