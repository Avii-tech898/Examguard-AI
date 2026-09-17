import { useEffect, useMemo, useState } from "react";

import {
  getAllAlerts,
  resolveDocumentAlert,
} from "../api/documentsApi";

import "../App.css";


function AlertManagement() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [statusFilter, setStatusFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");

  const [resolvingAlertId, setResolvingAlertId] = useState(null);


  // =====================================================
  // LOAD ALERTS
  // =====================================================

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getAllAlerts();

      setAlerts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load alerts:", err);

      if (err.response) {
        setError(
          `API Error: ${err.response.status} ${
            err.response.data?.detail || ""
          }`
        );
      } else {
        setError(
          "Unable to connect to EXAMGUARD-AI backend."
        );
      }
    } finally {
      setLoading(false);
    }
  };


  // =====================================================
  // INITIAL LOAD
  // =====================================================

  useEffect(() => {
    loadAlerts();
  }, []);


  // =====================================================
  // RESOLVE ALERT
  // =====================================================

  const handleResolve = async (alert) => {
    if (alert.status === "resolved") {
      return;
    }

    try {
      setResolvingAlertId(alert.id);
      setError("");

      await resolveDocumentAlert(
        alert.document_id,
        alert.id
      );

      await loadAlerts();
    } catch (err) {
      console.error("Failed to resolve alert:", err);

      if (err.response) {
        setError(
          `API Error: ${err.response.status} ${
            err.response.data?.detail || ""
          }`
        );
      } else {
        setError(
          "Unable to resolve the alert."
        );
      }
    } finally {
      setResolvingAlertId(null);
    }
  };


  // =====================================================
  // FILTER ALERTS
  // =====================================================

  const filteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      const statusMatch =
        statusFilter === "all" ||
        String(alert.status || "").toLowerCase() ===
          statusFilter;

      const severityMatch =
        severityFilter === "all" ||
        String(alert.severity || "").toLowerCase() ===
          severityFilter;

      return statusMatch && severityMatch;
    });
  }, [
    alerts,
    statusFilter,
    severityFilter,
  ]);


  // =====================================================
  // SUMMARY
  // =====================================================

  const totalAlerts = alerts.length;

  const openAlerts = alerts.filter(
    (alert) =>
      String(alert.status || "").toLowerCase() ===
      "open"
  ).length;

  const resolvedAlerts = alerts.filter(
    (alert) =>
      String(alert.status || "").toLowerCase() ===
      "resolved"
  ).length;

  const highRiskAlerts = alerts.filter((alert) => {
    const severity =
      String(alert.severity || "").toLowerCase();

    return (
      severity === "high" ||
      severity === "critical"
    );
  }).length;


  // =====================================================
  // DATE FORMAT
  // =====================================================

  const formatDate = (value) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString();
  };


  // =====================================================
  // RENDER
  // =====================================================

  return (
    <main className="main-content alert-management-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <section className="hero-section">
        <div>
          <h2>Security Alerts</h2>

          <p>
            Monitor examination security alerts,
            investigate suspicious activity, and
            resolve verified alerts.
          </p>
        </div>
      </section>


      {/* =================================================
          SUMMARY CARDS
      ================================================= */}

      <section className="alert-summary-grid">

        <div className="alert-summary-card">
          <span>Total Alerts</span>
          <strong>{totalAlerts}</strong>
          <small>All generated alerts</small>
        </div>


        <div className="alert-summary-card">
          <span>Open Alerts</span>
          <strong>{openAlerts}</strong>
          <small>Require attention</small>
        </div>


        <div className="alert-summary-card">
          <span>Resolved Alerts</span>
          <strong>{resolvedAlerts}</strong>
          <small>Successfully resolved</small>
        </div>


        <div className="alert-summary-card">
          <span>High Risk</span>
          <strong>{highRiskAlerts}</strong>
          <small>High or critical severity</small>
        </div>

      </section>


      {/* =================================================
          ALERT LIST
      ================================================= */}

      <section className="documents-section">

        <div className="section-header">

          <div>
            <h2>Alert Management</h2>

            <p className="section-subtitle">
              {filteredAlerts.length} alert
              {filteredAlerts.length !== 1 ? "s" : ""}
              {" "}shown
            </p>
          </div>


          <button
            type="button"
            className="secondary-button"
            onClick={loadAlerts}
            disabled={loading}
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>

        </div>


        {/* =================================================
            FILTERS
        ================================================= */}

        <div className="alert-filters">

          <div className="alert-filter-group">
            <label htmlFor="status-filter">
              Status
            </label>

            <select
              id="status-filter"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value)
              }
            >
              <option value="all">All Status</option>
              <option value="open">Open</option>
              <option value="resolved">
                Resolved
              </option>
            </select>
          </div>


          <div className="alert-filter-group">
            <label htmlFor="severity-filter">
              Severity
            </label>

            <select
              id="severity-filter"
              value={severityFilter}
              onChange={(event) =>
                setSeverityFilter(event.target.value)
              }
            >
              <option value="all">
                All Severity
              </option>

              <option value="low">Low</option>

              <option value="medium">
                Medium
              </option>

              <option value="high">High</option>

              <option value="critical">
                Critical
              </option>
            </select>
          </div>

        </div>


        {/* =================================================
            LOADING
        ================================================= */}

        {loading && (
          <div className="state-message">
            Loading security alerts...
          </div>
        )}


        {/* =================================================
            ERROR
        ================================================= */}

        {!loading && error && (
          <div className="error-message">
            {error}
          </div>
        )}


        {/* =================================================
            EMPTY
        ================================================= */}

        {!loading &&
          !error &&
          filteredAlerts.length === 0 && (
            <div className="state-message">
              No alerts match the selected filters.
            </div>
          )}


        {/* =================================================
            ALERT TABLE
        ================================================= */}

        {!loading &&
          !error &&
          filteredAlerts.length > 0 && (

            <div className="alerts-table-wrapper">

              <table className="alerts-table">

                <thead>
                  <tr>
                    <th>Alert</th>
                    <th>Document</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Risk Score</th>
                    <th>Created</th>
                    <th>Action</th>
                  </tr>
                </thead>


                <tbody>

                  {filteredAlerts.map((alert) => {

                    const severity =
                      String(
                        alert.severity || "low"
                      ).toLowerCase();

                    const status =
                      String(
                        alert.status || "open"
                      ).toLowerCase();


                    return (
                      <tr key={alert.id}>

                        {/* ALERT */}

                        <td>
                          <div className="alert-title-cell">

                            <strong>
                              #{alert.id}
                            </strong>

                            <span>
                              {alert.alert_type ||
                                "Security Alert"}
                            </span>

                            {alert.message && (
                              <small>
                                {alert.message}
                              </small>
                            )}

                          </div>
                        </td>


                        {/* DOCUMENT */}

                        <td>
                          <span className="document-id-badge">
                            DOC-{alert.document_id}
                          </span>
                        </td>


                        {/* SEVERITY */}

                        <td>
                          <span
                            className={`alert-severity-badge ${severity}`}
                          >
                            <span
                              className={`alert-severity-dot ${severity}`}
                            />

                            {severity}
                          </span>
                        </td>


                        {/* STATUS */}

                        <td>
                          <span
                            className={`alert-status-badge ${status}`}
                          >
                            {status}
                          </span>
                        </td>


                        {/* RISK SCORE ID */}

                        <td>
                          {alert.risk_score_id
                            ? `#${alert.risk_score_id}`
                            : "—"}
                        </td>


                        {/* CREATED */}

                        <td>
                          <span className="alert-date">
                            {formatDate(
                              alert.created_at
                            )}
                          </span>
                        </td>


                        {/* ACTION */}

                        <td>

                          {status === "resolved" ? (

                            <span className="resolved-label">
                              ✓ Resolved
                            </span>

                          ) : (

                            <button
                              type="button"
                              className="resolve-alert-button"
                              onClick={() =>
                                handleResolve(alert)
                              }
                              disabled={
                                resolvingAlertId ===
                                alert.id
                              }
                            >
                              {resolvingAlertId ===
                              alert.id
                                ? "Resolving..."
                                : "Resolve"}
                            </button>

                          )}

                        </td>

                      </tr>
                    );
                  })}

                </tbody>

              </table>

            </div>

          )}

      </section>

    </main>
  );
}


export default AlertManagement;