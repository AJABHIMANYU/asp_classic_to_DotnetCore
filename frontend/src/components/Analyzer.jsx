
// //new flow

// import React, { useState } from 'react';
// import { ArrowRight, Search, AlertCircle, Loader, ArrowLeft } from 'lucide-react';

// const Analyzer = ({ onBackToHome, onInitialAnalysisComplete, initialNamespace }) => {
//   const [formData, setFormData] = useState({
//     github_link: '',
//     git_token: '',
//     namespace: initialNamespace || 'MyApplication'
//   });
  
//   const [loading, setLoading] = useState(false);
//   const [statusText, setStatusText] = useState('');
//   const [error, setError] = useState('');

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setFormData(prev => ({ ...prev, [name]: value }));
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setLoading(true);
//     setError('');
//     setStatusText('Cloning repository...');

//     const submitData = new FormData();
//     submitData.append('github_link', formData.github_link);
//     submitData.append('git_token', formData.git_token);

//     try {
//       const response = await fetch('http://localhost:8000/api/analyze/perform-initial-analysis', {
//         method: 'POST',
//         body: submitData,
//       });

//       if (response.ok) {
//         setStatusText('Analyzing files...');
//         const result = await response.json();
//         // Pass the full result up to App.jsx, which will handle the next step
//         onInitialAnalysisComplete(result, formData.namespace);
//       } else {
//         const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
//         setError(errorData.detail);
//         setLoading(false);
//       }
//     } catch (err) {
//       setError('Failed to connect to the server. Please ensure the backend is running.');
//       setLoading(false);
//     }
//     // Note: setLoading is only set to false on error, as success triggers a navigation in App.jsx
//   };

//   return (
//     <div className="container py-5">
//       <div className="row justify-content-center">
//         <div className="col-lg-8">
//           <div className="card shadow-lg border-0 mb-4">
//             <div className="card-header text-white text-center py-4" style={{ background: 'linear-gradient(135deg, #0d9488, #14b8a6)' }}>
//               <h2 className="mb-0">
//                 <Search className="me-2" />
//                 Repository Analysis
//               </h2>
//             </div>
//             <div className="card-body p-5">
//               {loading ? (
//                 <div className="text-center py-5">
//                   <div className="spinner-border mb-3" role="status" style={{ width: '3rem', height: '3rem', color: '#0d9488' }} />
//                   <p className="text-muted"><Loader className="me-2" size={16} />{statusText}</p>
//                 </div>
//               ) : (
//                 <form onSubmit={handleSubmit}>
//                   <div className="mb-4">
//                     <label htmlFor="github_link" className="form-label fw-bold">GitHub Repository URL *</label>
//                     <input type="url" className="form-control form-control-lg" id="github_link" name="github_link" value={formData.github_link} onChange={handleInputChange} placeholder="https://github.com/username/repository" required />
//                   </div>
//                   <div className="mb-4">
//                     <label htmlFor="git_token" className="form-label fw-bold">Git Token (Optional)</label>
//                     <input type="password" className="form-control form-control-lg" id="git_token" name="git_token" value={formData.git_token} onChange={handleInputChange} placeholder="ghp_xxxxxxxxxxxxxxxxxxxx" />
//                   </div>
//                   <div className="mb-4">
//                     <label htmlFor="namespace" className="form-label fw-bold">Project Namespace *</label>
//                     <input type="text" className="form-control form-control-lg" id="namespace" name="namespace" value={formData.namespace} onChange={handleInputChange} placeholder="MyApplication" required />
//                   </div>
//                   <div className="d-grid">
//                     <button type="submit" className="btn btn-lg text-white" disabled={loading} style={{ background: '#0d9488' }}>
//                       <Search className="me-2" size={20} />
//                       Start Analysis
//                     </button>
//                   </div>
//                 </form>
//               )}

//               {error && !loading && (
//                 <div className="alert alert-danger d-flex align-items-center mt-4">
//                   <AlertCircle size={20} className="me-2" />
//                   {error}
//                 </div>
//               )}
//             </div>
//           </div>
//           <div className="text-center">
//             <button className="btn btn-outline-secondary d-flex align-items-center mx-auto" onClick={onBackToHome}>
//               <ArrowLeft size={16} className="me-2" />
//               Back to Home
//             </button>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Analyzer;
































//new flow

import React, { useState } from 'react';
import { ArrowRight, Search, AlertCircle, Loader, ArrowLeft } from 'lucide-react';

const Analyzer = ({ onBackToHome, onInitialAnalysisComplete, initialNamespace }) => {
  const [formData, setFormData] = useState({
    github_link: '',
    git_token: '',
    namespace: initialNamespace || 'MyApplication'
  });
  
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setStatusText('Cloning repository...');

    const submitData = new FormData();
    submitData.append('github_link', formData.github_link);
    submitData.append('git_token', formData.git_token);

    try {
      const response = await fetch('http://localhost:8000/api/analyze/perform-initial-analysis', {
        method: 'POST',
        body: submitData,
      });

      if (response.ok) {
        setStatusText('Analyzing files...');
        const result = await response.json();
        // Pass the full result up to App.jsx, which will handle the next step
        onInitialAnalysisComplete(result, formData.namespace);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
        setError(errorData.detail);
        setLoading(false);
      }
    } catch (err) {
      setError('Failed to connect to the server. Please ensure the backend is running.');
      setLoading(false);
    }
    // Note: setLoading is only set to false on error, as success triggers a navigation in App.jsx
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
              {loading ? (
                <div className="text-center py-5">
                  <div className="spinner-border mb-3" role="status" style={{ width: '3rem', height: '3rem', color: '#0d9488' }} />
                  <p className="text-muted"><Loader className="me-2" size={16} />{statusText}</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div className="mb-4">
                    <label htmlFor="github_link" className="form-label fw-bold">GitHub Repository URL *</label>
                    <input type="url" className="form-control form-control-lg" id="github_link" name="github_link" value={formData.github_link} onChange={handleInputChange} placeholder="https://github.com/username/repository" required />
                  </div>
                  <div className="mb-4">
                    <label htmlFor="git_token" className="form-label fw-bold">Git Token (Optional)</label>
                    <input type="password" className="form-control form-control-lg" id="git_token" name="git_token" value={formData.git_token} onChange={handleInputChange} placeholder="ghp_xxxxxxxxxxxxxxxxxxxx" />
                  </div>
                  <div className="mb-4">
                    <label htmlFor="namespace" className="form-label fw-bold">Project Namespace *</label>
                    <input type="text" className="form-control form-control-lg" id="namespace" name="namespace" value={formData.namespace} onChange={handleInputChange} placeholder="MyApplication" required />
                  </div>
                  <div className="d-grid">
                    <button type="submit" className="btn btn-lg text-white" disabled={loading} style={{ background: '#0d9488' }}>
                      <Search className="me-2" size={20} />
                      Start Analysis
                    </button>
                  </div>
                </form>
              )}

              {error && !loading && (
                <div className="alert alert-danger d-flex align-items-center mt-4">
                  <AlertCircle size={20} className="me-2" />
                  {error}
                </div>
              )}
            </div>
          </div>
          <div className="text-center">
            <button className="btn btn-outline-secondary d-flex align-items-center mx-auto" onClick={onBackToHome}>
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