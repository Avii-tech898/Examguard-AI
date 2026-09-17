import { useEffect, useState } from "react";

import {
  getDocuments,
  getAnalyticsOverview,
  uploadDocument,
  getBackendHealth,
} from "./api/documentsApi";

import DocumentCard from "./components/DocumentCard";
import DocumentDetails from "./pages/DocumentDetails";
import AlertManagement from "./pages/AlertManagement";

import "./App.css";

function App() {
  // =====================================================
  // DOCUMENT STATE
  // =====================================================

  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // =====================================================
  // UPLOAD STATE
  // =====================================================

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");

  // =====================================================
  // ANALYTICS STATE
  // =====================================================

  const [analytics, setAnalytics] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [analyticsError, setAnalyticsError] = useState("");

  // =====================================================
  // ALERT PAGE STATE
  // =====================================================

  const [showAlerts, setShowAlerts] = useState(false);

  // =====================================================
  // BACKEND HEALTH STATE
  // =====================================================

  const [backendOnline, setBackendOnline] = useState(false);
  const [backendChecking, setBackendChecking] = useState(true);

  // =====================================================
  // LOAD DOCUMENTS
  // =====================================================

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDocuments();

      setDocuments(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load documents:", err);

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
  // LOAD ANALYTICS
  // =====================================================

  const loadAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      setAnalyticsError("");

      const data = await getAnalyticsOverview();

      setAnalytics(data);
    } catch (err) {
      console.error("Failed to load analytics:", err);

      if (err.response) {
        setAnalyticsError(
          `Analytics API Error: ${err.response.status} ${
            err.response.data?.detail || ""
          }`
        );
      } else {
        setAnalyticsError(
          "Unable to load security analytics."
        );
      }
    } finally {
      setAnalyticsLoading(false);
    }
  };

  // =====================================================
  // BACKEND HEALTH CHECK
  // =====================================================

  const checkBackendHealth = async () => {
    try {
      setBackendChecking(true);

      const response = await getBackendHealth();

      setBackendOnline(
        response?.status === "healthy"
      );
    } catch (err) {
      console.error(
        "Backend health check failed:",
        err
      );

      setBackendOnline(false);
    } finally {
      setBackendChecking(false);
    }
  };

  // =====================================================
  // INITIAL LOAD
  // =====================================================

  useEffect(() => {
    loadDocuments();
    loadAnalytics();
    checkBackendHealth();
  }, []);

  // =====================================================
  // DOCUMENT UPLOAD
  // =====================================================

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploadError("");
    setUploadMessage("");
    setUploading(true);

    try {
      const uploadedDocument = await uploadDocument(file);

      setUploadMessage(
        `"${uploadedDocument.file_name}" uploaded successfully.`
      );

      await loadDocuments();
      await loadAnalytics();
      await checkBackendHealth();
    } catch (err) {
      console.error("Document upload failed:", err);

      if (err.response) {
        setUploadError(
          err.response.data?.detail ||
            `Upload failed with status ${err.response.status}`
        );
      } else {
        setUploadError(
          "Unable to upload document. Check backend connection."
        );
      }
    } finally {
      setUploading(false);

      // Allow same file to be selected again
      event.target.value = "";
    }
  };

  // =====================================================
  // DOCUMENT NAVIGATION
  // =====================================================

  const handleViewDetails = (document) => {
    setShowAlerts(false);
    setSelectedDocument(document);
  };

  const handleBack = () => {
    setSelectedDocument(null);

    // Refresh dashboard values after processing
    loadDocuments();
    loadAnalytics();
    checkBackendHealth();
  };

  // =====================================================
  // ALERT NAVIGATION
  // =====================================================

  const handleShowAlerts = () => {
    setSelectedDocument(null);
    setShowAlerts(true);
  };

  const handleBackToDashboard = () => {
    setShowAlerts(false);

    loadDocuments();
    loadAnalytics();
    checkBackendHealth();
  };

  // =====================================================
  // BACKEND STATUS UI
  // =====================================================

  const backendStatusText = backendChecking
    ? "Checking Backend..."
    : backendOnline
      ? "Backend Connected"
      : "Backend Offline";

  // =====================================================
  // DOCUMENT DETAILS PAGE
  // =====================================================

  if (selectedDocument) {
    return (
      <div className="app">
        <header className="header">
          <div>
            <h1>EXAMGUARD-AI</h1>

            <p>
              AI-Powered Examination Security Platform
            </p>
          </div>

          <div
            className={`backend-status ${
              backendOnline ? "online" : "offline"
            }`}
          >
            <span className="status-dot"></span>
            {backendStatusText}
          </div>
        </header>

        <DocumentDetails
          document={selectedDocument}
          documents={documents}
          onBack={handleBack}
        />
      </div>
    );
  }

  // =====================================================
  // ALERT MANAGEMENT PAGE
  // =====================================================

  if (showAlerts) {
    return (
      <div className="app">
        <header className="header">
          <div>
            <h1>EXAMGUARD-AI</h1>

            <p>
              AI-Powered Examination Security Platform
            </p>
          </div>

          <div
            className={`backend-status ${
              backendOnline ? "online" : "offline"
            }`}
          >
            <span className="status-dot"></span>
            {backendStatusText}
          </div>
        </header>

        <div className="page-navigation">
          <button
            type="button"
            className="secondary-button"
            onClick={handleBackToDashboard}
          >
            ← Dashboard
          </button>
        </div>

        <AlertManagement />
      </div>
    );
  }

  // =====================================================
  // MAIN DASHBOARD
  // =====================================================

  return (
    <div className="app">
      {/* =================================================
          HEADER
      ================================================= */}

      <header className="header">
        <div>
          <h1>EXAMGUARD-AI</h1>

          <p>
            AI-Powered Examination Security Platform
          </p>
        </div>

        <div
          className={`backend-status ${
            backendOnline ? "online" : "offline"
          }`}
        >
          <span className="status-dot"></span>
          {backendStatusText}
        </div>
      </header>

      <main className="main-content">
        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero-section">
          <div className="hero-content">
            <div>
              <h2>
                Document Security Dashboard
              </h2>

              <p>
                Manage uploaded examination documents
                and analyze security-related results.
              </p>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={handleShowAlerts}
            >
              🛡️ Security Alerts
            </button>
          </div>
        </section>

        {/* =================================================
            DOCUMENT UPLOAD
        ================================================= */}

        <section className="upload-section">
          <div className="upload-header">
            <div>
              <h2>
                Upload Examination Document
              </h2>

              <p>
                Upload a document for EXAMGUARD-AI
                security processing.
              </p>
            </div>

            <label
              htmlFor="document-upload"
              className={
                uploading
                  ? "upload-button disabled"
                  : "upload-button"
              }
            >
              {uploading
                ? "Uploading..."
                : "📤 Choose Document"}

              <input
                id="document-upload"
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleUpload}
                disabled={uploading}
                hidden
              />
            </label>
          </div>

          {uploadMessage && (
            <div className="upload-success">
              ✓ {uploadMessage}
            </div>
          )}

          {uploadError && (
            <div className="upload-error">
              {uploadError}
            </div>
          )}
        </section>

        {/* =================================================
            SECURITY OVERVIEW
        ================================================= */}

        <section className="analytics-section">
          <div className="section-header">
            <div>
              <h2>
                Security Overview
              </h2>

              <p className="analytics-subtitle">
                Live examination security analytics
              </p>
            </div>

            <span className="analytics-live-badge">
              <span className="analytics-live-dot"></span>
              LIVE
            </span>
          </div>

          {/* =================================================
              ANALYTICS LOADING
          ================================================= */}

          {analyticsLoading && (
            <div className="state-message">
              Loading security analytics...
            </div>
          )}

          {/* =================================================
              ANALYTICS ERROR
          ================================================= */}

          {!analyticsLoading && analyticsError && (
            <div className="error-message">
              {analyticsError}
            </div>
          )}

          {/* =================================================
              ANALYTICS DATA
          ================================================= */}

          {!analyticsLoading &&
            !analyticsError &&
            analytics && (
              <>
                {/* =================================================
                    TOP ANALYTICS CARDS
                ================================================= */}

                <div className="analytics-grid">
                  {/* TOTAL DOCUMENTS */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Total Documents
                      </span>

                      <span className="analytics-card-icon">
                        📄
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {analytics.total_documents ?? 0}
                    </strong>

                    <span className="analytics-card-description">
                      Uploaded examination documents
                    </span>
                  </div>

                  {/* ANALYZED DOCUMENTS */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Analyzed Documents
                      </span>

                      <span className="analytics-card-icon">
                        🔍
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {analytics.analyzed_documents ?? 0}
                    </strong>

                    <span className="analytics-card-description">
                      Documents processed by NLP
                    </span>
                  </div>

                  {/* AVG SIMILARITY */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Avg Similarity
                      </span>

                      <span className="analytics-card-icon">
                        📊
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {Number(
                        analytics.average_similarity ?? 0
                      ).toFixed(2)}
                      %
                    </strong>

                    <span className="analytics-card-description">
                      Average document similarity
                    </span>
                  </div>

                  {/* OPEN ALERTS */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Open Alerts
                      </span>

                      <span className="analytics-card-icon">
                        🚨
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {analytics.open_alerts ?? 0}
                    </strong>

                    <span className="analytics-card-description">
                      Active security alerts
                    </span>
                  </div>
                </div>

                {/* =================================================
                    EXTENDED ANALYTICS
                ================================================= */}

                <div className="analytics-grid">
                  {/* AVERAGE RISK SCORE */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Average Risk Score
                      </span>

                      <span className="analytics-card-icon">
                        ⚠️
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {Number(
                        analytics.average_risk_score ?? 0
                      ).toFixed(2)}
                    </strong>

                    <span className="analytics-card-description">
                      Average risk across analyzed documents
                    </span>
                  </div>

                  {/* SIMILARITY COMPARISONS */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Similarity Comparisons
                      </span>

                      <span className="analytics-card-icon">
                        🔎
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {analytics.similarity_comparisons ?? 0}
                    </strong>

                    <span className="analytics-card-description">
                      Total document comparisons
                    </span>
                  </div>

                  {/* PROCESSING RATE */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Processing Rate
                      </span>

                      <span className="analytics-card-icon">
                        ⚙️
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {Number(
                        analytics.processing_rate ?? 0
                      ).toFixed(2)}
                      %
                    </strong>

                    <span className="analytics-card-description">
                      Documents successfully processed
                    </span>
                  </div>

                  {/* ANALYTICS STATUS */}

                  <div className="analytics-card">
                    <div className="analytics-card-top">
                      <span className="analytics-card-label">
                        Analytics Status
                      </span>

                      <span className="analytics-card-icon">
                        🟢
                      </span>
                    </div>

                    <strong className="analytics-card-value">
                      {String(
                        analytics.analytics_status ?? "unknown"
                      ).toUpperCase()}
                    </strong>

                    <span className="analytics-card-description">
                      Live analytics service status
                    </span>
                  </div>
                </div>

                {/* =================================================
                    LOWER ANALYTICS
                ================================================= */}

                <div className="analytics-lower-grid">
                  {/* =================================================
                      RISK DISTRIBUTION
                  ================================================= */}

                  <div className="risk-distribution-card">
                    <div className="analytics-panel-header">
                      <div>
                        <h3>
                          Risk Distribution
                        </h3>

                        <p>
                          Latest risk level per document
                        </p>
                      </div>
                    </div>

                    <div className="risk-distribution-list">
                      {/* LOW */}

                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot low"></span>

                          <span>
                            Low
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.risk_distribution
                              ?.low ?? 0
                          }
                        </strong>
                      </div>

                      {/* MEDIUM */}

                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot medium"></span>

                          <span>
                            Medium
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.risk_distribution
                              ?.medium ?? 0
                          }
                        </strong>
                      </div>

                      {/* HIGH */}

                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot high"></span>

                          <span>
                            High
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.risk_distribution
                              ?.high ?? 0
                          }
                        </strong>
                      </div>

                      {/* CRITICAL */}

                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot critical"></span>

                          <span>
                            Critical
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.risk_distribution
                              ?.critical ?? 0
                          }
                        </strong>
                      </div>
                    </div>
                  </div>

                  {/* =================================================
                      SECURITY STATUS
                  ================================================= */}

                  <div className="security-status-card">
                    <div className="analytics-panel-header">
                      <div>
                        <h3>
                          Security Status
                        </h3>

                        <p>
                          Current platform assessment
                        </p>
                      </div>
                    </div>

                    <div className="security-status-main">
                      <div className="security-status-icon">
                        🛡️
                      </div>

                      <div>
                        <strong>
                          Monitoring Active
                        </strong>

                        <p>
                          EXAMGUARD-AI is actively
                          monitoring uploaded documents.
                        </p>
                      </div>
                    </div>

                    <div className="security-stat-list">
                      <div>
                        <span>
                          Similarity Comparisons
                        </span>

                        <strong>
                          {
                            analytics.similarity_comparisons
                              ?? 0
                          }
                        </strong>
                      </div>

                      <div>
                        <span>
                          High Risk Documents
                        </span>

                        <strong>
                          {
                            analytics.high_risk_documents
                              ?? 0
                          }
                        </strong>
                      </div>

                      <div>
                        <span>
                          Critical Documents
                        </span>

                        <strong>
                          {
                            analytics.critical_risk_documents
                              ?? 0
                          }
                        </strong>
                      </div>

                      <div>
                        <span>
                          Processing Rate
                        </span>

                        <strong>
                          {Number(
                            analytics.processing_rate ?? 0
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>

                {/* =================================================
                    ALERT DISTRIBUTION
                ================================================= */}

                <div className="analytics-lower-grid">
                  <div className="risk-distribution-card">
                    <div className="analytics-panel-header">
                      <div>
                        <h3>
                          Alert Distribution
                        </h3>

                        <p>
                          Current security alert status
                        </p>
                      </div>
                    </div>

                    <div className="risk-distribution-list">
                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot medium"></span>

                          <span>
                            Open Alerts
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.alert_distribution
                              ?.open ??
                            analytics.open_alerts ??
                            0
                          }
                        </strong>
                      </div>

                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot low"></span>

                          <span>
                            Resolved Alerts
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.alert_distribution
                              ?.resolved ?? 0
                          }
                        </strong>
                      </div>

                      <div className="risk-row">
                        <div className="risk-row-label">
                          <span className="risk-dot high"></span>

                          <span>
                            Total Alerts
                          </span>
                        </div>

                        <strong>
                          {
                            analytics.alert_distribution
                              ?.total ?? 0
                          }
                        </strong>
                      </div>
                    </div>
                  </div>

                  {/* PLATFORM HEALTH */}

                  <div className="security-status-card">
                    <div className="analytics-panel-header">
                      <div>
                        <h3>
                          Platform Health
                        </h3>

                        <p>
                          EXAMGUARD-AI monitoring status
                        </p>
                      </div>
                    </div>

                    <div className="security-status-main">
                      <div className="security-status-icon">
                        🟢
                      </div>

                      <div>
                        <strong>
                          Analytics Active
                        </strong>

                        <p>
                          Live security analytics are
                          connected to the database.
                        </p>
                      </div>
                    </div>

                    <div className="security-stat-list">
                      <div>
                        <span>
                          Analytics Status
                        </span>

                        <strong>
                          {String(
                            analytics.analytics_status ??
                              "unknown"
                          ).toUpperCase()}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Average Risk Score
                        </span>

                        <strong>
                          {Number(
                            analytics.average_risk_score ?? 0
                          ).toFixed(2)}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Open Alerts
                        </span>

                        <strong>
                          {analytics.open_alerts ?? 0}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Processing Rate
                        </span>

                        <strong>
                          {Number(
                            analytics.processing_rate ?? 0
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
        </section>

        {/* =================================================
            DOCUMENTS
        ================================================= */}

        <section className="documents-section">
          <div className="section-header">
            <h2>
              Uploaded Documents
            </h2>

            <span className="document-count">
              {documents.length} Documents
            </span>
          </div>

          {/* LOADING */}

          {loading && (
            <div className="state-message">
              Loading documents...
            </div>
          )}

          {/* ERROR */}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* EMPTY */}

          {!loading &&
            !error &&
            documents.length === 0 && (
              <div className="state-message">
                No documents found.
              </div>
            )}

          {/* DOCUMENT LIST */}

          {!loading &&
            !error &&
            documents.length > 0 && (
              <div className="document-grid">
                {documents.map((document) => (
                  <DocumentCard
                    key={document.id}
                    document={document}
                    onViewDetails={handleViewDetails}
                  />
                ))}
              </div>
            )}
        </section>
      </main>
    </div>
  );
}

export default App;