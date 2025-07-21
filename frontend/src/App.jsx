// import React, { useState } from 'react';
 
// function App() {
//   const [file, setFile] = useState(null);
//   const [githubLink, setGithubLink] = useState('https://github.com/Aarzoo0/myClassicASPApp');
//   const [namespace, setNamespace] = useState('MyUserManagementApp');
//   const [message, setMessage] = useState('');
 
//   const handleFileChange = (event) => {
//     setFile(event.target.files[0]);
//   };
 
//   const handleSubmit = async (event) => {
//     event.preventDefault();
//     if (!file) {
//       setMessage('Please upload a JSON file.');
//       return;
//     }
 
//     const formData = new FormData();
//     formData.append('json_file', file);
//     formData.append('github_link', githubLink);
//     formData.append('namespace', namespace);
 
//     try {
//       const response = await fetch('http://localhost:8000/generate-project', {
//         method: 'POST',
//         body: formData,
//       });
 
//       if (response.ok) {
//         const blob = await response.blob();
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement('a');
//         a.href = url;
//         a.download = `${namespace}.zip`;
//         a.click();
//         window.URL.revokeObjectURL(url);
//         setMessage('Project generated and downloaded successfully!');
//       } else {
//         const error = await response.json();
//         setMessage(`Error: ${error.detail || 'Failed to generate project'}`);
//       }
//     } catch (error) {
//       setMessage(`Error: ${error.message}`);
//     }
//   };
 
//   return (
//     <div style={{ padding: '20px', fontFamily: 'Arial' }}>
//       <h1>Generate ASP.NET Core Project</h1>
//       <form onSubmit={handleSubmit}>
//         <div style={{ marginBottom: '10px' }}>
//           <label>Upload Analysis JSON File:</label>
//           <input
//             type="file"
//             accept=".json"
//             onChange={handleFileChange}
//             style={{ marginLeft: '10px' }}
//             required
//           />
//         </div>
//         <div style={{ marginBottom: '10px' }}>
//           <label>GitHub Link:</label>
//           <input
//             type="text"
//             value={githubLink}
//             onChange={(e) => setGithubLink(e.target.value)}
//             style={{ marginLeft: '10px', width: '300px' }}
//           />
//         </div>
//         <div style={{ marginBottom: '10px' }}>
//           <label>Namespace:</label>
//           <input
//             type="text"
//             value={namespace}
//             onChange={(e) => setNamespace(e.target.value)}
//             style={{ marginLeft: '10px', width: '300px' }}
//           />
//         </div>
//         <button type="submit" style={{ padding: '5px 10px' }}>
//           Generate Project
//         </button>
//       </form>
//       {message && <p style={{ color: message.includes('Error') ? 'red' : 'green' }}>{message}</p>}
//     </div>
//   );
// }
 
// export default App;
 








import React, { useState } from 'react';
import { Search, RefreshCw, ArrowRight, Code, FileText, Settings, CheckCircle } from 'lucide-react';
import Convert from './components/Convert';
import Analyzer from './components/Analyzer'
 
const App = () => {
  const [showConvert, setShowConvert] = useState(false);
  const [showAnalyzer, setShowAnalyzer] = useState(false);
 
  const handleAnalysisClick = () => {
    setShowAnalyzer(true);
  };
 
  const handleConversionClick = () => {
    setShowConvert(true);
  };
 
  const handleBackToHome = () => {
    setShowConvert(false);
    setShowAnalyzer(false);
  };
 
  return (
    <>
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
        rel="stylesheet"
        integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM"
        crossOrigin="anonymous"
      />
     
      {showAnalyzer ? (
        <Analyzer onBackToHome={handleBackToHome} />
      ) : showConvert ? (
        <Convert onBackToHome={handleBackToHome} />
      ) : (
        // <div className="min-vh-100" style={{background: 'linear-gradient(135deg, #ffffff 0%, #f0fdfa 50%, #ffffff 100%)'}}>
        <div className="min-vh-100 overflow-x-hidden" style={{background: 'linear-gradient(135deg, #ffffff 0%, #f0fdfa 50%, #ffffff 100%)'}}>

          <div className="container py-5">
            <div className="text-center mb-5">
              <h1 className="display-3 fw-bold mb-4" style={{
                background: 'linear-gradient(135deg, #0d9488, #14b8a6)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                ASP.NET Core Generator
              </h1>
              <p className="lead text-muted mb-5" style={{fontSize: '1.3rem'}}>
                Transform your Classic ASP applications into modern ASP.NET Core projects with clean architecture
              </p>
            </div>
 
            <div className="row justify-content-center g-4 mb-5">
              <div className="col-lg-5 col-md-6">
                <div className="card shadow-lg border-0 h-100" style={{transition: 'transform 0.3s ease'}}>
                  <div className="card-header text-white text-center py-4" style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)'}}>
                    <div className="mb-3">
                      <Search size={48} />
                    </div>
                    <h3 className="h2 mb-2">Step 1: Analysis</h3>
                    <p className="mb-0 opacity-75">Analyze your Classic ASP application</p>
                  </div>
                 
                  <div className="card-body p-4 d-flex flex-column" style={{backgroundColor: '#ffffff'}}>
                    <div className="mb-4 flex-grow-1">
                      <h5 className="fw-bold mb-3" style={{color: '#0d9488'}}>What it does:</h5>
                      <ul className="list-unstyled">
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Scans your Classic ASP codebase</span>
                        </li>
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Identifies database connections and queries</span>
                        </li>
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Maps business logic and data flow</span>
                        </li>
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Generates detailed analysis report</span>
                        </li>
                      </ul>
                    </div>
                   
                    <button
                      className="btn btn-lg w-100 d-flex align-items-center justify-content-center text-white"
                      style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)', border: 'none'}}
                      onClick={handleAnalysisClick}
                    >
                      Start Analysis
                      <ArrowRight size={20} className="ms-2" />
                    </button>
                  </div>
                </div>
              </div>
 
              <div className="col-lg-5 col-md-6">
                <div className="card shadow-lg border-0 h-100" style={{transition: 'transform 0.3s ease'}}>
                  <div className="card-header text-white text-center py-4" style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)'}}>
                    <div className="mb-3">
                      <RefreshCw size={48} />
                    </div>
                    <h3 className="h2 mb-2">Step 2: Conversion</h3>
                    <p className="mb-0 opacity-75">Convert to ASP.NET Core project</p>
                  </div>
                 
                  <div className="card-body p-4 d-flex flex-column" style={{backgroundColor: '#ffffff'}}>
                    <div className="mb-4 flex-grow-1">
                      <h5 className="fw-bold mb-3" style={{color: '#0d9488'}}>What it does:</h5>
                      <ul className="list-unstyled">
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Generates clean architecture structure</span>
                        </li>
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Creates controllers, services & repositories</span>
                        </li>
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Implements Entity Framework models</span>
                        </li>
                        <li className="mb-2 d-flex align-items-start">
                          <CheckCircle size={16} className="me-2 mt-1 flex-shrink-0" style={{color: '#0d9488'}} />
                          <span>Provides downloadable project</span>
                        </li>
                      </ul>
                    </div>
                   
                    <button
                      className="btn btn-lg w-100 d-flex align-items-center justify-content-center text-white"
                      style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)', border: 'none'}}
                      onClick={handleConversionClick}
                    >
                      Start Conversion
                      <ArrowRight size={20} className="ms-2" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
 
            <div className="row justify-content-center mb-5">
              <div className="col-lg-10">
                <div className="card shadow-lg border-0">
                  <div className="card-header text-white text-center py-3" style={{background: 'linear-gradient(135deg, #0d9488, #14b8a6)'}}>
                    <h4 className="mb-0">How It Works</h4>
                  </div>
                  <div className="card-body p-4" style={{backgroundColor: '#ffffff'}}>
                    <div className="row g-4">
                      <div className="col-md-4 text-center">
                        <div className="mb-3">
                          <Search size={40} style={{color: '#0d9488'}} />
                        </div>
                        <h5 className="fw-bold mb-2">1. Analyze</h5>
                        <p className="text-muted small">Upload your Classic ASP project and let our tool analyze the structure, dependencies, and business logic.</p>
                      </div>
                      <div className="col-md-4 text-center">
                        <div className="mb-3">
                          <Settings size={40} style={{color: '#0d9488'}} />
                        </div>
                        <h5 className="fw-bold mb-2">2. Configure</h5>
                        <p className="text-muted small">Review the analysis results and configure your conversion settings including namespace and architecture preferences.</p>
                      </div>
                      <div className="col-md-4 text-center">
                        <div className="mb-3">
                          <Code size={40} style={{color: '#0d9488'}} />
                        </div>
                        <h5 className="fw-bold mb-2">3. Generate</h5>
                        <p className="text-muted small">Get your complete ASP.NET Core project with clean architecture, ready for modern development practices.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
 
            <div className="row justify-content-center">
              <div className="col-lg-10">
                <div className="text-center mb-4">
                  <h3 className="fw-bold" style={{color: '#0d9488'}}>Why Choose Our Generator?</h3>
                  <p className="text-muted">Modern solutions for legacy applications</p>
                </div>
               
                <div className="row g-4">
                  <div className="col-md-6 col-lg-3">
                    <div className="text-center p-3">
                      <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px', backgroundColor: '#f0fdfa'}}>
                        <Code size={24} style={{color: '#0d9488'}} />
                      </div>
                      <h6 className="fw-bold">Clean Architecture</h6>
                      <p className="text-muted small">Domain-driven design with clear separation of concerns</p>
                    </div>
                  </div>
                  <div className="col-md-6 col-lg-3">
                    <div className="text-center p-3">
                      <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px', backgroundColor: '#f0fdfa'}}>
                        <FileText size={24} style={{color: '#0d9488'}} />
                      </div>
                      <h6 className="fw-bold">Best Practices</h6>
                      <p className="text-muted small">Followingಸ Following .NET Core conventions and modern patterns</p>
                    </div>
                  </div>
                  <div className="col-md-6 col-lg-3">
                    <div className="text-center p-3">
                      <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px', backgroundColor: '#f0fdfa'}}>
                        <Settings size={24} style={{color: '#0d9488'}} />
                      </div>
                      <h6 className="fw-bold">Automated</h6>
                      <p className="text-muted small">Reduces manual effort and potential conversion errors</p>
                    </div>
                  </div>
                  <div className="col-md-6 col-lg-3">
                    <div className="text-center p-3">
                      <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px', backgroundColor: '#f0fdfa'}}>
                        <RefreshCw size={24} style={{color: '#0d9488'}} />
                      </div>
                      <h6 className="fw-bold">Future-Ready</h6>
                      <p className="text-muted small">Built for scalability and modern deployment practices</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
 
            <div className="text-center mt-5 pt-5 border-top">
              <p className="text-muted">
                Transform your legacy Classic ASP applications into modern, maintainable ASP.NET Core solutions
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
 
export default App;
 