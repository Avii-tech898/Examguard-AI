// =====================================================
// DOCUMENT CARD
// =====================================================

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

function DocumentCard({ document, onViewDetails }) {
  const displayFileName = getDisplayFileName(
    document?.file_name
  );

  const fileType =
    document?.file_type || "application/octet-stream";

  const status =
    document?.status || "unknown";

  const sourceType =
    document?.source_type || "unknown";

  return (
    <article className="document-card">

      {/* =================================================
          FILE TYPE
      ================================================= */}

      <div className="document-icon">
        {fileType
          .toLowerCase()
          .includes("pdf")
          ? "PDF"
          : "DOC"}
      </div>

      {/* =================================================
          DOCUMENT INFORMATION
      ================================================= */}

      <div className="document-info">

        <h3 title={displayFileName}>
          {displayFileName}
        </h3>

        <p>
          <strong>ID:</strong>{" "}
          {document?.id ?? "N/A"}
        </p>

        <p>
          <strong>Type:</strong>{" "}
          {fileType}
        </p>

        <p>
          <strong>Status:</strong>{" "}
          <span className="status-badge">
            {status}
          </span>
        </p>

        <p>
          <strong>Source:</strong>{" "}
          {sourceType}
        </p>

        {/* =================================================
            VIEW DETAILS
        ================================================= */}

        <button
          type="button"
          className="details-button"
          onClick={() => onViewDetails(document)}
        >
          View Details
        </button>

      </div>
    </article>
  );
}

export default DocumentCard;