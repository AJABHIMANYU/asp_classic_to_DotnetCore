
// //new workflow
// import React, { useState } from 'react';
// import { ArrowRight, Loader } from 'lucide-react';
// import Analyzer from './components/Analyzer';
// import RefinePlan from './components/RefinePlan';
// import ProjectPreview from './components/ProjectPreview';

// // Define the different stages of the application
// const STAGES = {
//   HOME: 'home',
//   ANALYZING: 'analyzing', // Shows Analyzer component
//   AGGREGATING: 'aggregating', // Shows a loading screen
//   REFINING: 'refining', // Shows RefinePlan component
//   GENERATING: 'generating', // Shows a loading screen
//   PREVIEW: 'preview', // Shows ProjectPreview component
// };

// const App = () => {
//   const [stage, setStage] = useState(STAGES.HOME);
//   const [error, setError] = useState('');
  
//   // State to hold data between stages
//   const [sessionId, setSessionId] = useState(null);
//   const [namespace, setNamespace] = useState('MyWebApp');
//   const [editablePlan, setEditablePlan] = useState(null);
//   const [finalFiles, setFinalFiles] = useState([]);

//   const handleStartAnalysis = () => {
//     // Reset state for a new run
//     setError('');
//     setSessionId(null);
//     setEditablePlan(null);
//     setFinalFiles([]);
//     setStage(STAGES.ANALYZING);
//   };

//   const handleBackToHome = () => {
//     setStage(STAGES.HOME);
//   };

//   // Called from Analyzer when the initial raw analysis is complete
//   const handleInitialAnalysisComplete = async (analysisResult, chosenNamespace) => {
//     setStage(STAGES.AGGREGATING); // Show loading screen
//     setError('');
//     setSessionId(analysisResult.session_id);
//     setNamespace(chosenNamespace);
    
//     try {
//       const response = await fetch('http://localhost:8000/api/analyze/aggregate-project-plan', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(analysisResult.raw_file_analyses),
//       });

//       if (response.ok) {
//         const plan = await response.json();
//         setEditablePlan(plan);
//         setStage(STAGES.REFINING);
//       } else {
//         const errorData = await response.json().catch(() => ({ detail: 'Failed to aggregate project plan.' }));
//         throw new Error(errorData.detail);
//       }
//     } catch (err) {
//       setError(err.message || 'Network error during plan aggregation.');
//       setStage(STAGES.ANALYZING); // Go back to allow retry
//     }
//   };

//   // Called from RefinePlan when the user confirms their edits
//   const handlePlanConfirmed = async (refinedPlan) => {
//     setStage(STAGES.GENERATING);
//     setError('');

//     const formData = new FormData();
//     formData.append('namespace', namespace);
//     formData.append('session_id', sessionId);
//     formData.append('refined_plan', JSON.stringify(refinedPlan));

//     try {
//       const response = await fetch('http://localhost:8000/api/generate/generate-project-from-plan', {
//         method: 'POST',
//         body: formData,
//       });

//       if (!response.ok) {
//         const errorData = await response.json().catch(() => ({ detail: 'Project generation failed.' }));
//         throw new Error(errorData.detail);
//       }
      
//       const blob = await response.blob();
//       const url = window.URL.createObjectURL(blob);
//       const a = document.createElement('a');
//       a.href = url;
//       a.download = `${namespace}.zip`;
//       document.body.appendChild(a);
//       a.click();
//       a.remove();
//       window.URL.revokeObjectURL(url);
      
//       await fetchProjectStructure();

//     } catch (err) {
//       setError(err.message);
//       setStage(STAGES.REFINING);
//     }
//   };

//   const fetchProjectStructure = async () => {
//     try {
//       await new Promise(resolve => setTimeout(resolve, 500));
//       const response = await fetch(`http://localhost:8000/api/generate/project-structure/${namespace}`);
//       if (response.ok) {
//         const data = await response.json();
//         setFinalFiles(data.files || []);
//         setStage(STAGES.PREVIEW);
//       } else {
//         throw new Error("Could not fetch project structure for preview.");
//       }
//     } catch (err) {
//       setError(`${err.message} Your project ZIP file should have downloaded successfully.`);
//       setStage(STAGES.REFINING);
//     }
//   };
  
//   const LoadingScreen = ({ text }) => (
//     <div className="d-flex justify-content-center align-items-center min-vh-100">
//       <div className="text-center">
//         <div className="spinner-border mb-3" role="status" style={{ width: '3rem', height: '3rem', color: '#0d9488' }} />
//         <p className="text-muted"><Loader className="me-2" size={16} />{text}</p>
//       </div>
//     </div>
//   );
  

//   const renderContent = () => {
//     if (error) {
//       // Display error prominently
//       return (
//          <div className="container mt-4">
//              <div className="alert alert-danger">
//                  <strong>Error:</strong> {error}
//                  <button className="btn btn-sm btn-outline-danger ms-3" onClick={() => window.location.reload()}>Start Over</button>
//              </div>
//          </div>
//       );
//     }

//     switch (stage) {
//       case STAGES.ANALYZING:
//         return <Analyzer onBackToHome={handleBackToHome} onInitialAnalysisComplete={handleInitialAnalysisComplete} initialNamespace={namespace} />;
//       case STAGES.AGGREGATING:
//         return <LoadingScreen text="Aggregating analysis into a project plan..." />;
//       case STAGES.REFINING:
//         return <RefinePlan initialPlan={editablePlan} sessionId={sessionId} namespace={namespace} onPlanConfirmed={handlePlanConfirmed} onBack={() => setStage(STAGES.ANALYZING)} />;
//       case STAGES.GENERATING:
//         return <LoadingScreen text="Generating your project... This may take a moment." />;
//       case STAGES.PREVIEW:
//         return <ProjectPreview namespace={namespace} initialFiles={finalFiles} onBackToHome={handleBackToHome} onStartNew={handleStartAnalysis} />;
//       case STAGES.HOME:
//       default:
//         return (
//           <div className="min-vh-100" style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f0fdfa 50%, #ffffff 100%)' }}>
//             <div className="container py-5 d-flex flex-column justify-content-center" style={{minHeight: '80vh'}}>
//               <div className="text-center mb-5">
//                 <h1 className="display-3 fw-bold mb-4" style={{ background: 'linear-gradient(135deg, #0d9488, #14b8a6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
//                   ASP.NET Core Generator
//                 </h1>
//                 <p className="lead text-muted mb-5" style={{fontSize: '1.3rem'}}>
//                   Modernize legacy applications with AI-powered analysis and code generation.
//                 </p>
//               </div>
//               <div className="row justify-content-center">
//                 <div className="col-lg-5 col-md-6">
//                   <div className="card shadow-lg border-0 h-100">
//                     <div className="card-body p-4 d-flex flex-column text-center">
//                       <h3 className="h2 mb-2">Start Conversion</h3>
//                       <p className="mb-4 flex-grow-1">Analyze a Classic ASP repository and convert it into a modern, layered ASP.NET Core application.</p>
//                       <button className="btn btn-lg w-100 text-white" style={{ background: 'linear-gradient(135deg, #0d9488, #14b8a6)' }} onClick={handleStartAnalysis}>
//                         Start Analysis <ArrowRight size={20} className="ms-2" />
//                       </button>
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>
//         );
//     }
//   };

//   return (
//     <>
//       <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
//       {renderContent()}
//     </>
//   );
// };

// export default App;








//new workflow
import React, { useState } from 'react';
import { ArrowRight, Loader } from 'lucide-react';
import Analyzer from './components/Analyzer';
import RefinePlan from './components/RefinePlan';
import ProjectPreview from './components/ProjectPreview';

// Define the different stages of the application
const STAGES = {
  HOME: 'home',
  ANALYZING: 'analyzing', // Shows Analyzer component
  AGGREGATING: 'aggregating', // Shows a loading screen
  REFINING: 'refining', // Shows RefinePlan component
  GENERATING: 'generating', // Shows a loading screen
  PREVIEW: 'preview', // Shows ProjectPreview component
};

const App = () => {
  const [stage, setStage] = useState(STAGES.HOME);
  const [error, setError] = useState('');
  
  // State to hold data between stages
  const [sessionId, setSessionId] = useState(null);
  const [namespace, setNamespace] = useState('MyWebApp');
  const [editablePlan, setEditablePlan] = useState(null);
  const [finalFiles, setFinalFiles] = useState([]);

  const handleStartAnalysis = () => {
    // Reset state for a new run
    setError('');
    setSessionId(null);
    setEditablePlan(null);
    setFinalFiles([]);
    setStage(STAGES.ANALYZING);
  };

  const handleBackToHome = () => {
    setStage(STAGES.HOME);
  };

  // Called from Analyzer when the initial raw analysis is complete
  const handleInitialAnalysisComplete = async (analysisResult, chosenNamespace) => {
    setStage(STAGES.AGGREGATING); // Show loading screen
    setError('');
    setSessionId(analysisResult.session_id);
    setNamespace(chosenNamespace);
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze/aggregate-project-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisResult.raw_file_analyses),
      });

      if (response.ok) {
        const plan = await response.json();
        setEditablePlan(plan);
        setStage(STAGES.REFINING);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to aggregate project plan.' }));
        throw new Error(errorData.detail);
      }
    } catch (err) {
      setError(err.message || 'Network error during plan aggregation.');
      setStage(STAGES.ANALYZING); // Go back to allow retry
    }
  };

  // Called from RefinePlan when the user confirms their edits
  const handlePlanConfirmed = async (refinedPlan) => {
    setStage(STAGES.GENERATING);
    setError('');

    const formData = new FormData();
    formData.append('namespace', namespace);
    formData.append('session_id', sessionId);
    formData.append('refined_plan', JSON.stringify(refinedPlan));

    try {
      const response = await fetch('http://localhost:8000/api/generate/generate-project-from-plan', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Project generation failed.' }));
        throw new Error(errorData.detail);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${namespace}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      await fetchProjectStructure();

    } catch (err) {
      setError(err.message);
      setStage(STAGES.REFINING);
    }
  };

  const fetchProjectStructure = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      const response = await fetch(`http://localhost:8000/api/generate/project-structure/${namespace}`);
      if (response.ok) {
        const data = await response.json();
        setFinalFiles(data.files || []);
        setStage(STAGES.PREVIEW);
      } else {
        throw new Error("Could not fetch project structure for preview.");
      }
    } catch (err) {
      setError(`${err.message} Your project ZIP file should have downloaded successfully.`);
      setStage(STAGES.REFINING);
    }
  };
  
  const LoadingScreen = ({ text }) => (
    <div className="d-flex justify-content-center align-items-center min-vh-100">
      <div className="text-center">
        <div className="spinner-border mb-3" role="status" style={{ width: '3rem', height: '3rem', color: '#0d9488' }} />
        <p className="text-muted"><Loader className="me-2" size={16} />{text}</p>
      </div>
    </div>
  );
  

  const renderContent = () => {
    if (error) {
      // Display error prominently
      return (
         <div className="container mt-4">
             <div className="alert alert-danger">
                 <strong>Error:</strong> {error}
                 <button className="btn btn-sm btn-outline-danger ms-3" onClick={() => window.location.reload()}>Start Over</button>
             </div>
         </div>
      );
    }

    switch (stage) {
      case STAGES.ANALYZING:
        return <Analyzer onBackToHome={handleBackToHome} onInitialAnalysisComplete={handleInitialAnalysisComplete} initialNamespace={namespace} />;
      case STAGES.AGGREGATING:
        return <LoadingScreen text="Aggregating analysis into a project plan..." />;
      case STAGES.REFINING:
        return <RefinePlan initialPlan={editablePlan} sessionId={sessionId} namespace={namespace} onPlanConfirmed={handlePlanConfirmed} onBack={() => setStage(STAGES.ANALYZING)} />;
      case STAGES.GENERATING:
        return <LoadingScreen text="Generating your project... This may take a moment." />;
      case STAGES.PREVIEW:
        return <ProjectPreview namespace={namespace} initialFiles={finalFiles} onBackToHome={handleBackToHome} onStartNew={handleStartAnalysis} />;
      case STAGES.HOME:
      default:
        return (
          <div className="min-vh-100" style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f0fdfa 50%, #ffffff 100%)' }}>
            <div className="container py-5 d-flex flex-column justify-content-center" style={{minHeight: '80vh'}}>
              <div className="text-center mb-5">
                <h1 className="display-3 fw-bold mb-4" style={{ background: 'linear-gradient(135deg, #0d9488, #14b8a6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  ASP.NET Core Generator
                </h1>
                <p className="lead text-muted mb-5" style={{fontSize: '1.3rem'}}>
                  Modernize legacy applications with AI-powered analysis and code generation.
                </p>
              </div>
              <div className="row justify-content-center">
                <div className="col-lg-5 col-md-6">
                  <div className="card shadow-lg border-0 h-100">
                    <div className="card-body p-4 d-flex flex-column text-center">
                      <h3 className="h2 mb-2">Start Conversion</h3>
                      <p className="mb-4 flex-grow-1">Analyze a Classic ASP repository and convert it into a modern, layered ASP.NET Core application.</p>
                      <button className="btn btn-lg w-100 text-white" style={{ background: 'linear-gradient(135deg, #0d9488, #14b8a6)' }} onClick={handleStartAnalysis}>
                        Start Analysis <ArrowRight size={20} className="ms-2" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
      {renderContent()}
    </>
  );
};

export default App;