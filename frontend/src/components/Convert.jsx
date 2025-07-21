import React, { useState, useRef } from 'react';
import { Upload, Download, Code, FileText, Settings, CheckCircle, AlertCircle, Loader, FolderOpen, ChevronRight, ArrowLeft, RefreshCw } from 'lucide-react';
 
const Convert = ({ onBackToHome }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [jsonFile, setJsonFile] = useState(null);
  const [githubLink, setGithubLink] = useState('https://github.com/Aarzoo0/myClassicASPApp');
  const [namespace, setNamespace] = useState('MyUserManagementApp');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [projectStructure, setProjectStructure] = useState(null);
  const fileInputRef = useRef(null);
 
  const validateNamespace = (value) => {
    const regex = /^[a-zA-Z0-9_]+$/;
    return regex.test(value);
  };
 
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        setJsonFile(file);
        setError('');
      } else {
        setError('Please upload a valid JSON file');
        setJsonFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    }
  };
 
  const handleGenerateProject = async () => {
    if (!jsonFile) {
      setError('Please upload a JSON file first');
      return;
    }
 
    if (!validateNamespace(namespace)) {
      setError('Invalid namespace. Use alphanumeric characters and underscores only.');
      return;
    }
 
    setIsGenerating(true);
    setError('');
    setSuccess('');
 
    try {
      const formData = new FormData();
      formData.append('json_file', jsonFile);
      formData.append('github_link', githubLink);
      formData.append('namespace', namespace);
 
      const response = await fetch('http://localhost:8000/api/generate/generate-project', {
        method: 'POST',
        body: formData,
      });
 
      if (response.ok) {
        const structureResponse = await fetch(`http://localhost:8000/api/generate/project-structure/${namespace}`);
        if (structureResponse.ok) {
          const structure = await structureResponse.json();
          setProjectStructure(structure);
          setGeneratedFiles(structure.files || []);
          setCurrentStep(3);
          setSuccess('Project generated successfully!');
        } else {
          const errorData = await structureResponse.json().catch(() => ({ detail: 'Failed to fetch project structure' }));
          setError(`Failed to load project structure: ${errorData.detail || structureResponse.statusText}`);
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        setError(`Generation failed: ${errorData.detail || response.statusText}`);
      }
    } catch (err) {
      setError(`Network error: ${err.message}. Is the backend server running at http://localhost:8000?`);
    } finally {
      setIsGenerating(false);
    }
  };
 
  const handleFileSelect = async (file) => {
    try {
      const response = await fetch(`http://localhost:8000/api/generate/file-content/${namespace}/${encodeURIComponent(file.path)}`);
      if (response.ok) {
        const data = await response.json();
        if (data && typeof data.content === 'string') {
          setSelectedFile({ ...file, content: data.content });
        } else {
          setError('Invalid file content received from server');
          setSelectedFile({ ...file, content: 'No content available' });
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to load file content' }));
        setError(`Failed to load file: ${errorData.detail || response.statusText}`);
      }
    } catch (err) {
      setError(`Error loading file: ${err.message}. Is the backend server running?`);
    }
  };
 
  const handleDownload = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/generate/download/${namespace}`, {
        method: 'GET',
      });
 
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${namespace}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        setSuccess('Project downloaded successfully!');
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Download failed' }));
        setError(`Download failed: ${errorData.detail || response.statusText}`);
      }
    } catch (err) {
      setError(`Download error: ${err.message}. Is the backend server running?`);
    }
  };
 
  const handleStartNewConversion = () => {
    setCurrentStep(1);
    setJsonFile(null);
    setGithubLink('https://github.com/Aarzoo0/myClassicASPApp');
    setNamespace('MyUserManagementApp');
    setGeneratedFiles([]);
    setSelectedFile(null);
    setError('');
    setSuccess('');
    setProjectStructure(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
 
  const getFileIcon = (filePath) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    const fileName = filePath.split('/').pop();
   
    if (extension === 'cs') {
      if (fileName.includes('Controller')) return { icon: <Code style={{color: '#0d9488'}} size={16} />, color: 'text-teal' };
      if (fileName.includes('Service')) return { icon: <Settings style={{color: '#14b8a6'}} size={16} />, color: 'text-teal' };
      if (fileName.includes('Repository')) return { icon: <Code style={{color: '#5eead4'}} size={16} />, color: 'text-teal' };
      if (fileName.includes('DbContext')) return { icon: <Settings style={{color: '#0f766e'}} size={16} />, color: 'text-teal' };
      return { icon: <FileText className="text-secondary" size={16} />, color: 'text-secondary' };
    }
    if (extension === 'cshtml') return { icon: <FileText style={{color: '#0d9488'}} size={16} />, color: 'text-teal' };
    if (extension === 'json') return { icon: <FileText style={{color: '#14b8a6'}} size={16} />, color: 'text-teal' };
    if (extension === 'sln' || extension === 'csproj') return { icon: <FolderOpen style={{color: '#0d9488'}} size={16} />, color: 'text-teal' };
   
    return { icon: <FileText className="text-muted" size={16} />, color: 'text-muted' };
  };
 
  const getLayerFromPath = (filePath) => {
    if (filePath.includes('/Domain/')) return 'Domain';
    if (filePath.includes('/Application/')) return 'Application';
    if (filePath.includes('/Infrastructure/')) return 'Infrastructure';
    if (filePath.includes('/Presentation/')) return 'Presentation';
    return 'Root';
  };
 
  const getLayerBadgeClass = (layer) => {
    switch (layer) {
      case 'Domain': return 'badge bg-teal-dark text-white';
      case 'Application': return 'badge bg-teal text-white';
      case 'Infrastructure': return 'badge bg-teal-light text-white';
      case 'Presentation': return 'badge bg-teal-darker text-white';
      default: return 'badge bg-secondary';
    }
  };
 
  const renderStep1 = () => (
    <div className="row justify-content-center">
      <div className="col-lg-8 col-xl-6">
        <div className="card shadow-lg border-0">
          <div className="card-header text-white" style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)'}}>
            <div className="d-flex align-items-center">
              <Upload size={24} className="me-3" />
              <div>
                <h2 className="h4 mb-1">Upload Configuration</h2>
                <p className="mb-0 opacity-75">Start by uploading your project analysis file</p>
              </div>
            </div>
          </div>
         
          <div className="card-body p-4" style={{backgroundColor: '#ffffff'}}>
            <div className="mb-4">
              <label className="form-label fw-bold">
                JSON Analysis File <span className="text-danger">*</span>
              </label>
              <input
                ref={fileInputRef}
                type="file"
                className="form-control form-control-lg"
                accept=".json"
                onChange={handleFileUpload}
              />
              {jsonFile && (
                <div className="mt-3 p-3 border rounded" style={{backgroundColor: '#f0fdfa', borderColor: '#5eead4 !important'}}>
                  <div className="d-flex align-items-center" style={{color: '#0d9488'}}>
                    <CheckCircle size={16} className="me-2" />
                    <div className="fw-medium">{jsonFile.name}</div>
                  </div>
                </div>
              )}
              <div className="form-text">Upload the JSON file containing the project analysis</div>
            </div>
 
            <div className="mb-4">
              <label className="form-label fw-bold">GitHub Repository URL</label>
              <input
                type="url"
                className="form-control form-control-lg"
                value={githubLink}
                onChange={(e) => setGithubLink(e.target.value)}
                placeholder="https://github.com/username/repository"
              />
              <div className="form-text">URL of the Classic ASP source repository</div>
            </div>
 
            <div className="mb-4">
              <label className="form-label fw-bold">
                Project Namespace <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                className="form-control form-control-lg"
                value={namespace}
                onChange={(e) => setNamespace(e.target.value)}
                placeholder="MyUserManagementApp"
              />
              <div className="form-text">Use alphanumeric characters and underscores only</div>
            </div>
 
            <button
              className="btn btn-lg w-100 d-flex align-items-center justify-content-center text-white"
              style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)', border: 'none'}}
              onClick={() => setCurrentStep(2)}
              disabled={!jsonFile || !namespace || !validateNamespace(namespace)}
            >
              Continue to Generation
              <ChevronRight size={20} className="ms-2" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
 
  const renderStep2 = () => (
    <div className="row justify-content-center">
      <div className="col-lg-8 col-xl-6">
        <div className="card shadow-lg border-0">
          <div className="card-header text-white" style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)'}}>
            <div className="d-flex align-items-center">
              <Settings size={24} className="me-3" />
              <div>
                <h2 className="h4 mb-1">Generate Project</h2>
                <p className="mb-0 opacity-75">Review your configuration and generate the ASP.NET Core project</p>
              </div>
            </div>
          </div>
         
          <div className="card-body p-4" style={{backgroundColor: '#ffffff'}}>
            <div className="bg-light rounded p-4 mb-4">
              <h5 className="fw-bold mb-3">Configuration Summary</h5>
              <div className="row g-3">
                <div className="col-sm-4 fw-medium text-muted">JSON File:</div>
                <div className="col-sm-8 fw-medium">{jsonFile?.name || 'None'}</div>
                <div className="col-sm-4 fw-medium text-muted">GitHub URL:</div>
                <div className="col-sm-8 fw-medium text-break">{githubLink}</div>
                <div className="col-sm-4 fw-medium text-muted">Namespace:</div>
                <div className="col-sm-8 fw-medium">{namespace}</div>
              </div>
            </div>
 
            <div className="text-center">
              {isGenerating ? (
                <div className="py-5">
                  <div className="spinner-border mb-3" role="status" style={{width: '3rem', height: '3rem', color: '#0d9488'}}>
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <p className="text-muted d-flex align-items-center justify-content-center">
                    <Loader className="me-2" size={16} />
                    Generating ASP.NET Core project... This may take a few minutes.
                  </p>
                </div>
              ) : (
                <div>
                  <button
                    className="btn btn-lg mb-3 px-5 text-white"
                    style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)', border: 'none'}}
                    onClick={handleGenerateProject}
                    disabled={isGenerating}
                  >
                    <Settings size={20} className="me-2" />
                    Generate Project
                  </button>
                  <div>
                    <button
                      className="btn btn-link text-muted"
                      onClick={() => setCurrentStep(1)}
                    >
                      ← Back to Configuration
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
 
  const renderStep3 = () => (
    <div className="row g-4">
      <div className="col-lg-4">
        <div className="card shadow-lg border-0 h-100">
          <div className="card-header text-white" style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)'}}>
            <h5 className="mb-0 d-flex align-items-center">
              <FolderOpen size={20} className="me-2" />
              Project Structure
            </h5>
          </div>
          <div className="card-body p-0" style={{height: '600px', overflowY: 'auto', backgroundColor: '#ffffff'}}>
            {generatedFiles.length > 0 ? (
              <div className="list-group list-group-flush">
                {generatedFiles.map((file, index) => {
                  const { icon } = getFileIcon(file.path);
                  const layer = getLayerFromPath(file.path);
                 
                  return (
                    <button
                      key={index}
                      className={`list-group-item list-group-item-action border-0 ${
                        selectedFile?.path === file.path ? 'active' : ''
                      }`}
                      style={{
                        backgroundColor: selectedFile?.path === file.path ? '#f0fdfa' : '#ffffff',
                        borderLeft: selectedFile?.path === file.path ? '4px solid #0d9488' : 'none'
                      }}
                      onClick={() => handleFileSelect(file)}
                    >
                      <div className="d-flex align-items-start">
                        <div className="me-3 mt-1">{icon}</div>
                        <div className="flex-grow-1 text-start">
                          <div className="fw-medium small mb-1">
                            {file.path.split('/').pop()}
                          </div>
                          <div className="text-muted small mb-2" style={{fontSize: '0.75rem'}}>
                            {file.path}
                          </div>
                          <span className={getLayerBadgeClass(layer)} style={{fontSize: '0.7rem'}}>
                            {layer}
                          </span>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="d-flex align-items-center justify-content-center h-100 text-muted">
                <div className="text-center">
                  <FolderOpen size={48} className="mb-3 opacity-50" />
                  <p>No files generated yet</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
     
      <div className="col-lg-8">
        <div className="card shadow-lg border-0 h-100">
          <div className="card-header bg-dark text-white d-flex justify-content-between align-items-center">
            <h5 className="mb-0 d-flex align-items-center">
              <Code size={20} className="me-2" />
              Code Preview
            </h5>
            <button
              className="btn btn-sm text-white"
              style={{backgroundColor: '#0d9488'}}
              onClick={handleDownload}
            >
              <Download size={16} className="me-2" />
              Download ZIP
            </button>
          </div>
          <div className="card-body p-0" style={{height: '600px', backgroundColor: '#ffffff'}}>
            {selectedFile ? (
              <div className="h-100 d-flex flex-column">
                <div className="bg-light px-3 py-2 border-bottom">
                  <div className="small text-muted">
                    {selectedFile.path}
                    <span className={getLayerBadgeClass(getLayerFromPath(selectedFile.path))} style={{fontSize: '0.7rem', marginLeft: '0.5rem'}}>
                      {getLayerFromPath(selectedFile.path)} Layer
                    </span>
                  </div>
                </div>
                <div className="flex-grow-1 overflow-auto">
                  <pre className="p-3 mb-0 h-100 bg-light">
                    <code className="text-dark small">
                      {typeof selectedFile.content === 'string' ? selectedFile.content : 'Loading...'}
                    </code>
                  </pre>
                </div>
              </div>
            ) : (
              <div className="d-flex align-items-center justify-content-center h-100 text-muted">
                <div className="text-center">
                  <FileText size={64} className="mb-3 opacity-50" />
                  <h5 className="fw-medium mb-2">Select a file to preview</h5>
                  <p className="small">Choose a file from the project structure to view its content</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
 
  return (
    <>
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
        rel="stylesheet"
        integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM"
        crossOrigin="anonymous"
      />
     
      <div className="min-vh-100" style={{background: 'linear-gradient(135deg, #ffffff 0%, #f0fdfa 50%, #ffffff 100%)'}}>
        <div className="container py-5">
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold mb-3" style={{
              background: 'linear-gradient(135deg, #0d9488, #14b8a6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              ASP.NET Core Generator
            </h1>
            <p className="lead text-muted">
              Transform your Classic ASP applications into modern ASP.NET Core projects with clean architecture
            </p>
          </div>
 
          <div className="mb-5">
            <div className="d-flex justify-content-center align-items-center flex-wrap gap-4">
              {[
                { step: 1, label: 'Upload', icon: Upload },
                { step: 2, label: 'Generate', icon: Settings },
                { step: 3, label: 'Preview & Download', icon: Download }
              ].map(({ step, label, icon: Icon }, index) => (
                <React.Fragment key={step}>
                  <div className="d-flex align-items-center">
                    <div className={`rounded-circle d-flex align-items-center justify-content-center fw-bold ${
                      currentStep >= step
                        ? 'text-white shadow'
                        : 'bg-light text-muted'
                    }`} style={{
                      width: '48px',
                      height: '48px',
                      backgroundColor: currentStep >= step ? '#0d9488' : undefined
                    }}>
                      {currentStep > step ? <CheckCircle size={20} /> : <Icon size={20} />}
                    </div>
                    <div className="ms-3">
                      <div className="small fw-medium text-muted">{label}</div>
                    </div>
                  </div>
                  {index < 2 && (
                    <div className={`d-none d-md-block ${
                      currentStep > step ? '' : 'bg-light'
                    }`} style={{
                      width: '60px',
                      height: '2px',
                      backgroundColor: currentStep > step ? '#0d9488' : undefined
                    }} />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
 
          {error && (
            <div className="row justify-content-center mb-4">
              <div className="col-lg-8">
                <div className="alert alert-danger d-flex align-items-center alert-dismissible" role="alert">
                  <AlertCircle size={20} className="me-2 flex-shrink-0" />
                  <div className="flex-grow-1">{error}</div>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setError('')}
                    aria-label="Close"
                  ></button>
                </div>
              </div>
            </div>
          )}
 
          {success && (
            <div className="row justify-content-center mb-4">
              <div className="col-lg-8">
                <div className="alert d-flex align-items-center alert-dismissible" role="alert" style={{backgroundColor: '#f0fdfa', borderColor: '#5eead4', color: '#0d9488'}}>
                  <CheckCircle size={20} className="me-2 flex-shrink-0" />
                  <div className="flex-grow-1">{success}</div>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setSuccess('')}
                    aria-label="Close"
                  ></button>
                </div>
              </div>
            </div>
          )}
 
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
 
          <div className="text-center mt-5 pt-4 border-top">
            <div className="d-flex justify-content-center gap-3 mb-3">
              <button
                className="btn btn-outline-secondary d-flex align-items-center"
                onClick={onBackToHome}
              >
                <ArrowLeft size={16} className="me-2" />
                Back to Home
              </button>
              <button
                className="btn btn-outline-secondary d-flex align-items-center"
                onClick={handleStartNewConversion}
              >
                <RefreshCw size={16} className="me-2" />
                Start New Conversion
              </button>
            </div>
            <p className="text-muted">
              Convert your Classic ASP applications to modern ASP.NET Core with clean architecture patterns
            </p>
          </div>
        </div>
      </div>
    </>
  );
};
 
export default Convert;
 