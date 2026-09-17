import { useEffect, useMemo, useState } from "react";

import {
  getDocuments,
  getDocumentText,
  getDocumentAnalysis,
  getDocumentSimilarity,
  calculateDocumentSimilarity,
  getDocumentRiskV1,
  getDocumentRiskV2,
  calculateDocumentRisk,
  calculateDocumentRiskV2,
  getDocumentAlerts,
  createDocumentAlert,
  processDocumentPair,
} from "../api/documentsApi";

// =====================================================
// HELPERS
// =====================================================

const getErrorMessage = (error, fallback) => {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    fallback
  );
};

// -----------------------------------------------------
// DISPLAY FILE NAME
// -----------------------------------------------------

const getDisplayFileName = (fileName) => {
  if (!fileName) {
    return "Untitled Document";
  }

  try {
    return decodeURIComponent(fileName);
  } catch {
    return fileName;
  }
};

// -----------------------------------------------------
// NORMALIZE SIMILARITY
// -----------------------------------------------------

const normalizeSimilarity = (data) => {
  if (!data) {
    return null;
  }

  return {
    ...data,

    similarity_score:
      data.similarity_score ??
      data.score ??
      null,

    similarity_method:
      data.similarity_method ??
      data.method ??
      null,

    document_id:
      data.document_id ??
      data.document?.id ??
      null,

    compared_document_id:
      data.compared_document_id ??
      data.compared_document?.id ??
      null,

    matching_sections:
      Array.isArray(data.matching_sections)
        ? data.matching_sections
        : [],
  };
};

// -----------------------------------------------------
// NORMALIZE RISK V1
// -----------------------------------------------------

const normalizeRisk = (data) => {
  if (!data) {
    return null;
  }

  return {
    ...data,

    id: data.id ?? null,

    risk_score:
      data.risk_score ??
      data.score ??
      null,

    risk_level:
      data.risk_level ??
      data.level ??
      null,

    model_version:
      data.model_version ??
      data.model ??
      null,

    risk_factors:
      Array.isArray(data.risk_factors)
        ? data.risk_factors
        : [],
  };
};

// -----------------------------------------------------
// NORMALIZE RISK V2
// -----------------------------------------------------

const normalizeRiskV2 = (data) => {
  if (!data) {
    return null;
  }

  const features =
    data.features ??
    data.feature_snapshot ??
    null;

  let riskFactors = Array.isArray(data.risk_factors)
    ? data.risk_factors
    : [];

  /*
   * Backend processing endpoint returns:
   *
   * risk_v2: {
   *   id,
   *   score,
   *   level,
   *   model,
   *   features
   * }
   *
   * Convert features into the same structure
   * used by GET /risk-v2.
   */

  if (
    features &&
    !riskFactors.some(
      (factor) =>
        factor &&
        typeof factor === "object" &&
        factor.feature_snapshot
    )
  ) {
    riskFactors = [
      ...riskFactors,
      {
        feature_snapshot: features,
      },
    ];
  }

  return {
    ...data,

    id: data.id ?? null,

    risk_score:
      data.risk_score ??
      data.score ??
      null,

    risk_level:
      data.risk_level ??
      data.level ??
      null,

    model_version:
      data.model_version ??
      data.model ??
      null,

    risk_factors: riskFactors,
  };
};

// -----------------------------------------------------
// NORMALIZE ALERT
// -----------------------------------------------------

const normalizeAlert = (data) => {
  if (!data) {
    return null;
  }

  return {
    ...data,

    id: data.id ?? null,

    document_id:
      data.document_id ??
      data.document?.id ??
      null,

    risk_score_id:
      data.risk_score_id ??
      null,

    alert_type:
      data.alert_type ??
      data.type ??
      null,

    severity:
      data.severity ??
      null,

    status:
      data.status ??
      null,

    message:
      data.message ??
      null,

    created_at:
      data.created_at ??
      null,

    resolved_at:
      data.resolved_at ??
      null,
  };
};

// =====================================================
// COMPONENT
// =====================================================

function DocumentDetails({
  document,
  documents = [],
  onBack,
}) {
  // =====================================================
  // STATE
  // =====================================================

  const [documentList, setDocumentList] =
    useState(documents || []);

  const [textData, setTextData] =
    useState(null);

  const [analysisData, setAnalysisData] =
    useState(null);

  const [similarityData, setSimilarityData] =
    useState(null);

  const [riskData, setRiskData] =
    useState(null);

  const [riskV2Data, setRiskV2Data] =
    useState(null);

  const [activeRisk, setActiveRisk] =
    useState(null);

  const [alertsData, setAlertsData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [actionLoading, setActionLoading] =
    useState("");

  const [error, setError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const [comparedDocumentId, setComparedDocumentId] =
    useState("");

  // =====================================================
  // COMPARISON DOCUMENTS
  // =====================================================

  const comparisonDocuments = useMemo(() => {
    if (!Array.isArray(documentList)) {
      return [];
    }

    return documentList.filter(
      (item) =>
        Number(item?.id) !==
        Number(document?.id)
    );
  }, [documentList, document?.id]);

  // =====================================================
  // V2 FEATURE SNAPSHOT
  // =====================================================

  const featureSnapshot = useMemo(() => {
    if (
      !Array.isArray(
        riskV2Data?.risk_factors
      )
    ) {
      return null;
    }

    const snapshotFactor =
      riskV2Data.risk_factors.find(
        (factor) =>
          factor &&
          typeof factor === "object" &&
          factor.feature_snapshot
      );

    return (
      snapshotFactor?.feature_snapshot ||
      null
    );
  }, [riskV2Data]);

  // =====================================================
  // V2 TEXTUAL RISK FACTORS
  // =====================================================

  const riskV2Factors = useMemo(() => {
    if (
      !Array.isArray(
        riskV2Data?.risk_factors
      )
    ) {
      return [];
    }

    return riskV2Data.risk_factors.filter(
      (factor) =>
        typeof factor === "string"
    );
  }, [riskV2Data]);

  // =====================================================
  // SYNC DOCUMENT LIST
  // =====================================================

  useEffect(() => {
    setDocumentList(
      Array.isArray(documents)
        ? documents
        : []
    );
  }, [documents]);

  // =====================================================
  // LOAD DOCUMENTS FOR COMPARISON
  // =====================================================

  useEffect(() => {
    let cancelled = false;

    const loadDocumentsForComparison =
      async () => {
        if (
          !document?.id ||
          documentList.length > 0
        ) {
          return;
        }

        try {
          const result =
            await getDocuments();

          if (
            !cancelled &&
            Array.isArray(result)
          ) {
            setDocumentList(result);
          }
        } catch (err) {
          console.error(
            "Failed to load documents for comparison:",
            err
          );
        }
      };

    loadDocumentsForComparison();

    return () => {
      cancelled = true;
    };
  }, [
    document?.id,
    documentList.length,
  ]);

  // =====================================================
  // SELECT FIRST COMPARISON DOCUMENT
  // =====================================================

  useEffect(() => {
    if (!document?.id) {
      setComparedDocumentId("");
      return;
    }

    if (
      comparisonDocuments.length === 0
    ) {
      setComparedDocumentId("");
      return;
    }

    const currentComparisonExists =
      comparisonDocuments.some(
        (item) =>
          String(item.id) ===
          String(comparedDocumentId)
      );

    if (!currentComparisonExists) {
      setComparedDocumentId(
        String(
          comparisonDocuments[0].id
        )
      );
    }
  }, [
    document?.id,
    comparisonDocuments,
    comparedDocumentId,
  ]);

  // =====================================================
  // LOAD DOCUMENT DETAILS
  // =====================================================

  useEffect(() => {
    let cancelled = false;

    const loadDocumentDetails =
      async () => {
        if (!document?.id) {
          setLoading(false);
          return;
        }

        try {
          setLoading(true);
          setError("");
          setSuccessMessage("");

          setTextData(null);
          setAnalysisData(null);
          setSimilarityData(null);

          setRiskData(null);
          setRiskV2Data(null);
          setActiveRisk(null);

          setAlertsData(null);

          const results =
            await Promise.allSettled([
              getDocumentText(
                document.id
              ),

              getDocumentAnalysis(
                document.id
              ),

              getDocumentRiskV1(
                document.id
              ),

              getDocumentRiskV2(
                document.id
              ),

              getDocumentAlerts(
                document.id
              ),
            ]);

          if (cancelled) {
            return;
          }

          const [
            textResult,
            analysisResult,
            riskV1Result,
            riskV2Result,
            alertsResult,
          ] = results;

          // -------------------------------------------------
          // TEXT
          // -------------------------------------------------

          if (
            textResult.status ===
            "fulfilled"
          ) {
            setTextData(
              textResult.value
            );
          }

          // -------------------------------------------------
          // NLP
          // -------------------------------------------------

          if (
            analysisResult.status ===
            "fulfilled"
          ) {
            setAnalysisData(
              analysisResult.value
            );
          }

          // -------------------------------------------------
          // RISK V1
          // -------------------------------------------------

          if (
            riskV1Result.status ===
            "fulfilled"
          ) {
            const normalized =
              normalizeRisk(
                riskV1Result.value
              );

            setRiskData(normalized);
          }

          // -------------------------------------------------
          // RISK V2
          // -------------------------------------------------

          if (
            riskV2Result.status ===
            "fulfilled"
          ) {
            const normalized =
              normalizeRiskV2(
                riskV2Result.value
              );

            setRiskV2Data(normalized);

            setActiveRisk(
              normalized
            );
          } else if (
            riskV1Result.status ===
            "fulfilled"
          ) {
            const normalized =
              normalizeRisk(
                riskV1Result.value
              );

            setActiveRisk(
              normalized
            );
          }

          // -------------------------------------------------
          // ALERT
          // -------------------------------------------------

          if (
            alertsResult.status ===
            "fulfilled"
          ) {
            setAlertsData(
              normalizeAlert(
                alertsResult.value
              )
            );
          }
        } catch (err) {
          console.error(
            "Failed to load document details:",
            err
          );

          if (!cancelled) {
            setError(
              getErrorMessage(
                err,
                "Unable to load document details."
              )
            );
          }
        } finally {
          if (!cancelled) {
            setLoading(false);
          }
        }
      };

    loadDocumentDetails();

    return () => {
      cancelled = true;
    };
  }, [document?.id]);

  // =====================================================
  // LOAD EXISTING SIMILARITY
  // =====================================================

  useEffect(() => {
    let cancelled = false;

    const loadSimilarity =
      async () => {
        if (
          !document?.id ||
          !comparedDocumentId
        ) {
          setSimilarityData(null);
          return;
        }

        try {
          const result =
            await getDocumentSimilarity(
              document.id,
              Number(comparedDocumentId)
            );

          if (!cancelled) {
            setSimilarityData(
              normalizeSimilarity(result)
            );
          }

          return;
        } catch (err) {
          // -------------------------------------------------
          // REVERSE LOOKUP
          // -------------------------------------------------

          if (
            err?.response?.status ===
            404
          ) {
            try {
              const reverseResult =
                await getDocumentSimilarity(
                  Number(
                    comparedDocumentId
                  ),
                  document.id
                );

              if (!cancelled) {
                setSimilarityData(
                  normalizeSimilarity({
                    ...reverseResult,

                    document_id:
                      document.id,

                    compared_document_id:
                      Number(
                        comparedDocumentId
                      ),
                  })
                );
              }

              return;
            } catch (
              reverseError
            ) {
              if (
                reverseError?.response
                  ?.status !== 404
              ) {
                console.error(
                  "Failed to load reverse similarity:",
                  reverseError
                );
              }
            }
          } else {
            console.error(
              "Failed to load similarity:",
              err
            );
          }
        }

        if (!cancelled) {
          setSimilarityData(null);
        }
      };

    loadSimilarity();

    return () => {
      cancelled = true;
    };
  }, [
    document?.id,
    comparedDocumentId,
  ]);

  // =====================================================
  // MESSAGE HELPERS
  // =====================================================

  const clearMessages = () => {
    setError("");
    setSuccessMessage("");
  };

  // =====================================================
  // REFRESH RESULTS
  // =====================================================

  const refreshResults = async () => {
    if (!document?.id) {
      return;
    }

    const results =
      await Promise.allSettled([
        getDocumentText(
          document.id
        ),

        getDocumentAnalysis(
          document.id
        ),

        getDocumentRiskV1(
          document.id
        ),

        getDocumentRiskV2(
          document.id
        ),

        getDocumentAlerts(
          document.id
        ),
      ]);

    // TEXT

    if (
      results[0].status ===
      "fulfilled"
    ) {
      setTextData(
        results[0].value
      );
    }

    // NLP

    if (
      results[1].status ===
      "fulfilled"
    ) {
      setAnalysisData(
        results[1].value
      );
    }

    // V1

    if (
      results[2].status ===
      "fulfilled"
    ) {
      setRiskData(
        normalizeRisk(
          results[2].value
        )
      );
    }

    // V2

    if (
      results[3].status ===
      "fulfilled"
    ) {
      const normalized =
        normalizeRiskV2(
          results[3].value
        );

      setRiskV2Data(
        normalized
      );

      setActiveRisk(
        normalized
      );
    } else if (
      results[2].status ===
      "fulfilled"
    ) {
      setActiveRisk(
        normalizeRisk(
          results[2].value
        )
      );
    }

    // ALERT

    if (
      results[4].status ===
      "fulfilled"
    ) {
      setAlertsData(
        normalizeAlert(
          results[4].value
        )
      );
    }
  };

  // =====================================================
  // COMPARISON CHANGE
  // =====================================================

  const handleComparisonChange = (
    event
  ) => {
    const value =
      event.target.value;

    setComparedDocumentId(
      value
    );

    setSimilarityData(null);

    setRiskData(null);
    setRiskV2Data(null);
    setActiveRisk(null);

    setAlertsData(null);

    clearMessages();
  };

  // =====================================================
  // FULL SECURITY ANALYSIS
  // =====================================================

  const handleFullSecurityAnalysis =
    async () => {
      if (
        !document?.id ||
        !comparedDocumentId
      ) {
        setError(
          "Please select a document comparison before running full security analysis."
        );

        return;
      }

      try {
        clearMessages();

        setActionLoading(
          "full-analysis"
        );

        const result =
          await processDocumentPair(
            document.id,
            Number(
              comparedDocumentId
            )
          );

        // -------------------------------------------------
        // SIMILARITY
        // -------------------------------------------------

        if (result?.similarity) {
          setSimilarityData(
            normalizeSimilarity({
              similarity_score:
                result.similarity
                  .score,

              similarity_method:
                result.similarity
                  .method,

              document_id:
                result.document?.id ??
                document.id,

              compared_document_id:
                result.compared_document
                  ?.id ??
                Number(
                  comparedDocumentId
                ),

              matching_sections:
                result.similarity
                  .matching_sections ||
                [],
            })
          );
        }

        // -------------------------------------------------
        // RISK V1
        // -------------------------------------------------

        if (result?.risk_v1) {
          const normalizedV1 =
            normalizeRisk({
              id:
                result.risk_v1.id,

              risk_score:
                result.risk_v1.score,

              risk_level:
                result.risk_v1.level,

              model_version:
                result.risk_v1.model,

              risk_factors: [],
            });

          setRiskData(
            normalizedV1
          );
        }

        // -------------------------------------------------
        // RISK V2
        // -------------------------------------------------

        if (result?.risk_v2) {
          const normalizedV2 =
            normalizeRiskV2({
              id:
                result.risk_v2.id,

              risk_score:
                result.risk_v2.score,

              risk_level:
                result.risk_v2.level,

              model_version:
                result.risk_v2.model,

              features:
                result.risk_v2
                  .features,

              risk_factors: [],
            });

          setRiskV2Data(
            normalizedV2
          );

          setActiveRisk(
            normalizedV2
          );
        } else if (
          result?.risk_v1
        ) {
          setActiveRisk(
            normalizeRisk({
              id:
                result.risk_v1.id,

              risk_score:
                result.risk_v1.score,

              risk_level:
                result.risk_v1.level,

              model_version:
                result.risk_v1.model,

              risk_factors: [],
            })
          );
        }

        // -------------------------------------------------
        // ALERT
        // -------------------------------------------------

        if (result?.alert) {
          setAlertsData(
            normalizeAlert({
              ...result.alert,

              document_id:
                result.document?.id ??
                document.id,

              risk_score_id:
                result.risk_v2?.id ??
                result.risk_v1?.id ??
                null,
            })
          );
        }

        // -------------------------------------------------
        // REFRESH DATABASE RESULTS
        // -------------------------------------------------

        await refreshResults();

        setSuccessMessage(
          "Full security analysis completed successfully."
        );
      } catch (err) {
        console.error(
          "Full security analysis failed:",
          err
        );

        setError(
          getErrorMessage(
            err,
            "Full security analysis failed."
          )
        );
      } finally {
        setActionLoading("");
      }
    };

  // =====================================================
  // CALCULATE SIMILARITY
  // =====================================================

  const handleCalculateSimilarity =
    async () => {
      if (
        !document?.id ||
        !comparedDocumentId
      ) {
        setError(
          "Please select a document to compare."
        );

        return;
      }

      try {
        clearMessages();

        setActionLoading(
          "similarity"
        );

        const result =
          await calculateDocumentSimilarity(
            document.id,
            Number(
              comparedDocumentId
            )
          );

        setSimilarityData(
          normalizeSimilarity(
            result
          )
        );

        /*
         * Similarity is the prerequisite
         * for generating risk.
         */

        setRiskData(null);
        setRiskV2Data(null);
        setActiveRisk(null);
        setAlertsData(null);

        setSuccessMessage(
          "Similarity analysis calculated successfully."
        );
      } catch (err) {
        console.error(
          "Similarity calculation failed:",
          err
        );

        setError(
          getErrorMessage(
            err,
            "Failed to calculate similarity."
          )
        );
      } finally {
        setActionLoading("");
      }
    };

  // =====================================================
  // GENERATE RISK V1
  // =====================================================

  const handleGenerateRisk =
    async () => {
      if (
        !document?.id ||
        !comparedDocumentId
      ) {
        setError(
          "Please select a document comparison before generating risk."
        );

        return;
      }

      if (!similarityData) {
        setError(
          "Please calculate similarity before generating risk."
        );

        return;
      }

      try {
        clearMessages();

        setActionLoading(
          "risk"
        );

        const result =
          await calculateDocumentRisk(
            document.id,
            Number(
              comparedDocumentId
            )
          );

        const normalized =
          normalizeRisk(result);

        setRiskData(
          normalized
        );

        /*
         * Keep V1 as active risk when
         * V1 is explicitly generated.
         */

        setActiveRisk(
          normalized
        );

        setSuccessMessage(
          "Risk assessment V1 generated successfully."
        );
      } catch (err) {
        console.error(
          "Risk generation failed:",
          err
        );

        setError(
          getErrorMessage(
            err,
            "Failed to generate risk assessment."
          )
        );
      } finally {
        setActionLoading("");
      }
    };

  // =====================================================
  // GENERATE RISK V2
  // =====================================================

  const handleGenerateRiskV2 =
    async () => {
      if (
        !document?.id ||
        !comparedDocumentId
      ) {
        setError(
          "Please select a document comparison before generating Risk V2."
        );

        return;
      }

      if (!similarityData) {
        setError(
          "Please calculate similarity before generating Risk V2."
        );

        return;
      }

      try {
        clearMessages();

        setActionLoading(
          "risk-v2"
        );

        const result =
          await calculateDocumentRiskV2(
            document.id,
            Number(
              comparedDocumentId
            )
          );

        const normalized =
          normalizeRiskV2(
            result
          );

        setRiskV2Data(
          normalized
        );

        /*
         * V2 is the enhanced/current risk engine.
         */

        setActiveRisk(
          normalized
        );

        setSuccessMessage(
          "Feature-based Risk Assessment V2 generated successfully."
        );
      } catch (err) {
        console.error(
          "Risk V2 generation failed:",
          err
        );

        setError(
          getErrorMessage(
            err,
            "Failed to generate Risk Assessment V2."
          )
        );
      } finally {
        setActionLoading("");
      }
    };

  // =====================================================
  // GENERATE ALERT
  // =====================================================

  const handleGenerateAlert =
    async () => {
      if (!document?.id) {
        setError(
          "A valid document is required."
        );

        return;
      }

      if (!activeRisk) {
        setError(
          "Please generate a risk assessment before generating an alert."
        );

        return;
      }

      try {
        clearMessages();

        setActionLoading(
          "alert"
        );

        const result =
          await createDocumentAlert(
            document.id
          );

        setAlertsData(
          normalizeAlert(result)
        );

        setSuccessMessage(
          "Security alert generated successfully."
        );
      } catch (err) {
        console.error(
          "Alert generation failed:",
          err
        );

        setError(
          getErrorMessage(
            err,
            "Failed to generate alert."
          )
        );
      } finally {
        setActionLoading("");
      }
    };

  // =====================================================
  // NO DOCUMENT
  // =====================================================

  if (!document) {
    return (
      <div className="state-message">
        No document selected.
      </div>
    );
  }

  // =====================================================
  // CURRENT RISK LEVEL
  // =====================================================

  const riskLevel =
    activeRisk?.risk_level ||
    "pending";

  // =====================================================
  // RENDER
  // =====================================================

  return (
    <main className="main-content">

      {/* =================================================
          BACK
      ================================================= */}

      <button
        type="button"
        className="back-button"
        onClick={onBack}
        disabled={
          actionLoading !== ""
        }
      >
        ← Back to Documents
      </button>

      {/* =================================================
          HERO
      ================================================= */}

      <section className="hero-section">
        <h2>
          {getDisplayFileName(
            document.file_name
          )}
        </h2>

        <p>
          Document ID: {document.id}
        </p>
      </section>

      {/* =================================================
          SECURITY OVERVIEW
      ================================================= */}

      <section className="security-overview">

        <div className="security-overview-header">

          <div>
            <span className="overview-label">
              EXAMGUARD SECURITY
            </span>

            <h2>
              Security Overview
            </h2>
          </div>

          <div
            className={`security-status ${riskLevel}`}
          >
            {riskLevel === "pending"
              ? "PENDING"
              : riskLevel.toUpperCase()}
          </div>

        </div>

        <div className="security-overview-grid">

          {/* SIMILARITY */}

          <div className="overview-card">
            <span>
              Similarity
            </span>

            <strong>
              {similarityData?.similarity_score !==
                null &&
              similarityData?.similarity_score !==
                undefined
                ? `${Number(
                    similarityData.similarity_score
                  ).toFixed(2)}%`
                : "N/A"}
            </strong>

            <small>
              {similarityData?.similarity_method ||
                "Not analyzed"}
            </small>
          </div>

          {/* RISK SCORE */}

          <div className="overview-card">
            <span>
              Risk Score
            </span>

            <strong>
              {activeRisk?.risk_score ??
                "N/A"}
            </strong>

            <small>
              {activeRisk?.model_version ||
                "Risk model pending"}
            </small>
          </div>

          {/* RISK LEVEL */}

          <div className="overview-card">
            <span>
              Risk Level
            </span>

            <strong>
              {activeRisk?.risk_level
                ? activeRisk.risk_level.toUpperCase()
                : "N/A"}
            </strong>

            <small>
              {activeRisk?.model_version ||
                "Risk model pending"}
            </small>
          </div>

          {/* ALERT */}

          <div className="overview-card">
            <span>
              Alert Status
            </span>

            <strong>
              {alertsData?.status
                ? alertsData.status.toUpperCase()
                : "N/A"}
            </strong>

            <small>
              {alertsData?.severity
                ? `Severity: ${alertsData.severity}`
                : "No alert generated"}
            </small>
          </div>

        </div>
      </section>

      {/* =================================================
          LOADING
      ================================================= */}

      {loading && (
        <section className="documents-section">
          <div className="state-message">
            Loading document analysis...
          </div>
        </section>
      )}

      {/* =================================================
          ERROR
      ================================================= */}

      {!loading && error && (
        <section className="documents-section">
          <div className="error-message">
            {error}
          </div>
        </section>
      )}

      {/* =================================================
          SUCCESS
      ================================================= */}

      {!loading && successMessage && (
        <section className="documents-section">
          <div className="success-message">
            {successMessage}
          </div>
        </section>
      )}

      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      {!loading && (
        <>

          {/* =================================================
              DOCUMENT INFORMATION
          ================================================= */}

          <section className="documents-section">

            <h2>
              Document Information
            </h2>

            <div className="details-grid">

              <div className="detail-item">
                <span>
                  Document ID
                </span>

                <strong>
                  {document.id}
                </strong>
              </div>

              <div className="detail-item">
                <span>
                  File Type
                </span>

                <strong>
                  {document.file_type ||
                    "N/A"}
                </strong>
              </div>

              <div className="detail-item">
                <span>
                  Status
                </span>

                <strong>
                  {document.status ||
                    "N/A"}
                </strong>
              </div>

              <div className="detail-item">
                <span>
                  Source
                </span>

                <strong>
                  {document.source_type ||
                    "N/A"}
                </strong>
              </div>

            </div>
          </section>

          {/* =================================================
              ANALYSIS ACTIONS
          ================================================= */}

          <section className="documents-section">

            <h2>
              Analysis Actions
            </h2>

            <div className="comparison-selector">

              <label htmlFor="comparison-document">
                Compare Document{" "}
                {document.id} With
              </label>

              {comparisonDocuments.length >
              0 ? (
                <select
                  id="comparison-document"
                  value={
                    comparedDocumentId
                  }
                  onChange={
                    handleComparisonChange
                  }
                  disabled={
                    actionLoading !== ""
                  }
                >

                  <option value="">
                    Select a document
                  </option>

                  {comparisonDocuments.map(
                    (item) => (
                      <option
                        key={item.id}
                        value={item.id}
                      >
                        Document{" "}
                        {item.id} -{" "}
                        {getDisplayFileName(
                          item.file_name
                        )}
                      </option>
                    )
                  )}

                </select>
              ) : (
                <div className="state-message">
                  No other document is
                  available for comparison.
                </div>
              )}

            </div>

            {comparedDocumentId && (
              <p className="comparison-description">
                Comparing Document{" "}
                <strong>
                  {document.id}
                </strong>{" "}
                with Document{" "}
                <strong>
                  {comparedDocumentId}
                </strong>
                .
              </p>
            )}

            {/* ACTION BUTTONS */}

            <div className="action-buttons">

              {/* FULL ANALYSIS */}

              <button
                type="button"
                className="primary-button"
                onClick={
                  handleFullSecurityAnalysis
                }
                disabled={
                  !comparedDocumentId ||
                  actionLoading !== ""
                }
              >
                {actionLoading ===
                "full-analysis"
                  ? "Running Full Analysis..."
                  : "Run Full Security Analysis"}
              </button>

              {/* SIMILARITY */}

              <button
                type="button"
                className="primary-button"
                onClick={
                  handleCalculateSimilarity
                }
                disabled={
                  !comparedDocumentId ||
                  actionLoading !== ""
                }
              >
                {actionLoading ===
                "similarity"
                  ? "Calculating..."
                  : "Calculate Similarity"}
              </button>

              {/* RISK V1 */}

              <button
                type="button"
                className="primary-button"
                onClick={
                  handleGenerateRisk
                }
                disabled={
                  !comparedDocumentId ||
                  !similarityData ||
                  actionLoading !== ""
                }
              >
                {actionLoading === "risk"
                  ? "Generating..."
                  : "Generate Risk Assessment"}
              </button>

              {/* RISK V2 */}

              <button
                type="button"
                className="secondary-button"
                onClick={
                  handleGenerateRiskV2
                }
                disabled={
                  !comparedDocumentId ||
                  !similarityData ||
                  actionLoading !== ""
                }
              >
                {actionLoading ===
                "risk-v2"
                  ? "Generating V2..."
                  : "Generate Risk V2"}
              </button>

              {/* ALERT */}

              <button
                type="button"
                className="primary-button"
                onClick={
                  handleGenerateAlert
                }
                disabled={
                  !activeRisk ||
                  actionLoading !== ""
                }
              >
                {actionLoading === "alert"
                  ? "Generating..."
                  : "Generate Alert"}
              </button>

            </div>
          </section>

          {/* =================================================
              EXTRACTED TEXT
          ================================================= */}

          <section className="documents-section">

            <h2>
              Extracted Text
            </h2>

            {textData ? (
              <>

                <div className="text-box">
                  {textData.extracted_text ||
                    "No extracted text available."}
                </div>

                <div className="metadata-grid">

                  <div className="detail-item">
                    <span>
                      OCR Engine
                    </span>

                    <strong>
                      {textData.ocr_engine ||
                        "N/A"}
                    </strong>
                  </div>

                  <div className="detail-item">
                    <span>
                      OCR Confidence
                    </span>

                    <strong>
                      {textData.ocr_confidence ??
                        "N/A"}
                    </strong>
                  </div>

                  <div className="detail-item">
                    <span>
                      Language
                    </span>

                    <strong>
                      {textData.language ||
                        "N/A"}
                    </strong>
                  </div>

                </div>

              </>
            ) : (
              <div className="state-message">
                Extracted text is not available.
              </div>
            )}

          </section>

          {/* =================================================
              NLP ANALYSIS
          ================================================= */}

          <section className="documents-section">

            <h2>
              NLP Analysis
            </h2>

            {analysisData ? (
              <>

                <div className="analysis-grid">

                  <div className="analysis-card">
                    <span>
                      Word Count
                    </span>

                    <strong>
                      {analysisData
                        .result_data
                        ?.word_count ?? 0}
                    </strong>
                  </div>

                  <div className="analysis-card">
                    <span>
                      Sentence Count
                    </span>

                    <strong>
                      {analysisData
                        .result_data
                        ?.sentence_count ?? 0}
                    </strong>
                  </div>

                  <div className="analysis-card">
                    <span>
                      Character Count
                    </span>

                    <strong>
                      {analysisData
                        .result_data
                        ?.character_count ?? 0}
                    </strong>
                  </div>

                  <div className="analysis-card">
                    <span>
                      Unique Words
                    </span>

                    <strong>
                      {analysisData
                        .result_data
                        ?.unique_word_count ?? 0}
                    </strong>
                  </div>

                </div>

                <div className="analysis-meta">

                  <p>
                    <strong>
                      Analysis Type:
                    </strong>{" "}
                    {analysisData.analysis_type ||
                      "N/A"}
                  </p>

                  <p>
                    <strong>
                      Model:
                    </strong>{" "}
                    {analysisData.model_version ||
                      "N/A"}
                  </p>

                  <p>
                    <strong>
                      Confidence:
                    </strong>{" "}
                    {analysisData.confidence_score ??
                      "N/A"}
                    %
                  </p>

                </div>

                <h3 className="subheading">
                  Top Words
                </h3>

                <div className="top-words">

                  {analysisData
                    .result_data
                    ?.top_words?.length > 0 ? (
                    analysisData.result_data.top_words.map(
                      (item, index) => (
                        <div
                          className="word-item"
                          key={`${item.word}-${index}`}
                        >
                          <span>
                            {item.word}
                          </span>

                          <strong>
                            {item.count}
                          </strong>
                        </div>
                      )
                    )
                  ) : (
                    <div className="state-message">
                      No top words available.
                    </div>
                  )}

                </div>

              </>
            ) : (
              <div className="state-message">
                NLP analysis has not been
                generated for this document yet.
              </div>
            )}

          </section>

          {/* =================================================
              DOCUMENT SIMILARITY
          ================================================= */}

          <section className="documents-section">

            <h2>
              Document Similarity
            </h2>

            {similarityData ? (
              <>

                <div className="similarity-panel">

                  <div className="similarity-card">
                    <span>
                      Similarity Score
                    </span>

                    <strong>
                      {Number(
                        similarityData.similarity_score
                      ).toFixed(2)}
                      %
                    </strong>
                  </div>

                  <div className="similarity-card">
                    <span>
                      Comparison Method
                    </span>

                    <strong>
                      {similarityData
                        .similarity_method ||
                        "N/A"}
                    </strong>
                  </div>

                </div>

                <div className="comparison-panel">

                  <div className="comparison-document">
                    <span>
                      Current Document
                    </span>

                    <strong>
                      Document{" "}
                      {similarityData
                        .document_id ??
                        "N/A"}
                    </strong>
                  </div>

                  <div className="comparison-arrow">
                    ↔
                  </div>

                  <div className="comparison-document">
                    <span>
                      Compared Document
                    </span>

                    <strong>
                      Document{" "}
                      {similarityData
                        .compared_document_id ??
                        "N/A"}
                    </strong>
                  </div>

                </div>

                <div className="similarity-badge">

                  {Number(
                    similarityData.similarity_score
                  ) < 40
                    ? "Low Similarity"
                    : Number(
                        similarityData.similarity_score
                      ) < 70
                    ? "Moderate Similarity"
                    : "High Similarity"}

                </div>

                {Array.isArray(
                  similarityData.matching_sections
                ) &&
                  similarityData
                    .matching_sections
                    .length > 0 && (
                    <>

                      <h3 className="subheading">
                        Matching Sections
                      </h3>

                      <div className="matching-sections">

                        {similarityData.matching_sections.map(
                          (
                            section,
                            index
                          ) => (
                            <div
                              className="matching-section"
                              key={index}
                            >
                              {typeof section ===
                              "string"
                                ? section
                                : JSON.stringify(
                                    section
                                  )}
                            </div>
                          )
                        )}

                      </div>

                    </>
                  )}

              </>
            ) : (
              <div className="state-message">
                Select a document and calculate
                similarity to view the result.
              </div>
            )}

          </section>

          {/* =================================================
              RISK V1
          ================================================= */}

          <section className="documents-section">

            <div className="section-title-row">

              <div>

                <h2>
                  Risk Assessment
                </h2>

                <span className="model-badge">
                  BASELINE · V1
                </span>

              </div>

            </div>

            {riskData ? (
              <>

                <div className="risk-panel">

                  <div className="risk-score">
                    <span>
                      Risk Score
                    </span>

                    <strong>
                      {riskData.risk_score}
                    </strong>
                  </div>

                  <div className="risk-level">
                    <span>
                      Risk Level
                    </span>

                    <strong>
                      {riskData.risk_level
                        ?.toUpperCase() ||
                        "N/A"}
                    </strong>
                  </div>

                </div>

                <div className="analysis-meta">

                  <p>
                    <strong>
                      Model:
                    </strong>{" "}
                    {riskData.model_version ||
                      "N/A"}
                  </p>

                </div>

                <h3 className="subheading">
                  Risk Factors
                </h3>

                <ul className="risk-factors">

                  {Array.isArray(
                    riskData.risk_factors
                  ) &&
                  riskData.risk_factors.length >
                    0 ? (
                    riskData.risk_factors.map(
                      (
                        factor,
                        index
                      ) => (
                        <li key={index}>
                          {typeof factor ===
                          "string"
                            ? factor
                            : JSON.stringify(
                                factor
                              )}
                        </li>
                      )
                    )
                  ) : (
                    <li>
                      No risk factors reported.
                    </li>
                  )}

                </ul>

              </>
            ) : (
              <div className="state-message">
                V1 risk assessment has not been
                generated for this comparison.
              </div>
            )}

          </section>

          {/* =================================================
              RISK V2
          ================================================= */}

          <section className="documents-section">

            <div className="section-title-row">

              <div>

                <h2>
                  Risk Assessment V2
                </h2>

                <span className="model-badge v2">
                  ENHANCED · V2
                </span>

              </div>

            </div>

            {riskV2Data ? (
              <>

                <div className="risk-panel">

                  <div className="risk-score">
                    <span>
                      Risk Score
                    </span>

                    <strong>
                      {riskV2Data.risk_score}
                    </strong>
                  </div>

                  <div className="risk-level">
                    <span>
                      Risk Level
                    </span>

                    <strong>
                      {riskV2Data.risk_level
                        ?.toUpperCase() ||
                        "N/A"}
                    </strong>
                  </div>

                </div>

                <div className="analysis-meta">

                  <p>
                    <strong>
                      Model:
                    </strong>{" "}
                    {riskV2Data.model_version ||
                      "N/A"}
                  </p>

                </div>

                <h3 className="subheading">
                  Risk Factors
                </h3>

                <ul className="risk-factors">

                  {riskV2Factors.length >
                  0 ? (
                    riskV2Factors.map(
                      (
                        factor,
                        index
                      ) => (
                        <li key={index}>
                          {factor}
                        </li>
                      )
                    )
                  ) : (
                    <li>
                      No textual risk factors
                      reported.
                    </li>
                  )}

                </ul>

                {/* =================================================
                    FEATURE SNAPSHOT
                ================================================= */}

                {featureSnapshot && (
                  <>

                    <h3 className="subheading">
                      Feature Snapshot
                    </h3>

                    <div className="feature-grid">

                      <div className="feature-card">
                        <span>
                          Similarity
                        </span>

                        <strong>
                          {Number(
                            featureSnapshot
                              .similarity_score ??
                              0
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Word Difference
                        </span>

                        <strong>
                          {Number(
                            featureSnapshot
                              .word_count_difference ??
                              0
                          )}
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Word Difference Ratio
                        </span>

                        <strong>
                          {(
                            Number(
                              featureSnapshot
                                .word_count_difference_ratio ??
                                0
                            ) * 100
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Sentence Difference
                        </span>

                        <strong>
                          {Number(
                            featureSnapshot
                              .sentence_count_difference ??
                              0
                          )}
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Sentence Difference Ratio
                        </span>

                        <strong>
                          {(
                            Number(
                              featureSnapshot
                                .sentence_count_difference_ratio ??
                                0
                            ) * 100
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Character Difference
                        </span>

                        <strong>
                          {Number(
                            featureSnapshot
                              .character_count_difference ??
                              0
                          )}
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Character Difference Ratio
                        </span>

                        <strong>
                          {(
                            Number(
                              featureSnapshot
                                .character_count_difference_ratio ??
                                0
                            ) * 100
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Unique Word Difference
                        </span>

                        <strong>
                          {Number(
                            featureSnapshot
                              .unique_word_difference ??
                              0
                          )}
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Unique Word Difference Ratio
                        </span>

                        <strong>
                          {(
                            Number(
                              featureSnapshot
                                .unique_word_difference_ratio ??
                                0
                            ) * 100
                          ).toFixed(2)}
                          %
                        </strong>
                      </div>

                      <div className="feature-card">
                        <span>
                          Words / Sentence
                        </span>

                        <strong>
                          {Number(
                            featureSnapshot
                              .current_words_per_sentence ??
                              0
                          ).toFixed(2)}
                        </strong>
                      </div>

                    </div>

                  </>
                )}

              </>
            ) : (
              <div className="state-message">
                Feature-based Risk Assessment V2
                has not been generated for this
                comparison.
              </div>
            )}

          </section>

          {/* =================================================
              MODEL COMPARISON
          ================================================= */}

          {(riskData || riskV2Data) && (
            <section className="documents-section">

              <h2>
                Risk Model Comparison
              </h2>

              <div className="risk-comparison-grid">

                <div className="model-comparison-card">

                  <span>
                    Risk Engine V1
                  </span>

                  <strong>
                    {riskData?.risk_score ??
                      "N/A"}
                  </strong>

                  <small>
                    {riskData?.risk_level
                      ?.toUpperCase() ||
                      "NOT GENERATED"}
                  </small>

                  <em>
                    Similarity-based baseline
                  </em>

                </div>

                <div className="model-comparison-card">

                  <span>
                    Risk Engine V2
                  </span>

                  <strong>
                    {riskV2Data?.risk_score ??
                      "N/A"}
                  </strong>

                  <small>
                    {riskV2Data?.risk_level
                      ?.toUpperCase() ||
                      "NOT GENERATED"}
                  </small>

                  <em>
                    Feature-based enhanced model
                  </em>

                </div>

              </div>

            </section>
          )}

          {/* =================================================
              SECURITY ALERTS
          ================================================= */}

          <section className="documents-section security-alert-section">

            <div className="section-title-row">

              <div>

                <h2>
                  Security Alerts
                </h2>

                <span className="model-badge">
                  SECURITY MONITORING
                </span>

              </div>

              {alertsData && (
                <span
                  className={`alert-status-badge ${
                    alertsData.status?.toLowerCase() ||
                    "unknown"
                  }`}
                >
                  {alertsData.status?.toUpperCase() ||
                    "UNKNOWN"}
                </span>
              )}

            </div>

            {alertsData ? (
              <div
                className={`security-alert-card ${
                  alertsData.severity?.toLowerCase() ||
                  "medium"
                }`}
              >

                {/* ALERT HEADER */}

                <div className="security-alert-header">

                  <div className="security-alert-icon">
                    🔔
                  </div>

                  <div className="security-alert-heading">

                    <span className="alert-eyebrow">
                      EXAMGUARD SECURITY ALERT
                    </span>

                    <h3>
                      {alertsData.alert_type ===
                      "critical_risk"
                        ? "Critical Risk Detected"
                        : alertsData.alert_type ===
                          "high_risk"
                        ? "High Risk Detected"
                        : alertsData.alert_type ===
                          "moderate_risk"
                        ? "Moderate Risk Detected"
                        : "Security Risk Assessment"}
                    </h3>

                    <p>
                      Examination document
                      security monitoring has
                      detected a potential risk
                      condition.
                    </p>

                  </div>

                  <div
                    className={`alert-severity ${
                      alertsData.severity?.toLowerCase() ||
                      "medium"
                    }`}
                  >
                    {alertsData.severity?.toUpperCase() ||
                      "UNKNOWN"}
                  </div>

                </div>

                {/* ALERT INFORMATION */}

                <div className="alert-info-grid">

                  <div className="alert-info-card">
                    <span>
                      Alert Type
                    </span>

                    <strong>
                      {alertsData.alert_type ||
                        "N/A"}
                    </strong>
                  </div>

                  <div className="alert-info-card">
                    <span>
                      Severity
                    </span>

                    <strong>
                      {alertsData.severity
                        ?.toUpperCase() ||
                        "N/A"}
                    </strong>
                  </div>

                  <div className="alert-info-card">
                    <span>
                      Status
                    </span>

                    <strong>
                      {alertsData.status
                        ?.toUpperCase() ||
                        "N/A"}
                    </strong>
                  </div>

                  <div className="alert-info-card">
                    <span>
                      Alert ID
                    </span>

                    <strong>
                      {alertsData.id ??
                        "N/A"}
                    </strong>
                  </div>

                </div>

                {/* ALERT MESSAGE */}

                <div className="alert-message-box">

                  <span>
                    Security Assessment
                  </span>

                  <p>
                    {alertsData.message ||
                      "No security alert message available."}
                  </p>

                </div>

                {/* ALERT METADATA */}

                <div className="alert-metadata">

                  <div>
                    <span>
                      Document ID
                    </span>

                    <strong>
                      {alertsData.document_id ??
                        document.id}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Risk Score ID
                    </span>

                    <strong>
                      {alertsData.risk_score_id ??
                        "N/A"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Generated At
                    </span>

                    <strong>
                      {alertsData.created_at ||
                        "N/A"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Resolution
                    </span>

                    <strong>
                      {alertsData.resolved_at
                        ? alertsData.resolved_at
                        : "Pending verification"}
                    </strong>
                  </div>

                </div>

                {/* RECOMMENDATION */}

                <div className="alert-recommendation">

                  <div className="recommendation-icon">
                    ⚠
                  </div>

                  <div>

                    <strong>
                      Recommended Action
                    </strong>

                    <p>
                      {alertsData.severity ===
                      "critical"
                        ? "Immediate examination-security investigation is recommended."
                        : alertsData.severity ===
                          "high"
                        ? "Detailed verification and security review are recommended."
                        : alertsData.severity ===
                          "medium"
                        ? "Further verification is recommended before taking action."
                        : "Continue normal monitoring and verification procedures."}
                    </p>

                  </div>

                </div>

              </div>
            ) : (
              <div className="no-alert-card">

                <div className="no-alert-icon">
                  ✓
                </div>

                <div>

                  <h3>
                    No Security Alert
                  </h3>

                  <p>
                    No alert has been generated
                    for this document yet.
                    Generate a risk assessment
                    first, then generate a
                    security alert.
                  </p>

                </div>

              </div>
            )}

          </section>

        </>
      )}

    </main>
  );
}

export default DocumentDetails;
