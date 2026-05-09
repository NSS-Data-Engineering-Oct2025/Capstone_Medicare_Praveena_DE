"""
routers/inpatient.py — Inpatient hospital endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
import duckdb
from fastapi_app.database import get_connection
from fastapi_app.schemas.inpatient_schema import (
    InpatientStateSummary,
    DRGSummary,
    PaymentGapByState,
    UrbanRuralSummary
)

# APIRouter groups all inpatient endpoints together
# prefix means all endpoints here start with /api/v1/inpatient
# tags groups them together in Swagger UI docs
router = APIRouter(
    prefix="/api/v1/inpatient",
    tags=["Inpatient Hospital Analytics"]
)


@router.get(
    "/state/{state_code}",
    response_model=InpatientStateSummary,
    summary="Get inpatient summary for a state",
    description="Returns hospital count, discharge volume and average Medicare payment for a given state code (e.g. TX, CA, NY)"
)
def inpatient_by_state(state_code: str, con: duckdb.DuckDBPyConnection = Depends(get_connection)):

    result = con.execute("""
            SELECT
                provider_state                          AS state,
                COUNT(DISTINCT provider_ccn)            AS total_hospitals,
                SUM(total_discharges)                   AS total_discharges,
                ROUND(AVG(avg_medicare_payment), 2)     AS avg_medicare_payment,
                ROUND(AVG(avg_submitted_charge), 2)     AS avg_submitted_charge,
                ROUND(AVG(payment_gap), 2)              AS avg_payment_gap,
                ROUND(AVG(medicare_coverage_pct), 2)    AS avg_medicare_coverage_pct
            FROM marts.mart_inpatient
            WHERE provider_state = ?
            GROUP BY provider_state
        """, [state_code.upper()]).fetchone()

    if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state: {state_code.upper()}"
            )

    return InpatientStateSummary(
            state=result[0],
            total_hospitals=result[1],
            total_discharges=result[2],
            avg_medicare_payment=result[3],
            avg_submitted_charge=result[4],
            avg_payment_gap=result[5],
            avg_medicare_coverage_pct=result[6]
        )



@router.get(
    "/top-drg",
    response_model=list[DRGSummary],
    summary="Get top DRG codes by total discharges",
    description="Returns the most common hospital procedures ranked by discharge volume. Default limit is 10."
)
def top_drg(limit: int = 10, con: duckdb.DuckDBPyConnection = Depends(get_connection)):

    results = con.execute("""
            SELECT
                drg_code,
                drg_desc,
                SUM(total_discharges) AS total_discharges
            FROM marts.mart_inpatient
            WHERE drg_code IS NOT NULL
            GROUP BY drg_code, drg_desc
            ORDER BY total_discharges DESC
            LIMIT ?
        """, [limit]).fetchall()

    return [
            DRGSummary(
                drg_code=row[0],
                drg_desc=row[1],
                total_discharges=row[2]
            )
            for row in results
        ]


@router.get(
    "/payment-gap",
    response_model=list[PaymentGapByState],
    summary="Get average payment gap by state",
    description="Returns the difference between submitted charges and Medicare payments per state, sorted highest to lowest."
)
def payment_gap_by_state(con: duckdb.DuckDBPyConnection = Depends(get_connection)):

        results = con.execute("""
            SELECT
                provider_state,
                ROUND(AVG(payment_gap), 2) AS avg_payment_gap
            FROM marts.mart_inpatient
            WHERE provider_state IS NOT NULL
            GROUP BY provider_state
            ORDER BY avg_payment_gap DESC
        """).fetchall()

        return [
            PaymentGapByState(
                provider_state=row[0],
                avg_payment_gap=row[1]
            )
            for row in results
        ]



@router.get(
    "/urban-rural",
    response_model=list[UrbanRuralSummary],
    summary="Compare urban vs rural hospital Medicare payments",
    description="Returns average Medicare payment grouped by RUCA urban/rural classification."
)
def urban_vs_rural(con: duckdb.DuckDBPyConnection = Depends(get_connection)):


        results = con.execute("""
            SELECT
                provider_ruca_desc,
                ROUND(AVG(avg_medicare_payment), 2) AS avg_medicare_payment
            FROM marts.mart_inpatient
            WHERE provider_ruca_desc IS NOT NULL
            GROUP BY provider_ruca_desc
            ORDER BY avg_medicare_payment DESC
        """).fetchall()

        return [
            UrbanRuralSummary(
                provider_ruca_desc=row[0],
                avg_medicare_payment=row[1]
            )
            for row in results
        ]
