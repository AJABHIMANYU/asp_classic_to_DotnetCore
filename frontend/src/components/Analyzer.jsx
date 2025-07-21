import React, { useState } from 'react';
 
const Analyzer = ({ onBackToHome }) => {
  const [formData, setFormData] = useState({
    github_link: '',
    git_token: '',
    namespace: ''
  });
  const [jsonFile, setJsonFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
 
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
 
  const handleFileChange = (e) => {
    setJsonFile(e.target.files[0]);
  };
 
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
 
    const submitData = new FormData();
    submitData.append('github_link', formData.github_link);
    submitData.append('git_token', formData.git_token);
    submitData.append('namespace', formData.namespace);
    if (jsonFile) {
      submitData.append('json_file', jsonFile);
    }
 
    try {
      const response = await fetch('http://localhost:8000/api/analyze/generate-project-analysis', {
        method: 'POST',
        body: submitData,
      });
 
      const data = await response.json();
     
      if (response.ok) {
        setResult(data);
      } else {
        setError(data.detail || 'An error occurred during analysis');
      }
    } catch (err) {
      setError('Failed to connect to the server. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };
 
  const downloadResult = () => {
    if (result) {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'analysis_result.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };
 
  return (
    // <div className="min-vh-100" style={{ background: 'linear-gradient(135deg, #E0F7FA 30%, #FFFFFF 70%)' }}>
    <div className="min-vh-100 overflow-x-hidden" style={{ background: 'linear-gradient(135deg, #E0F7FA 30%, #FFFFFF 70%)' }}>

    {/* Header */}
      <nav className="navbar navbar-expand-lg shadow-sm" style={{ backgroundColor: '#20B2AA' }}>
        <div className="container">
          <div className="navbar-brand text-white fw-bold fs-3">
            <i className="fas fa-code-branch me-2"></i>
            Classic ASP to ASP.NET Analyzer
          </div>
        </div>
      </nav>
 
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            {/* Main Card */}
            <div className="card shadow-lg border-0 mb-4">
              <div className="card-header text-white text-center py-4" style={{ backgroundColor: '#008B8B' }}>
                <h2 className="mb-0">
                  <i className="fas fa-analytics me-2"></i>
                  Repository Analysis Tool
                </h2>
                <p className="mb-0 mt-2 opacity-90">
                  Convert your Classic ASP applications to modern ASP.NET with Onion Architecture
                </p>
              </div>
 
              <div className="card-body p-5" style={{ backgroundColor: '#FFFFFF' }}>
                <form onSubmit={handleSubmit}>
                  {/* GitHub Repository URL */}
                  <div className="mb-4">
                    <label htmlFor="github_link" className="form-label fw-semibold text-dark">
                      <i className="fab fa-github me-2" style={{ color: '#20B2AA' }}></i>
                      GitHub Repository URL *
                    </label>
                    <input
                      type="url"
                      className="form-control form-control-lg"
                      id="github_link"
                      name="github_link"
                      value={formData.github_link}
                      onChange={handleInputChange}
                      placeholder="https://github.com/username/repository"
                      required
                      style={{ borderColor: '#20B2AA', borderWidth: '2px' }}
                    />
                    <div className="form-text">
                      <i className="fas fa-info-circle me-1" style={{ color: '#20B2AA' }}></i>
                      Enter the full GitHub repository URL you want to analyze
                    </div>
                  </div>
 
                  {/* Git Token */}
                  <div className="mb-4">
                    <label htmlFor="git_token" className="form-label fw-semibold text-dark">
                      <i className="fas fa-key me-2" style={{ color: '#20B2AA' }}></i>
                      Git Token (Optional)
                    </label>
                    <input
                      type="password"
                      className="form-control form-control-lg"
                      id="git_token"
                      name="git_token"
                      value={formData.git_token}
                      onChange={handleInputChange}
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      style={{ borderColor: '#E0F7FA', borderWidth: '2px' }}
                    />
                    <div className="form-text">
                      <i className="fas fa-shield-alt me-1" style={{ color: '#20B2AA' }}></i>
                      Required only for private repositories
                    </div>
                  </div>
 
                  {/* Namespace */}
                  <div className="mb-4">
                    <label htmlFor="namespace" className="form-label fw-semibold text-dark">
                      <i className="fas fa-cube me-2" style={{ color: '#20B2AA' }}></i>
                      Namespace (Optional)
                    </label>
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      id="namespace"
                      name="namespace"
                      value={formData.namespace}
                      onChange={handleInputChange}
                      placeholder="MyApplication"
                      style={{ borderColor: '#E0F7FA', borderWidth: '2px' }}
                    />
                    <div className="form-text">
                      <i className="fas fa-tag me-1" style={{ color: '#20B2AA' }}></i>
                      Default namespace for the converted application
                    </div>
                  </div>
 
                  {/* JSON File Upload */}
                  <div className="mb-4">
                    <label htmlFor="json_file" className="form-label fw-semibold text-dark">
                      <i className="fas fa-file-code me-2" style={{ color: '#20B2AA' }}></i>
                      JSON Configuration File (Optional)
                    </label>
                    <input
                      type="file"
                      className="form-control form-control-lg"
                      id="json_file"
                      accept=".json"
                      onChange={handleFileChange}
                      style={{ borderColor: '#E0F7FA', borderWidth: '2px' }}
                    />
                    <div className="form-text">
                      <i className="fas fa-upload me-1" style={{ color: '#20B2AA' }}></i>
                      Upload additional configuration if needed
                    </div>
                  </div>
 
                  {/* Submit Button */}
                  <div className="d-grid mb-4">
                    <button
                      type="submit"
                      className="btn btn-lg fw-semibold text-white"
                      disabled={loading}
                      style={{
                        backgroundColor: '#20B2AA',
                        borderColor: '#20B2AA',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => e.target.style.backgroundColor = '#008B8B'}
                      onMouseLeave={(e) => e.target.style.backgroundColor = '#20B2AA'}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                          Analyzing Repository...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-search me-2"></i>
                          Start Analysis
                        </>
                      )}
                    </button>
                    {/* Home Button */}
                    <button
                      type="button"
                      className="btn btn-lg fw-semibold text-white mt-3"
                      style={{
                        backgroundColor: '#20B2AA',
                        borderColor: '#20B2AA',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => e.target.style.backgroundColor = '#008B8B'}
                      onMouseLeave={(e) => e.target.style.backgroundColor = '#20B2AA'}
                      onClick={onBackToHome}
                    >
                      <i className="fas fa-home me-2"></i>
                      Go to Home
                    </button>
                  </div>
                </form>
 
                {/* Error Display */}
                {error && (
                  <div className="alert alert-danger border-0 shadow-sm" role="alert">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    <strong>Error:</strong> {error}
                  </div>
                )}
 
                {/* Loading State */}
                {loading && (
                  <div className="text-center py-4">
                    <div className="spinner-border text-primary mb-3" style={{ color: '#20B2AA !important' }} role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="text-muted">
                      <i className="fas fa-cogs me-2"></i>
                      Analyzing your repository files...
                    </p>
                  </div>
                )}
 
                {/* Results Display */}
                {result && (
                  <div className="mt-4">
                    <div className="card border-0 shadow-sm" style={{ backgroundColor: '#E0F7FA' }}>
                      <div className="card-header text-white d-flex justify-content-between align-items-center" style={{ backgroundColor: '#20B2AA' }}>
                        <h5 className="mb-0">
                          <i className="fas fa-check-circle me-2"></i>
                          Analysis Complete
                        </h5>
                        <button
                          className="btn btn-light btn-sm"
                          onClick={downloadResult}
                        >
                          <i className="fas fa-download me-1"></i>
                          Download JSON
                        </button>
                      </div>
                      <div className="card-body">
                        <div className="row mb-3">
                          <div className="col-md-6">
                            <div className="d-flex align-items-center">
                              <i className="fas fa-link me-2" style={{ color: '#008B8B' }}></i>
                              <strong>Repository:</strong>
                            </div>
                            <p className="mb-0 ms-4 text-break">{result.repository_url}</p>
                          </div>
                          <div className="col-md-6">
                            <div className="d-flex align-items-center">
                              <i className="fas fa-file-alt me-2" style={{ color: '#008B8B' }}></i>
                              <strong>Files Analyzed:</strong>
                            </div>
                            <p className="mb-0 ms-4">{result.files_analyzed?.length || 0} files</p>
                          </div>
                        </div>
 
                        {result.files_analyzed && result.files_analyzed.length > 0 && (
                          <div>
                            <h6 className="fw-semibold mb-3" style={{ color: '#008B8B' }}>
                              <i className="fas fa-list me-2"></i>
                              Analyzed Files:
                            </h6>
                            <div className="row">
                              {result.files_analyzed.slice(0, 6).map((file, index) => (
                                <div key={index} className="col-md-6 mb-2">
                                  <div className="d-flex align-items-center p-2 rounded" style={{ backgroundColor: '#FFFFFF' }}>
                                    <i className="fas fa-file-code me-2" style={{ color: '#20B2AA' }}></i>
                                    <span className="text-truncate" title={file.file_name}>
                                      {file.file_name}
                                    </span>
                                  </div>
                                </div>
                              ))}
                              {result.files_analyzed.length > 6 && (
                                <div className="col-12">
                                  <p className="text-muted mb-0">
                                    <i className="fas fa-ellipsis-h me-1"></i>
                                    And {result.files_analyzed.length - 6} more files...
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
 
                        <div className="alert alert-info border-0 mt-3" style={{ backgroundColor: '#FFFFFF' }}>
                          <i className="fas fa-info-circle me-2" style={{ color: '#20B2AA' }}></i>
                          <strong>Next Steps:</strong> Download the JSON file to review the detailed analysis and conversion recommendations for each file.
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
 
            {/* Features Card */}
            <div className="card border-0 shadow-sm" style={{ backgroundColor: '#FFFFFF' }}>
              <div className="card-body p-4">
                <h5 className="card-title mb-4" style={{ color: '#008B8B' }}>
                  <i className="fas fa-star me-2"></i>
                  What This Tool Does
                </h5>
                <div className="row">
                  <div className="col-md-4 mb-3">
                    <div className="text-center">
                      <div className="mb-3">
                        <i className="fas fa-search fa-2x" style={{ color: '#20B2AA' }}></i>
                      </div>
                      <h6 className="fw-semibold">Code Analysis</h6>
                      <p className="text-muted small">Analyzes Classic ASP files and identifies their purpose and functionality</p>
                    </div>
                  </div>
                  <div className="col-md-4 mb-3">
                    <div className="text-center">
                      <div className="mb-3">
                        <i className="fas fa-layer-group fa-2x" style={{ color: '#20B2AA' }}></i>
                      </div>
                      <h6 className="fw-semibold">Architecture Mapping</h6>
                      <p className="text-muted small">Maps components to ASP.NET Onion Architecture layers</p>
                    </div>
                  </div>
                  <div className="col-md-4 mb-3">
                    <div className="text-center">
                      <div className="mb-3">
                        <i className="fas fa-lightbulb fa-2x" style={{ color: '#20B2AA' }}></i>
                      </div>
                      <h6 className="fw-semibold">Conversion Guide</h6>
                      <p className="text-muted small">Provides detailed recommendations for modern ASP.NET conversion</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
 
        {/* Footer */}
        <footer className="py-4 mt-5" style={{ backgroundColor: '#20B2AA' }}>
          <div className="container text-center text-white">
            <p className="mb-0">
              <i className="fas fa-code me-2"></i>
              Classic ASP to ASP.NET Analyzer - Modernize your legacy applications
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};
 
export default Analyzer;
 