import apiClient from "./client";

// =====================================================
// DOCUMENTS
// =====================================================

export const getDocuments = async () => {
  const response = await apiClient.get("/documents/");
  return response.data;
};


// =====================================================
// DOCUMENT UPLOAD
// =====================================================

export const uploadDocument = async (file) => {
  if (!file) {
    throw new Error("File is required");
  }

  const formData = new FormData();

  formData.append("file", file);

  const response = await apiClient.post(
    "/documents/upload",
    formData
  );

  return response.data;
};


// =====================================================
// DOCUMENT TEXT - GET
// =====================================================

export const getDocumentText = async (documentId) => {
  const response = await apiClient.get(
    `/documents/${documentId}/text`
  );

  return response.data;
};


// =====================================================
// DOCUMENT TEXT - POST / EXTRACT
// =====================================================

export const extractDocumentText = async (documentId) => {
  const response = await apiClient.post(
    `/documents/${documentId}/extract-text`
  );

  return response.data;
};


// =====================================================
// NLP ANALYSIS - GET
// =====================================================

export const getDocumentAnalysis = async (documentId) => {
  const response = await apiClient.get(
    `/documents/${documentId}/analysis`
  );

  return response.data;
};


// =====================================================
// NLP ANALYSIS - POST / GENERATE
// =====================================================

export const analyzeDocument = async (documentId) => {
  const response = await apiClient.post(
    `/documents/${documentId}/analyze`
  );

  return response.data;
};


// =====================================================
// SIMILARITY - GET
// =====================================================

export const getDocumentSimilarity = async (
  documentId,
  comparedDocumentId
) => {
  const response = await apiClient.get(
    `/documents/${documentId}/similarity/${comparedDocumentId}`
  );

  return response.data;
};


// =====================================================
// SIMILARITY - POST / CALCULATE
// =====================================================

export const calculateDocumentSimilarity = async (
  documentId,
  comparedDocumentId
) => {
  const response = await apiClient.post(
    `/documents/${documentId}/similarity/${comparedDocumentId}`
  );

  return response.data;
};


// =====================================================
// RISK - GET LATEST
// =====================================================

export const getDocumentRisk = async (documentId) => {
  const response = await apiClient.get(
    `/documents/${documentId}/risk`
  );

  return response.data;
};


// =====================================================
// RISK V1 - GET
// =====================================================

export const getDocumentRiskV1 = async (documentId) => {
  const response = await apiClient.get(
    `/documents/${documentId}/risk-v1`
  );

  return response.data;
};


// =====================================================
// RISK V1 - POST / GENERATE
// =====================================================

export const calculateDocumentRisk = async (
  documentId,
  comparedDocumentId
) => {
  const response = await apiClient.post(
    `/documents/${documentId}/risk/${comparedDocumentId}`
  );

  return response.data;
};


// =====================================================
// RISK V2 - GET
// =====================================================

export const getDocumentRiskV2 = async (documentId) => {
  const response = await apiClient.get(
    `/documents/${documentId}/risk-v2`
  );

  return response.data;
};


// =====================================================
// RISK V2 - POST / GENERATE
// =====================================================

export const calculateDocumentRiskV2 = async (
  documentId,
  comparedDocumentId
) => {
  const response = await apiClient.post(
    `/documents/${documentId}/risk-v2/${comparedDocumentId}`
  );

  return response.data;
};


// =====================================================
// ALERT - GET LATEST DOCUMENT ALERT
// =====================================================

export const getDocumentAlerts = async (documentId) => {
  const response = await apiClient.get(
    `/documents/${documentId}/alerts`
  );

  return response.data;
};


// =====================================================
// ALERT - GET ALL
// =====================================================

export const getAllAlerts = async () => {
  const response = await apiClient.get(
    "/alerts"
  );

  return response.data;
};


// =====================================================
// ALERT - POST / GENERATE
// =====================================================

export const createDocumentAlert = async (documentId) => {
  const response = await apiClient.post(
    `/documents/${documentId}/alerts`
  );

  return response.data;
};


// =====================================================
// ALERT - PATCH / RESOLVE
// =====================================================

export const resolveDocumentAlert = async (
  documentId,
  alertId
) => {
  const response = await apiClient.patch(
    `/documents/${documentId}/alerts/${alertId}/resolve`
  );

  return response.data;
};


// =====================================================
// ANALYTICS - SECURITY OVERVIEW
// =====================================================

export const getAnalyticsOverview = async () => {
  const response = await apiClient.get(
    "/analytics/overview"
  );

  return response.data;
};


// =====================================================
// FULL SECURITY PROCESSING PIPELINE
// =====================================================

export const processDocumentPair = async (
  documentId,
  comparedDocumentId
) => {
  const response = await apiClient.post(
    `/documents/${documentId}/process/${comparedDocumentId}`
  );

  return response.data;
};
// =====================================================
// HEALTH CHECK
// =====================================================

export const getBackendHealth = async () => {
  const response = await apiClient.get("/v1/health");
  return response.data;
};