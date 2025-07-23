
 
import React, { useState } from 'react';
import { ArrowRight, Download, Search, CheckCircle, AlertCircle, Loader, ArrowLeft } from 'lucide-react';
 
const Analyzer = ({ onBackToHome, onAnalysisComplete, initialNamespace }) => {
  const [formData, setFormData] = useState({
    github_link: '',
    git_token: '',
    namespace: initialNamespace || 'MyApplication'
  });
 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisBundle, setAnalysisBundle] = useState(null); // Will hold the downloaded blob/file
 
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
 
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setAnalysisBundle(null);
 
    const submitData = new FormData();
    submitData.append('github_link', formData.github_link);
    submitData.append('git_token', formData.git_token);
 
    try {
      const response = await fetch('http://localhost:8000/api/analyze/generate-project-analysis', {
        method: 'POST',
        body: submitData,
      });
 
      if (response.ok) {
        const blob = await response.blob();
        const file = new File([blob], "analysis_bundle.zip", { type: "application/zip" });
        setAnalysisBundle(file); // Store the file object
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred during analysis.' }));
        setError(errorData.detail);
      }
    } catch (err) {
      setError('Failed to connect to the server. Please ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
 
  const downloadAnalysisBundle = () => {
    if (analysisBundle) {
      const url = URL.createObjectURL(analysisBundle);
      const a = document.createElement('a');
      a.href = url;
      a.download = analysisBundle.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };
 
  const proceedToConversion = () => {
    if (analysisBundle && onAnalysisComplete) {
      onAnalysisComplete(analysisBundle, formData.namespace, formData.github_link);
    }
  };
 
  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-lg border-0 mb-4">
            <div className="card-header text-white text-center py-4" style={{ background: 'linear-gradient(135deg, #0d9488, #14b8a6)' }}>
              <h2 className="mb-0">
                <Search className="me-2" />
                Repository Analysis
              </h2>
            </div>
            <div className="card-body p-5">
              {!analysisBundle && !loading && (
                <form onSubmit={handleSubmit}>
                  {/* Form fields remain the same */}
                  <div className="mb-4">
                    <label htmlFor="github_link" className="form-label fw-bold">GitHub Repository URL *</label>
                    <input type="url" className="form-control form-control-lg" id="github_link" name="github_link" value={formData.github_link} onChange={handleInputChange} placeholder="https://github.com/username/repository" required />
                  </div>
                  <div className="mb-4">
                    <label htmlFor="git_token" className="form-label fw-bold">Git Token (Optional for private repos)</label>
                    <input type="password" className="form-control form-control-lg" id="git_token" name="git_token" value={formData.git_token} onChange={handleInputChange} placeholder="ghp_xxxxxxxxxxxxxxxxxxxx" />
                  </div>
                  <div className="mb-4">
                    <label htmlFor="namespace" className="form-label fw-bold">Project Namespace</label>
                    <input type="text" className="form-control form-control-lg" id="namespace" name="namespace" value={formData.namespace} onChange={handleInputChange} placeholder="MyApplication" />
                  </div>
                  <div className="d-grid">
                    <button type="submit" className="btn btn-lg text-white" disabled={loading} style={{ background: '#0d9488' }}>
                      <Search className="me-2" size={20} />
                      Start Analysis
                    </button>
                  </div>
                </form>
              )}
             
              {loading && (
                <div className="text-center py-5">
                  <div className="spinner-border mb-3" role="status" style={{ width: '3rem', height: '3rem', color: '#0d9488' }} />
                  <p className="text-muted"><Loader className="me-2" size={16} />Analyzing repository...</p>
                </div>
              )}
 
              {error && (
                <div className="alert alert-danger d-flex align-items-center mt-4">
                  <AlertCircle size={20} className="me-2" />
                  {error}
                </div>
              )}
 
              {analysisBundle && !loading && (
                <div className="text-center py-4">
                  <CheckCircle size={64} className="mb-3" style={{ color: '#10b981' }} />
                  <h3 className="fw-bold">Analysis Complete!</h3>
                  <p className="text-muted">The analysis bundle is ready. You can download it or proceed directly to project conversion.</p>
                  <div className="d-flex justify-content-center gap-3 mt-4">
                    <button className="btn btn-lg btn-outline-secondary" onClick={downloadAnalysisBundle}>
                      <Download size={20} className="me-2" />
                      Download Bundle
                    </button>
                    <button className="btn btn-lg text-white" style={{ background: '#0d9488' }} onClick={proceedToConversion}>
                      Proceed to Conversion
                      <ArrowRight size={20} className="ms-2" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
           <div className="text-center">
                <button
                className="btn btn-outline-secondary d-flex align-items-center mx-auto"
                onClick={onBackToHome}
              >
                <ArrowLeft size={16} className="me-2" />
                Back to Home
              </button>
            </div>
        </div>
      </div>
    </div>
  );
};
 
export default Analyzer;
 
 