import { useEffect, useState } from "react";
import {
  CalendarDays,
  Heart,
  Activity,
  Trash2,
  LoaderCircle,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

import "./PeriodTracker.css";

const API_URL = "http://127.0.0.1:8000";

const symptomOptions = [
  "Cramps",
  "Bloating",
  "Acne",
  "Fatigue",
  "Mood swings",
  "Headache",
  "Breast tenderness",
  "Unusual hair growth",
  "Hair thinning",
  "None",
];

function formatDate(value) {
  if (!value) return "Not recorded";

  return new Date(`${value}T00:00:00`).toLocaleDateString(
    undefined,
    {
      day: "numeric",
      month: "short",
      year: "numeric",
    }
  );
}

export default function PeriodTracker() {
  const [periods, setPeriods] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [prediction, setPrediction] = useState(null);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [symptoms, setSymptoms] = useState([]);
  const [notes, setNotes] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/cycles`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not load cycle history."
        );
      }

      setPeriods(data.periods || []);
      setCycles(data.cycles || []);
      setPrediction(data.prediction || null);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Could not connect to the backend. Check that FastAPI is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  function toggleSymptom(symptom) {
    setSymptoms((previous) => {
      if (symptom === "None") {
        return previous.includes("None") ? [] : ["None"];
      }

      const withoutNone = previous.filter(
        (item) => item !== "None"
      );

      return withoutNone.includes(symptom)
        ? withoutNone.filter((item) => item !== symptom)
        : [...withoutNone, symptom];
    });
  }

  async function savePeriod(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API_URL}/api/cycles`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate || null,
          symptoms,
          notes,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not save period."
        );
      }

      setStartDate("");
      setEndDate("");
      setSymptoms([]);
      setNotes("");

      setSuccess("Your period has been recorded successfully.");

      await loadHistory();
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Could not connect to the backend."
          : err.message
      );
    } finally {
      setSaving(false);
    }
  }

  async function deletePeriod(id) {
    if (
      !window.confirm(
        "Delete this period record? Your cycle calculations will be updated."
      )
    ) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      const response = await fetch(
        `${API_URL}/api/cycles/${id}`,
        { method: "DELETE" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not delete the period."
        );
      }

      setSuccess("Period record deleted.");
      await loadHistory();
    } catch (err) {
      setError(err.message);
    }
  }

  const completedCycles = prediction?.completed_cycles || 0;

  const isPersonalized =
    prediction?.prediction_method ===
    "personalized_cycle_history";

  return (
    <div className="period-tracker">
      <div className="pt-heading">
        <div>
          <span className="pt-eyebrow">
            <Heart size={15} />
            YOUR MENSTRUAL HEALTH
          </span>

          <h1>Period Tracker</h1>

          <p>
            Record your periods and symptoms to build your
            personalized cycle history.
          </p>
        </div>

        <div className="pt-heading-icon">
          <CalendarDays size={30} />
        </div>
      </div>

      {error && (
        <div className="pt-message pt-error" role="alert">
          <AlertCircle size={19} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="pt-message pt-success" role="status">
          <CheckCircle2 size={19} />
          <span>{success}</span>
        </div>
      )}

      <div className="pt-stats">
        <article className="pt-stat">
          <span>Recorded periods</span>
          <strong>{periods.length}</strong>
        </article>

        <article className="pt-stat">
          <span>Completed cycles</span>
          <strong>{completedCycles}</strong>
        </article>

        <article className="pt-stat">
          <span>Average cycle length</span>
          <strong>
            {prediction?.average_cycle_length != null
              ? `${prediction.average_cycle_length} days`
              : "Not available"}
          </strong>
        </article>
      </div>

      <section className="pt-card">
        <div className="pt-section-title">
          <div>
            <h2>Record a period</h2>
            <p>
              Enter the dates you actually experienced. Do not
              enter a predicted date as an actual period.
            </p>
          </div>
        </div>

        <form onSubmit={savePeriod} className="pt-form">
          <label>
            Period start date
            <input
              type="date"
              value={startDate}
              max={new Date().toISOString().slice(0, 10)}
              onChange={(event) =>
                setStartDate(event.target.value)
              }
              required
            />
          </label>

          <label>
            Period end date (optional)
            <input
              type="date"
              value={endDate}
              min={startDate || undefined}
              max={new Date().toISOString().slice(0, 10)}
              onChange={(event) =>
                setEndDate(event.target.value)
              }
            />
          </label>

          <fieldset className="pt-symptoms">
            <legend>Symptoms during this period</legend>

            <div className="pt-symptom-grid">
              {symptomOptions.map((symptom) => (
                <label
                  className={`pt-symptom ${
                    symptoms.includes(symptom)
                      ? "pt-symptom-selected"
                      : ""
                  }`}
                  key={symptom}
                >
                  <input
                    type="checkbox"
                    checked={symptoms.includes(symptom)}
                    onChange={() => toggleSymptom(symptom)}
                  />

                  <span>{symptom}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <label>
            Notes (optional)
            <textarea
              value={notes}
              onChange={(event) =>
                setNotes(event.target.value)
              }
              maxLength={1000}
              rows={3}
              placeholder="Anything else you would like to record..."
            />
          </label>

          <button
            type="submit"
            className="pt-primary-button"
            disabled={saving}
          >
            {saving ? (
              <>
                <LoaderCircle className="pt-spin" size={18} />
                Saving period...
              </>
            ) : (
              <>
                <CalendarDays size={18} />
                Save period
              </>
            )}
          </button>
        </form>
      </section>

      <section className="pt-card">
        <div className="pt-section-title">
          <div>
            <h2>Your prediction method</h2>
            <p>
              CycleSense changes methods as your recorded
              menstrual history grows.
            </p>
          </div>
        </div>

        <div className="pt-method">
          <div className="pt-method-icon">
            <Activity size={23} />
          </div>

          <div>
            <span className="pt-method-label">
              CURRENT METHOD
            </span>

            <h3>
              {isPersonalized
                ? "Personalized cycle-history estimate"
                : "Questionnaire-based estimate"}
            </h3>

            <p>
              {isPersonalized
                ? "Three completed cycles are available. CycleSense can estimate your next period from your recent cycle lengths."
                : `You have ${completedCycles} of the 3 completed cycles needed to switch to history-based estimation. Continue recording your period start dates.`}
            </p>
          </div>
        </div>

        {isPersonalized && prediction && (
          <div className="pt-prediction">
            <span>Estimated next period</span>

            <strong>
              {formatDate(prediction.estimated_next_period)}
            </strong>

            <p>
              Estimated from a typical recent cycle length of{" "}
              {prediction.median_cycle_length} days.
            </p>

            <p className="pt-disclaimer">
              {prediction.disclaimer}
            </p>
          </div>
        )}

        {isPersonalized &&
          prediction?.symptom_summary &&
          Object.keys(prediction.symptom_summary).length > 0 && (
            <div className="pt-symptom-summary">
              <h3>Symptoms recorded in recent cycles</h3>

              {Object.entries(
                prediction.symptom_summary
              ).map(([symptom, count]) => (
                <span key={symptom} className="pt-summary-chip">
                  {symptom} · {count}
                </span>
              ))}
            </div>
          )}
      </section>

      <section className="pt-card">
        <div className="pt-section-title">
          <div>
            <h2>Cycle history</h2>
            <p>
              Your period records and calculated cycle lengths.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="pt-empty">
            <LoaderCircle className="pt-spin" size={25} />
            <p>Loading your history...</p>
          </div>
        ) : periods.length === 0 ? (
          <div className="pt-empty">
            <CalendarDays size={30} />
            <h3>No periods recorded yet</h3>
            <p>
              Record your first period above to start building
              your cycle history.
            </p>
          </div>
        ) : (
          <div className="pt-history-list">
            {[...periods].reverse().map((period) => {
              const cycle = cycles.find(
                (item) =>
                  item.start_date === period.start_date
              );

              return (
                <article
                  className="pt-history-item"
                  key={period.id}
                >
                  <div className="pt-history-icon">
                    <CalendarDays size={20} />
                  </div>

                  <div className="pt-history-content">
                    <h3>{formatDate(period.start_date)}</h3>

                    <p>
                      End date: {formatDate(period.end_date)}
                    </p>

                    <p>
                      {cycle
                        ? `Cycle length: ${cycle.cycle_length} days`
                        : "Cycle length not yet available"}
                    </p>

                    {period.symptoms?.length > 0 && (
                      <div className="pt-history-symptoms">
                        {period.symptoms.map((symptom) => (
                          <span key={symptom}>
                            {symptom}
                          </span>
                        ))}
                      </div>
                    )}

                    {period.notes && (
                      <p className="pt-notes">
                        {period.notes}
                      </p>
                    )}
                  </div>

                  <button
                    type="button"
                    className="pt-delete-button"
                    onClick={() => deletePeriod(period.id)}
                    aria-label="Delete period record"
                    title="Delete period record"
                  >
                    <Trash2 size={17} />
                  </button>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}