"""
schemas/inpatient.py — Pydantic response models for inpatient endpoints.

Pydantic schemas define the exact shape of what the API returns.

"""

from pydantic import BaseModel


class InpatientStateSummary(BaseModel):
    """Summary of inpatient hospital data for a specific state."""
    state: str
    total_hospitals: int
    total_discharges: int
    avg_medicare_payment: float
    avg_submitted_charge: float
    avg_payment_gap: float
    avg_medicare_coverage_pct: float


class DRGSummary(BaseModel):
    """One DRG code with its total discharge volume."""
    drg_code: str
    drg_desc: str
    total_discharges: int


class PaymentGapByState(BaseModel):
    """Average payment gap between submitted charge and Medicare payment per state."""
    provider_state: str
    avg_payment_gap: float


class UrbanRuralSummary(BaseModel):
    """Average Medicare payment by urban/rural classification."""
    provider_ruca_desc: str
    avg_medicare_payment: float