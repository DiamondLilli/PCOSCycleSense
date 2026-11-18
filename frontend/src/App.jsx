import { useEffect, useState } from "react";
import {
  Activity,
  CalendarDays,
  ChartNoAxesCombined,
  Heart,
  Home,
  Menu,
  Settings,
  Sparkles,
  ChevronRight,
  ArrowRight,
  Moon,
  ShieldCheck,
  CircleHelp,
  ClipboardList,
  Clock3,
  X,
  Brain,
  LoaderCircle,
  AlertCircle,
  Trash2,
} from "lucide-react";

import PeriodTracker from "./PeriodTracker";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";
const HISTORY_KEY = "cyclesense_history";

const navigation = [
  { name: "Dashboard", icon: Home },
  { name: "Cycle Assessment", icon: ClipboardList },
  { name: "My Insights", icon: ChartNoAxesCombined },
  { name: "Cycle History", icon: CalendarDays },
  { name: "Period Tracker", icon: Activity },
];

const initialForm = {
  "Period Length": "",
  Age: "",
  Overweight: "",
  "loss weight gain / weight loss": "",
  "Difficulty in conceiving": "",
  "Hair growth on Chin": "",
  "Hair growth  on Cheeks": "",
  "Hair growth Between breasts": "",
  "Hair growth  on Upper lips": "",
  "Hair growth in Arms": "",
  "Hair growth on Inner thighs": "",
  "Acne or skin tags": "",
  "Hair thinning or hair loss": "",
  "Dark patches": "",
  "always tired": "",
  "more Mood Swings": "",
  "exercise per week": "",
  "eat outside per week": "",
  "canned food often": "",
};

const fieldGroups = [
  {
    title: "Menstrual health",
    description: "Share details about your period.",
    fields: [
      {
        name: "Period Length",
        label: "Usual period duration",
        type: "select",
        options: [
          "2-3 days",
          "4-5 days",
          "6-7 days",
          "More than 7 days",
        ],
      },
    ],
  },
  {
    title: "About you",
    description: "A few basic details.",
    fields: [
      {
        name: "Age",
        label: "Age group",
        type: "select",
        options: [
          "Below 18",
          "18-25",
          "26-30",
          "31-35",
          "36-40",
          "40-45",
          "Above 45",
        ],
      },
    ],
  },
  {
    title: "Health and symptoms",
    description:
      "Select the responses that best describe your experience.",
    fields: [
      {
        name: "Overweight",
        label: "Do you consider yourself overweight?",
        type: "select",
        options: ["Yes", "No", "Maybe"],
      },
      {
        name: "loss weight gain / weight loss",
        label: "Have you experienced weight gain or weight loss?",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "Difficulty in conceiving",
        label: "Difficulty conceiving",
        type: "select",
        options: ["Not Applicable", "Yes", "No"],
      },
      {
        name: "Hair growth on Chin",
        label: "Hair growth on chin",
        type: "select",
        options: ["normal", "moderate", "excessive"],
      },
      {
        name: "Hair growth  on Cheeks",
        label: "Hair growth on cheeks",
        type: "select",
        options: ["normal", "moderate", "excessive"],
      },
      {
        name: "Hair growth Between breasts",
        label: "Hair growth between breasts",
        type: "select",
        options: ["normal", "moderate", "excessive"],
      },
      {
        name: "Hair growth  on Upper lips",
        label: "Hair growth on upper lips",
        type: "select",
        options: ["normal", "moderate", "excessive"],
      },
      {
        name: "Hair growth in Arms",
        label: "Hair growth on arms",
        type: "select",
        options: ["normal", "moderate", "excessive"],
      },
      {
        name: "Hair growth on Inner thighs",
        label: "Hair growth on inner thighs",
        type: "select",
        options: ["normal", "moderate", "excessive"],
      },
      {
        name: "Acne or skin tags",
        label: "Acne or skin tags",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "Hair thinning or hair loss",
        label: "Hair thinning or hair loss",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "Dark patches",
        label: "Dark patches on the skin",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "always tired",
        label: "Do you often feel tired?",
        type: "select",
        options: ["Yes", "No"],
      },
      {
        name: "more Mood Swings",
        label: "Have you experienced mood swings?",
        type: "select",
        options: ["Yes", "No"],
      },
    ],
  },
  {
    title: "Lifestyle",
    description: "Tell us a little about your habits.",
    fields: [
      {
        name: "exercise per week",
        label: "Exercise sessions per week",
        type: "number",
        min: 0,
        max: 7,
      },
      {
        name: "eat outside per week",
        label: "Meals eaten outside per week",
        type: "number",
        min: 0,
        max: 7,
      },
      {
        name: "canned food often",
        label: "Do you often eat canned food?",
        type: "select",
        options: ["Yes", "No"],
      },
    ],
  },
];

function readHistory() {
  try {
    const saved = localStorage.getItem(HISTORY_KEY);
    const parsed = saved ? JSON.parse(saved) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [form, setForm] = useState(initialForm);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [cycleHistory, setCycleHistory] = useState(readHistory);

  useEffect(() => {
    try {
      localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(cycleHistory)
      );
    } catch (storageError) {
      console.error("Could not save assessment history:", storageError);
    }
  }, [cycleHistory]);

  function navigate(page) {
    setActivePage(page);
    setSidebarOpen(false);
    setError("");
  }

  function updateForm(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setError("");
  }

  async function submitAssessment(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const features = {
        ...form,
        "exercise per week": Number(form["exercise per week"]),
        "eat outside per week": Number(form["eat outside per week"]),
      };

      const response = await fetch(`${API_URL}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ features }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.error ||
            "Unable to process your assessment."
        );
      }

      if (!data.predicted_cycle_category) {
        throw new Error(
          "The prediction API did not return a cycle category."
        );
      }

      const entry = {
        id: `${Date.now()}-${Math.random()
          .toString(36)
          .slice(2, 9)}`,
        date: new Date().toISOString(),
        predicted_cycle_category: data.predicted_cycle_category,
        model_type: data.model_type || "Tuned Random Forest",
        features: { ...features },
      };

      setPrediction(data);

      setCycleHistory((previous) => [
        entry,
        ...previous,
      ]);

      navigate("My Insights");
    } catch (err) {
      console.error("Prediction error:", err);

      setError(
        err.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
          : err.message || "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  function startNewAssessment() {
    setForm(initialForm);
    setPrediction(null);
    setError("");
    navigate("Cycle Assessment");
  }

  function deleteHistoryEntry(id) {
    setCycleHistory((previous) =>
      previous.filter((entry) => entry.id !== id)
    );
  }

  function clearHistory() {
    if (!cycleHistory.length) return;

    if (
      window.confirm(
        "Delete all questionnaire assessment history?"
      )
    ) {
      setCycleHistory([]);
    }
  }

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >
        <div className="brand">
          <div className="brand-icon">
            <Activity size={24} />
          </div>

          <div>
            <h2>CycleSense</h2>
            <span>PCOS CARE</span>
          </div>

          <button
            className="close-sidebar"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="navigation">
          {navigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${
                activePage === name ? "nav-active" : ""
              }`}
              onClick={() => navigate(name)}
            >
              <Icon size={19} />
              <span>{name}</span>

              {activePage === name && (
                <span className="active-indicator" />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="support-card">
            <div className="support-icon">
              <CircleHelp size={20} />
            </div>

            <h4>Need some guidance?</h4>

            <p>
              Learn more about menstrual health and PCOS.
            </p>

            <button
              onClick={() =>
                window.open(
                  "https://www.womenshealth.gov/",
                  "_blank",
                  "noopener,noreferrer"
                )
              }
            >
              Explore resources <ArrowRight size={15} />
            </button>
          </div>

          <button
            className="nav-item settings-item"
            onClick={() => navigate("Settings")}
          >
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="avatar">U</div>

            <div className="profile-info">
              <strong>Your Profile</strong>
              <span>Personal health space</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="menu-button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            <span>CycleSense</span>
            <ChevronRight size={15} />
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <div className="privacy-indicator">
              <ShieldCheck size={16} />
              <span>Private workspace</span>
            </div>
          </div>
        </header>

        <div className="page-container">
          {activePage === "Dashboard" && (
            <>
              <section className="welcome-section">
                <div>
                  <div className="eyebrow">
                    <Sparkles size={15} />
                    YOUR PERSONAL HEALTH SPACE
                  </div>

                  <h1>
                    Understand your cycle,
                    <br />
                    <span>one step at a time.</span>
                  </h1>

                  <p className="welcome-description">
                    Track your menstrual history, record symptoms,
                    and explore experimental cycle estimates.
                  </p>

                  <button
                    className="primary-button"
                    onClick={() => navigate("Period Tracker")}
                  >
                    Track your period <ArrowRight size={18} />
                  </button>
                </div>

                <div className="hero-illustration">
                  <div className="hero-circle">
                    <div className="hero-moon">
                      <Moon size={64} />
                    </div>

                    <div className="floating-card">
                      <Heart size={18} />
                      <span>Your health matters</span>
                    </div>
                  </div>
                </div>
              </section>

              <section className="overview-grid">
                <article className="overview-card">
                  <div className="card-top">
                    <div className="stat-icon lavender">
                      <ClipboardList size={22} />
                    </div>
                    <span className="stat-label">
                      Assessments
                    </span>
                  </div>

                  <h2>{cycleHistory.length}</h2>
                  <p>Saved questionnaire assessments</p>
                </article>

                <article className="overview-card">
                  <div className="card-top">
                    <div className="stat-icon pink">
                      <CalendarDays size={22} />
                    </div>
                    <span className="stat-label">
                      Latest activity
                    </span>
                  </div>

                  <h2>
                    {cycleHistory.length
                      ? new Date(
                          cycleHistory[0].date
                        ).toLocaleDateString(undefined, {
                          day: "numeric",
                          month: "short",
                        })
                      : "—"}
                  </h2>

                  <p>
                    {cycleHistory.length
                      ? "Most recent assessment"
                      : "No assessment yet"}
                  </p>
                </article>

                <article className="overview-card">
                  <div className="card-top">
                    <div className="stat-icon peach">
                      <Brain size={22} />
                    </div>
                    <span className="stat-label">
                      Prediction
                    </span>
                  </div>

                  <h2>Ready</h2>
                  <p>Experimental research model</p>
                </article>
              </section>

              <section className="assessment-card">
                <div className="assessment-card-content">
                  <div className="eyebrow">
                    <Sparkles size={15} />
                    YOUR CYCLE JOURNEY
                  </div>

                  <h2>
                    Build a clearer picture of your cycle.
                  </h2>

                  <p>
                    Record your period dates and symptoms. CycleSense
                    will calculate completed cycles and use your
                    recorded history for personalized estimates once
                    enough history is available.
                  </p>

                  <button
                    className="primary-button"
                    onClick={() => navigate("Period Tracker")}
                  >
                    Open period tracker{" "}
                    <ArrowRight size={18} />
                  </button>
                </div>
              </section>
            </>
          )}

          {activePage === "Cycle Assessment" && (
            <section className="form-page">
              <div className="eyebrow">
                <ClipboardList size={15} />
                YOUR CYCLE PROFILE
              </div>

              <h1>Cycle assessment</h1>

              <p className="welcome-description">
                Complete this questionnaire for an experimental
                cycle-length category estimate.
              </p>

              <form
                className="assessment-form"
                onSubmit={submitAssessment}
              >
                {fieldGroups.map((group) => (
                  <section
                    className="form-group"
                    key={group.title}
                  >
                    <div className="section-heading">
                      <div>
                        <h2>{group.title}</h2>
                        <p>{group.description}</p>
                      </div>
                    </div>

                    {group.fields.map((field) => (
                      <label key={field.name}>
                        {field.label}

                        {field.type === "select" ? (
                          <select
                            name={field.name}
                            value={form[field.name]}
                            onChange={updateForm}
                            required
                          >
                            <option value="">
                              Choose an answer
                            </option>

                            {field.options.map((option) => (
                              <option
                                key={option}
                                value={option}
                              >
                                {option}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="number"
                            name={field.name}
                            min={field.min}
                            max={field.max}
                            step="1"
                            value={form[field.name]}
                            onChange={updateForm}
                            required
                          />
                        )}
                      </label>
                    ))}
                  </section>
                ))}

                {error && (
                  <div
                    className="form-notice error-notice"
                    role="alert"
                  >
                    <AlertCircle size={20} />
                    <p>{error}</p>
                  </div>
                )}

                <div className="form-notice">
                  <ShieldCheck size={19} />
                  <p>
                    This is an experimental research prototype,
                    not a medical diagnostic tool. Predictions
                    are not clinically validated.
                  </p>
                </div>

                <button
                  className="primary-button"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <LoaderCircle
                        size={18}
                        className="spin-icon"
                      />
                      Analysing responses...
                    </>
                  ) : (
                    <>
                      Get cycle estimate{" "}
                      <ArrowRight size={18} />
                    </>
                  )}
                </button>
              </form>
            </section>
          )}

          {activePage === "My Insights" && (
            <section className="insights-page">
              <div className="eyebrow">
                <ChartNoAxesCombined size={15} />
                YOUR INSIGHTS
              </div>

              <h1>Cycle insights</h1>

              <p className="welcome-description">
                Review the output of your questionnaire-based model.
                Personalized estimates are available in Period Tracker
                after sufficient cycle history is recorded.
              </p>

              {prediction ? (
                <article className="insight-result">
                  <div className="stat-icon lavender">
                    <Brain size={24} />
                  </div>

                  <h2>Estimated cycle-length category</h2>

                  <p className="prediction-category">
                    {prediction.predicted_cycle_category}
                  </p>

                  <p>
                    <strong>Model:</strong>{" "}
                    {prediction.model_type ||
                      "Tuned Random Forest"}
                  </p>

                  {prediction.class_probabilities && (
                    <div className="probability-section">
                      <h3>Model output by category</h3>

                      <p>
                        These scores are model outputs, not
                        calibrated medical probabilities.
                      </p>

                      {Object.entries(
                        prediction.class_probabilities
                      ).map(([category, probability]) => {
                        const percentage = Math.max(
                          0,
                          Math.min(
                            100,
                            Number(probability) * 100
                          )
                        );

                        return (
                          <div
                            className="probability-row"
                            key={category}
                          >
                            <div className="probability-label">
                              <span>{category}</span>
                              <strong>
                                {percentage.toFixed(1)}%
                              </strong>
                            </div>

                            <div className="probability-track">
                              <div
                                className="probability-fill"
                                style={{
                                  width: `${percentage}%`,
                                }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  <div className="form-notice">
                    <ShieldCheck size={19} />
                    <p>
                      This questionnaire estimate does not predict
                      an exact next-period date. Use Period Tracker
                      to record actual menstrual dates and obtain
                      history-based estimates when sufficient
                      records are available.
                    </p>
                  </div>

                  <button
                    className="secondary-button"
                    onClick={startNewAssessment}
                  >
                    New assessment <ArrowRight size={17} />
                  </button>
                </article>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">
                    <Clock3 size={28} />
                  </div>

                  <h2>Your insights will appear here.</h2>

                  <p>
                    Complete the questionnaire to get an
                    experimental estimate.
                  </p>

                  <button
                    className="primary-button"
                    onClick={() =>
                      navigate("Cycle Assessment")
                    }
                  >
                    Start assessment{" "}
                    <ArrowRight size={18} />
                  </button>
                </div>
              )}
            </section>
          )}

          {activePage === "Cycle History" && (
            <section className="history-page">
              <div className="eyebrow">
                <CalendarDays size={15} />
                YOUR SAVED ASSESSMENTS
              </div>

              <h1>Cycle history</h1>

              <p className="welcome-description">
                This page contains questionnaire assessment history.
                For actual period dates and completed cycle lengths,
                open Period Tracker.
              </p>

              {cycleHistory.length > 0 ? (
                <>
                  <div className="history-summary">
                    <div className="stat-icon lavender">
                      <ClipboardList size={22} />
                    </div>

                    <div>
                      <span>Total assessments</span>
                      <h2>{cycleHistory.length}</h2>
                    </div>
                  </div>

                  <div className="history-list">
                    {cycleHistory.map((entry) => (
                      <article
                        className="history-entry"
                        key={entry.id}
                      >
                        <div className="history-entry-icon">
                          <CalendarDays size={21} />
                        </div>

                        <div className="history-entry-content">
                          <span className="history-date">
                            {new Date(
                              entry.date
                            ).toLocaleString(undefined, {
                              dateStyle: "medium",
                              timeStyle: "short",
                            })}
                          </span>

                          <h3>
                            {entry.predicted_cycle_category}
                          </h3>

                          <p>
                            Model:{" "}
                            {entry.model_type ||
                              "Tuned Random Forest"}
                          </p>

                          {entry.features && (
                            <details className="history-details">
                              <summary>
                                View submitted responses
                              </summary>

                              <dl>
                                {Object.entries(
                                  entry.features
                                ).map(([key, value]) => (
                                  <div key={key}>
                                    <dt>{key}</dt>
                                    <dd>
                                      {String(value ?? "")}
                                    </dd>
                                  </div>
                                ))}
                              </dl>
                            </details>
                          )}
                        </div>

                        <button
                          className="history-delete"
                          onClick={() =>
                            deleteHistoryEntry(entry.id)
                          }
                          aria-label="Delete assessment"
                          title="Delete assessment"
                        >
                          <Trash2 size={17} />
                        </button>
                      </article>
                    ))}
                  </div>

                  <button
                    className="secondary-button"
                    onClick={clearHistory}
                  >
                    Clear assessment history
                  </button>
                </>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">
                    <CalendarDays size={28} />
                  </div>

                  <h2>No assessments saved yet</h2>

                  <p>
                    Completed questionnaire assessments will
                    appear here.
                  </p>

                  <button
                    className="primary-button"
                    onClick={() =>
                      navigate("Cycle Assessment")
                    }
                  >
                    Start assessment{" "}
                    <ArrowRight size={18} />
                  </button>
                </div>
              )}
            </section>
          )}

          {activePage === "Period Tracker" && (
            <PeriodTracker />
          )}

          {activePage === "Settings" && (
            <section className="empty-state history-state">
              <div className="empty-icon">
                <Settings size={28} />
              </div>

              <h1>Settings</h1>

              <p>
                Questionnaire assessment history is stored in
                this browser. Period records are stored in the
                local SQLite database used by your backend.
              </p>

              <button
                className="secondary-button"
                onClick={() => navigate("Dashboard")}
              >
                Back to dashboard{" "}
                <ArrowRight size={17} />
              </button>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;