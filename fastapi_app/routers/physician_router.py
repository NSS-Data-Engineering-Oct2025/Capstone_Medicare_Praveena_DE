"""
routers/physician.py — Physician analytics endpoints.

"""

from fastapi import APIRouter, HTTPException, Query, Depends
import duckdb
from fastapi_app.database import get_connection
from fastapi_app.schemas.physician_schema import (
    PhysicianStateSummary,
    SpecialtySummary,
    DrugVsNonDrug,
    PhysicianList
)

# APIRouter groups all physician endpoints together
# prefix means all endpoints here start with /api/v1/physician
# tags groups them together in Swagger UI docs
router = APIRouter(
    prefix="/api/v1/physician",
    tags=["Physician Analytics"]
)


@router.get(
    "/state/{state_code}",
    response_model=PhysicianStateSummary,
    summary="Get physician billing summary for a state",
    description="Returns provider count, total services, beneficiaries and average Medicare payment for a given state code (e.g. TX, CA, NY)"
)
def physician_by_state(state_code: str, con: duckdb.DuckDBPyConnection = Depends(get_connection)):


        result = con.execute("""
            SELECT
                provider_state                              AS state,
                COUNT(DISTINCT npi)                         AS total_providers,
                ROUND(SUM(total_services), 2)               AS total_services,
                SUM(total_beneficiaries)                    AS total_beneficiaries,
                ROUND(AVG(avg_medicare_payment), 2)         AS avg_medicare_payment,
                ROUND(AVG(avg_submitted_charge), 2)         AS avg_submitted_charge,
                ROUND(AVG(payment_gap), 2)                  AS avg_payment_gap,
                ROUND(AVG(medicare_coverage_pct), 2)        AS avg_medicare_coverage_pct
            FROM marts.mart_physician
            WHERE provider_state = ?
            GROUP BY provider_state
        """, [state_code.upper()]).fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state: {state_code.upper()}"
            )

        return PhysicianStateSummary(
            state=result[0],
            total_providers=result[1],
            total_services=result[2],
            total_beneficiaries=result[3],
            avg_medicare_payment=result[4],
            avg_submitted_charge=result[5],
            avg_payment_gap=result[6],
            avg_medicare_coverage_pct=result[7]
        )



@router.get(
    "/specialties",
    response_model=list[SpecialtySummary],
    summary="Get physician specialties with Medicare payment stats",
    description="""
    Returns physician specialties with provider count and average Medicare payment.
    Filter by state or specialty type for more specific results.
 
    Examples:
    - /api/v1/physician/specialties                          → all specialties nationally
    - /api/v1/physician/specialties?state=CA                 → top specialties in California
    - /api/v1/physician/specialties?specialty=Cardiology     → Cardiology stats by state
    - /api/v1/physician/specialties?state=CA&specialty=Cardiology → Cardiology in California
    """
)
def specialties(
    state: str = Query(None, description="2-letter state code e.g. CA, TX, NY"),
    specialty: str = Query(None, description="Provider specialty type e.g. Cardiology"),
    limit: int = Query(15, description="Number of results", le=100),
    con: duckdb.DuckDBPyConnection = Depends(get_connection)
):


        # build filters dynamically
        filters = ["provider_type IS NOT NULL"]
        params = []
 
        if state:
            filters.append("provider_state = ?")
            params.append(state.upper())
 
        if specialty:
            filters.append("provider_type ILIKE ?")
            params.append(f"%{specialty}%")
 
        where_clause = "WHERE " + " AND ".join(filters)
 
        # include state in group by only when filtering by specialty
        group_by = "provider_type, provider_state" if specialty else "provider_type"
        select_state = "provider_state" if specialty else "NULL AS provider_state"
 
        params.append(limit)
 
        results = con.execute(f"""
            SELECT
                provider_type,
                {select_state},
                COUNT(DISTINCT npi)                 AS total_providers,
                ROUND(SUM(total_services), 2)       AS total_services,
                ROUND(AVG(avg_medicare_payment), 2) AS avg_medicare_payment
            FROM marts.mart_physician
            {where_clause}
            GROUP BY {group_by}
            ORDER BY avg_medicare_payment DESC
            LIMIT ?
        """, params).fetchall()
 
        if not results:
            raise HTTPException(
                status_code=404,
                detail="No specialties found for the given filters"
            )
 
        return [
            SpecialtySummary(
                provider_type=row[0],
                provider_state=row[1],
                total_providers=row[2],
                total_services=row[3],
                avg_medicare_payment=row[4]
            )
            for row in results
        ]



@router.get(
    "/drug-vs-nondrug",
    response_model=list[DrugVsNonDrug],
    summary="Get drug vs non-drug service breakdown",
    description="""
    Returns total Medicare services split by drug vs non-drug.
    Optionally filter by state code (e.g. CA, TX, NY) to get
    state-level breakdown instead of national.
 
    Examples:
    - /api/v1/physician/drug-vs-nondrug         → national breakdown
    - /api/v1/physician/drug-vs-nondrug?state=CA → California breakdown
    """
)
def drug_vs_nondrug(state: str = None, con: duckdb.DuckDBPyConnection = Depends(get_connection)):

        # build WHERE clause based on whether state is provided
        if state:
            where_clause = "WHERE hcpcs_drug_indicator IS NOT NULL AND provider_state = ?"
            params = [state.upper()]
        else:
            where_clause = "WHERE hcpcs_drug_indicator IS NOT NULL"
            params = []
 
        results = con.execute(f"""
            SELECT
                CASE
                    WHEN hcpcs_drug_indicator = 'Y' THEN 'Drug'
                    WHEN hcpcs_drug_indicator = 'N' THEN 'Non-Drug'
                    ELSE 'Unknown'
                END                             AS hcpcs_drug_indicator,
                ROUND(SUM(total_services), 2)   AS total_services
            FROM marts.mart_physician
            {where_clause}
            GROUP BY hcpcs_drug_indicator
            ORDER BY total_services DESC
        """, params).fetchall()
 
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state: {state.upper() if state else 'N/A'}"
            )
 
        return [
            DrugVsNonDrug(
                hcpcs_drug_indicator=row[0],
                total_services=row[1]
            )
            for row in results
        ]




@router.get(
    "/list",
    response_model=list[PhysicianList],
    summary="Get list of physicians by state",
    description="""
    Returns a list of physicians for a given state.
    Use limit and offset for pagination.
    
    Examples:
    - /api/v1/physician/list?state=CA
    - /api/v1/physician/list?state=TX&limit=50
    - /api/v1/physician/list?state=NY&limit=50&offset=50
    """
)
def list_physicians(
    state: str = Query(..., description="2-letter state code", example="CA"),
    limit: int = Query(50, description="Number of results per page", le=100),
    offset: int = Query(0, description="Starting position for pagination"),
    con: duckdb.DuckDBPyConnection = Depends(get_connection)
):

        results = con.execute("""
            SELECT
                npi,
                provider_first_name,
                provider_last_name,
                provider_type,
                provider_city,
                provider_state,
                medicare_participating,
                ROUND(SUM(total_services), 2)       AS total_services,
                ROUND(AVG(avg_medicare_payment), 2) AS avg_medicare_payment
            FROM marts.mart_physician
            WHERE provider_state = ?
            GROUP BY
                npi,
                provider_first_name,
                provider_last_name,
                provider_type,
                provider_city,
                provider_state,
                medicare_participating
            ORDER BY avg_medicare_payment DESC
            LIMIT ? OFFSET ?
        """, [state.upper(), limit, offset]).fetchall()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No physicians found for state: {state.upper()}"
            )

        return [
            PhysicianList(
                npi=row[0],
                provider_first_name=row[1],
                provider_last_name=row[2],
                provider_type=row[3],
                provider_city=row[4],
                provider_state=row[5],
                medicare_participating=row[6],
                total_services=row[7],
                avg_medicare_payment=row[8]
            )
            for row in results
        ]
