import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/cycles", tags=["Cycle Tracker"])

DATABASE_PATH = Path(__file__).resolve().parent / "cycles.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL UNIQUE,
                end_date TEXT,
                symptoms TEXT NOT NULL DEFAULT '[]',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )


initialize_database()


class PeriodCreate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    symptoms: list[str] = Field(default_factory=list)
    notes: str = ""


def get_periods():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, start_date, end_date, symptoms, notes, created_at
            FROM periods
            ORDER BY start_date ASC
            """
        ).fetchall()

    periods = []

    for row in rows:
        item = dict(row)
        item["symptoms"] = json.loads(item["symptoms"])
        periods.append(item)

    return periods


def calculate_cycles(periods):
    """
    A cycle length is the number of days between consecutive
    period start dates.

    Three completed cycles require four recorded period start dates.
    """
    cycles = []

    for index in range(1, len(periods)):
        previous_start = date.fromisoformat(
            periods[index - 1]["start_date"]
        )
        current_start = date.fromisoformat(
            periods[index]["start_date"]
        )

        cycle_length = (current_start - previous_start).days

        if cycle_length <= 0:
            continue

        cycles.append(
            {
                "cycle_number": len(cycles) + 1,
                "start_date": periods[index - 1]["start_date"],
                "next_start_date": periods[index]["start_date"],
                "cycle_length": cycle_length,
                "symptoms": periods[index - 1]["symptoms"],
            }
        )

    return cycles


def get_prediction(periods):
    cycles = calculate_cycles(periods)
    completed_cycles = len(cycles)

    if completed_cycles < 3:
        return {
            "prediction_method": "questionnaire_based",
            "completed_cycles": completed_cycles,
            "required_cycles": 3,
            "message": (
                "Continue recording your periods. The existing "
                "questionnaire model remains the primary prediction "
                "method until three completed cycles are available."
            ),
            "cycle_lengths": [
                cycle["cycle_length"] for cycle in cycles
            ],
            "average_cycle_length": (
                round(
                    sum(c["cycle_length"] for c in cycles)
                    / completed_cycles,
                    1,
                )
                if completed_cycles
                else None
            ),
            "estimated_next_period": None,
            "symptom_summary": {},
        }

    # Use the most recent six completed cycles when available.
    recent_cycles = cycles[-6:]
    recent_lengths = [
        cycle["cycle_length"] for cycle in recent_cycles
    ]

    # Median is less sensitive to unusually short or long cycles.
    estimated_length = round(median(recent_lengths))

    last_start = date.fromisoformat(periods[-1]["start_date"])
    estimated_next_date = last_start + timedelta(
        days=estimated_length
    )

    symptom_counts = {}

    for cycle in recent_cycles:
        for symptom in cycle["symptoms"]:
            symptom_counts[symptom] = (
                symptom_counts.get(symptom, 0) + 1
            )

    return {
        "prediction_method": "personalized_cycle_history",
        "completed_cycles": completed_cycles,
        "cycle_lengths": [
            cycle["cycle_length"] for cycle in cycles
        ],
        "recent_cycle_lengths": recent_lengths,
        "average_cycle_length": round(
            sum(recent_lengths) / len(recent_lengths), 1
        ),
        "median_cycle_length": estimated_length,
        "estimated_next_period": estimated_next_date.isoformat(),
        "symptom_summary": symptom_counts,
        "message": (
            "This estimate uses your recorded cycle history. "
            "Symptoms are summarized for tracking but are not "
            "independently proven to improve this prediction."
        ),
        "disclaimer": (
            "This is an estimate, not a medical diagnosis or a "
            "guaranteed period date. Irregular cycles can make "
            "forecasting less reliable."
        ),
    }


@router.get("")
def list_periods():
    periods = get_periods()
    cycles = calculate_cycles(periods)

    return {
        "periods": periods,
        "cycles": cycles,
        "completed_cycles": len(cycles),
        "prediction": get_prediction(periods),
    }


@router.post("")
def add_period(period: PeriodCreate):
    if period.end_date and period.end_date < period.start_date:
        raise HTTPException(
            status_code=400,
            detail="Period end date cannot be before its start date.",
        )

    today = date.today()

    if period.start_date > today:
        raise HTTPException(
            status_code=400,
            detail="Period start date cannot be in the future.",
        )

    if period.end_date and period.end_date > today:
        raise HTTPException(
            status_code=400,
            detail="Period end date cannot be in the future.",
        )

    if period.end_date and (
        period.end_date - period.start_date
    ).days > 14:
        raise HTTPException(
            status_code=400,
            detail="Please verify the period dates. The duration exceeds 14 days.",
        )

    existing_periods = get_periods()

    for existing in existing_periods:
        existing_start = date.fromisoformat(
            existing["start_date"]
        )

        if existing_start == period.start_date:
            raise HTTPException(
                status_code=409,
                detail="A period with this start date already exists.",
            )

        if period.end_date:
            if existing["end_date"]:
                existing_end = date.fromisoformat(
                    existing["end_date"]
                )
            else:
                existing_end = existing_start

            if (
                period.start_date <= existing_end
                and period.end_date >= existing_start
            ):
                raise HTTPException(
                    status_code=400,
                    detail="These dates overlap an existing period record.",
                )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO periods (
                start_date,
                end_date,
                symptoms,
                notes,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                period.start_date.isoformat(),
                (
                    period.end_date.isoformat()
                    if period.end_date
                    else None
                ),
                json.dumps(period.symptoms),
                period.notes,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

        new_id = cursor.lastrowid

    periods = get_periods()

    return {
        "message": "Period recorded successfully.",
        "period_id": new_id,
        "completed_cycles": len(calculate_cycles(periods)),
        "prediction": get_prediction(periods),
    }


@router.delete("/{period_id}")
def delete_period(period_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM periods WHERE id = ?",
            (period_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Period record not found.",
            )

    periods = get_periods()

    return {
        "message": "Period record deleted.",
        "completed_cycles": len(calculate_cycles(periods)),
        "prediction": get_prediction(periods),
    }


@router.get("/prediction")
def cycle_prediction():
    periods = get_periods()
    return get_prediction(periods)