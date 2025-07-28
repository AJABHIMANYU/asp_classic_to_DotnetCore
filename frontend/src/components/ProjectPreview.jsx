import React, { useState, useEffect } from 'react';
import { Download, Code, FileText, FolderOpen, ChevronRight, ArrowLeft, RefreshCw, Settings } from 'lucide-react';

const ProjectPreview = ({ namespace, initialFiles, onBackToHome, onStartNew }) => {
  const [generatedFiles, setGeneratedFiles] = useState(initialFiles || []);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileTree, setFileTree] = useState(null);

  useEffect(() => {
    if (generatedFiles && generatedFiles.length > 0) {
      setFileTree(buildFileTree(generatedFiles));
    }
  }, [generatedFiles]);

  const handleFileSelect = async (file) => {
    try {
      const response = await fetch(`http://localhost:8000/api/generate/file-content/${namespace}/${encodeURIComponent(file.path)}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedFile({ ...file, content: data.content || 'No content available' });
      } else {
        throw new Error('Failed to load file content.');
      }
    } catch (err) {
      console.error(err);
      setSelectedFile({ ...file, content: 'Error loading file content.' });
    }
  };
  
  const handleDownload = () => {
    // We create a temporary link to trigger the download.
    // This avoids a full page navigation which can be disruptive.
    const link = document.createElement('a');
    link.href = `http://localhost:8000/api/generate/download/${namespace}`;
    link.setAttribute('download', `${namespace}.zip`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };


  const buildFileTree = (files) => {
    const tree = {};
    if (!files) return tree;
    files.forEach(file => {
      const parts = file.path.replace(/\\/g, '/').split('/');
      let currentLevel = tree;
      parts.forEach((part, index) => {
        if (index === parts.length - 1) {
          currentLevel[part] = { type: 'file', data: file };
        } else {
          if (!currentLevel[part]) {
            currentLevel[part] = { type: 'folder', children: {} };
          }
          // Ensure we are traversing into the children object
          if (currentLevel[part].type === 'folder') {
             currentLevel = currentLevel[part].children;
          }
        }
      });
    });
    return tree;
  };

  const getFileIcon = (filePath) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    if (extension === 'cs') return <Code size={16} className="text-primary" />;
    if (extension === 'cshtml') return <FileText size={16} className="text-success" />;
    if (extension === 'json') return <FileText size={16} className="text-warning" />;
    if (extension === 'sln' || extension === 'csproj') return <Settings size={16} className="text-info" />;
    return <FileText size={16} className="text-muted" />;
  };

  // ### CORRECTED RECURSIVE COMPONENTS ###

  const FileTree = ({ node, onFileSelect, selectedFilePath, level = 0 }) => {
    // Sort so folders appear before files
    const sortedKeys = Object.keys(node).sort((a, b) => {
      const itemA = node[a];
      const itemB = node[b];
      if (itemA.type === 'folder' && itemB.type === 'file') return -1;
      if (itemA.type === 'file' && itemB.type === 'folder') return 1;
      return a.localeCompare(b);
    });

    return (
      <div className="list-group list-group-flush">
        {sortedKeys.map(key => {
          const item = node[key];
          if (item.type === 'folder') {
            // Correctly render the Folder component
            return <Folder key={key} name={key} folder={item} onFileSelect={onFileSelect} selectedFilePath={selectedFilePath} level={level} />;
          } else {
            // Render a file button
            return (
              <button
                key={item.data.path}
                className="list-group-item list-group-item-action border-0 d-flex align-items-center"
                style={{
                  paddingLeft: `${level * 20 + 15}px`,
                  backgroundColor: selectedFilePath === item.data.path ? '#e9f7f5' : 'transparent',
                  borderLeft: selectedFilePath === item.data.path ? '4px solid #0d9488' : 'none'
                }}
                onClick={() => onFileSelect(item.data)}
              >
                {getFileIcon(item.data.path)}
                <span className="ms-2 small">{key}</span>
              </button>
            );
          }
        })}
      </div>
    );
  };
  
  const Folder = ({ name, folder, onFileSelect, selectedFilePath, level }) => {
    const [isOpen, setIsOpen] = useState(true);
  
    return (
      <div>
        <button
          className="list-group-item list-group-item-action border-0 fw-bold d-flex align-items-center"
          style={{ paddingLeft: `${level * 20 + 15}px` }}
          onClick={() => setIsOpen(!isOpen)}
        >
          <ChevronRight size={16} className="me-2" style={{ transform: isOpen ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }} />
          <FolderOpen size={16} className="me-2 text-secondary" />
          {name}
        </button>
        {isOpen && (
          // Correctly render the FileTree component recursively
          <FileTree node={folder.children} onFileSelect={onFileSelect} selectedFilePath={selectedFilePath} level={level + 1} />
        )}
      </div>
    );
  };

  return (
    <div className="container py-5">
        <div className="text-center mb-4">
            <h2 className="fw-bold">Project Generation Complete!</h2>
            <p className="text-muted">Your project has been generated. You can preview the files below or download the complete ZIP archive.</p>
        </div>
        <div className="row g-4">
            <div className="col-lg-4">
                <div className="card shadow-sm h-100">
                    <div className="card-header fw-bold">Project Structure</div>
                    <div className="card-body p-0" style={{ height: '60vh', overflowY: 'auto' }}>
                        {fileTree ? <FileTree node={fileTree} onFileSelect={handleFileSelect} selectedFilePath={selectedFile?.path} /> : <div className="p-3 text-muted">Loading structure...</div>}
                    </div>
                </div>
            </div>
            <div className="col-lg-8">
                <div className="card shadow-sm h-100">
                    <div className="card-header fw-bold d-flex justify-content-between align-items-center">
                        Code Preview
                        <button className="btn btn-sm text-white" style={{ background: '#0d9488' }} onClick={handleDownload}>
                            <Download size={16} className="me-2" /> Download Project ZIP
                        </button>
                    </div>
                    <div className="card-body p-0" style={{ height: '60vh', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
                        {selectedFile ? (
                            <pre className="p-3 m-0 h-100"><code className="text-dark small" style={{whiteSpace: 'pre-wrap'}}>{selectedFile.content}</code></pre>
                        ) : (
                            <div className="d-flex align-items-center justify-content-center h-100 text-muted">Select a file to preview</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
        <div className="text-center mt-4">
            <button className="btn btn-outline-secondary me-2" onClick={onBackToHome}><ArrowLeft size={16} className="me-2" /> Back to Home</button>
            <button className="btn btn-outline-secondary" onClick={onStartNew}><RefreshCw size={16} className="me-2" /> Start New Conversion</button>
        </div>
    </div>
  );
};

export default ProjectPreview;