import { useEffect, useState } from "react";
import api from "./api.js";
import Sidebar from "./components/Layout/Sidebar.jsx";
import MobileNav from "./components/Layout/MobileNav.jsx";
import DashboardHome from "./components/Dashboard/DashboardHome.jsx";
import DetectionPage from "./components/Detection/DetectionPage.jsx";
import PredictionHistory from "./components/History/PredictionHistory.jsx";
import HistoryDetail from "./components/History/HistoryDetail.jsx";
import CropGuidePage from "./components/CropGuide/CropGuidePage.jsx";
import AboutPage from "./components/About/AboutPage.jsx";
import { getHistory, addHistoryEntry, deleteHistoryEntry, clearHistory } from "./lib/history.js";

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function App() {
  const [activeSection, setActiveSection] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(true);

  const [history, setHistory] = useState(() => getHistory());
  const [selectedHistoryEntry, setSelectedHistoryEntry] = useState(null);

  // Keep the object URL preview in sync with the selected file, and revoke
  // it on change/unmount to avoid memory leaks.
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleNavigate = (section) => {
    setActiveSection(section);
    setSidebarOpen(false);
  };

  const handleFileSelected = (f) => {
    setFile(f);
    setResult(null);
    setError(null);
    setValidationError(null);
  };

  const handleRemove = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post("analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      setBackendOnline(true);

      const thumb = await fileToDataUrl(file).catch(() => null);
      const updated = addHistoryEntry({
        fileName: file.name,
        imageDataUrl: thumb,
        predictedClass: res.data.predicted_class,
        confidence: res.data.confidence,
        probabilities: res.data.probabilities,
        recommendation: res.data.recommendation,
        recommendationError: res.data.recommendation_error,
      });
      setHistory(updated);
    } catch (err) {
      setBackendOnline(false);
      setError(
        err?.response?.data?.detail ||
          "We couldn't connect to the AI analysis service. Please check that the backend is running and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = () => {
    setHistory(clearHistory());
    setSelectedHistoryEntry(null);
  };

  const handleDeleteHistoryEntry = (id) => {
    const updated = deleteHistoryEntry(id);
    setHistory(updated);
    if (selectedHistoryEntry?.id === id) {
      setSelectedHistoryEntry(null);
      setActiveSection("history");
    }
  };

  const handleSelectHistory = (entry) => {
    setSelectedHistoryEntry(entry);
    setActiveSection("historyDetail");
  };

  const handleBackToHistory = () => {
    setSelectedHistoryEntry(null);
    setActiveSection("history");
  };

  return (
    <div className="app-shell">
      <Sidebar
        active={activeSection}
        onNavigate={handleNavigate}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        backendOnline={backendOnline}
      />

      <div className="main-area">
        <MobileNav onOpenMenu={() => setSidebarOpen(true)} />

        <div className="main-content">
          {activeSection === "dashboard" && (
            <DashboardHome
              backendOnline={backendOnline}
              recentHistory={history}
              onNavigate={handleNavigate}
              onSelectHistory={handleSelectHistory}
            />
          )}

          {activeSection === "detect" && (
            <DetectionPage
              file={file}
              previewUrl={previewUrl}
              result={result}
              loading={loading}
              error={error}
              validationError={validationError}
              backendOnline={backendOnline}
              onFileSelected={handleFileSelected}
              onRemove={handleRemove}
              onNewPrediction={handleRemove}
              onAnalyze={handleAnalyze}
              onValidationError={setValidationError}
              onDismissValidationError={() => setValidationError(null)}
            />
          )}

          {activeSection === "history" && (
            <PredictionHistory
              history={history}
              onClear={handleClearHistory}
              onSelect={handleSelectHistory}
              onDelete={handleDeleteHistoryEntry}
            />
          )}

          {activeSection === "historyDetail" && selectedHistoryEntry && (
            <HistoryDetail entry={selectedHistoryEntry} onBack={handleBackToHistory} onDelete={handleDeleteHistoryEntry} />
          )}

          {activeSection === "guide" && <CropGuidePage />}

          {activeSection === "about" && <AboutPage />}
        </div>
      </div>
    </div>
  );
}
