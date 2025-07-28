import React, { useState } from 'react';
import {
  Box, Typography, Button, TextField, IconButton, Accordion,
  AccordionSummary, AccordionDetails, Grid, Paper, Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  AddCircleOutline as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  ArrowBack as BackIcon,
  AccountTree as RepoIcon,
  Settings as ServiceIcon,
  DataObject as EntityIcon,
  ViewModule as ViewIcon,
  DeveloperBoard as ControllerIcon,
  SettingsApplications as NonFunctionalIcon,
  ChevronRight
} from '@mui/icons-material';
import { Loader } from 'lucide-react';

const RefinePlan = ({ initialPlan, sessionId, namespace, onPlanConfirmed, onBack }) => {
  const [plan, setPlan] = useState(initialPlan);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  // Generic handler for nested state updates
  const handlePlanChange = (path, value) => {
    setPlan(prevPlan => {
      const newPlan = JSON.parse(JSON.stringify(prevPlan)); // Deep copy
      let current = newPlan;
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
      }
      current[path[path.length - 1]] = value;
      return newPlan;
    });
  };

  // Generic handler to add an item to an array in the plan
  const handleAddItem = (path, newItem) => {
    setPlan(prevPlan => {
      const newPlan = JSON.parse(JSON.stringify(prevPlan));
      let current = newPlan;
      path.forEach(p => { current = current[p]; });
      current.push(newItem);
      return newPlan;
    });
  };

  // Generic handler to delete an item from an array in the plan
  const handleDeleteItem = (path, index) => {
    setPlan(prevPlan => {
      const newPlan = JSON.parse(JSON.stringify(prevPlan));
      let current = newPlan;
      path.forEach(p => { current = current[p]; });
      current.splice(index, 1);
      return newPlan;
    });
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError('');
    try {
      await onPlanConfirmed(plan);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during generation.');
      setIsGenerating(false);
    }
  };

  const sectionHeader = (title, icon) => (
    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: '#0f766e' }}>
      {icon}
      <span style={{ marginLeft: '8px' }}>{title}</span>
    </Typography>
  );

  return (
    <div className="container py-5">
      <div className="text-center mb-4">
        <h1 className="display-5 fw-bold">Review & Refine Project Plan</h1>
        <p className="lead text-muted">Inspect the AI-generated plan. You can edit names, add or remove items before final code generation.</p>
      </div>

      <Paper elevation={3} sx={{ p: 3, backgroundColor: '#f8fafc' }}>
        <Grid container spacing={3}>
          {/* Entities */}
          <Grid item xs={12}>
            {sectionHeader("Domain Entities", <EntityIcon />)}
            {plan.entities?.map((entity, eIndex) => (
              <Accordion key={eIndex} defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <TextField
                    variant="standard"
                    value={entity.name}
                    onChange={(e) => handlePlanChange(['entities', eIndex, 'name'], e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    sx={{ fontWeight: 'bold' }}
                  />
                </AccordionSummary>
                <AccordionDetails>
                  {entity.properties?.map((prop, pIndex) => (
                    <Box key={pIndex} display="flex" alignItems="center" mb={1}>
                      <TextField label="Property Name" size="small" variant="outlined" value={prop.name} onChange={(e) => handlePlanChange(['entities', eIndex, 'properties', pIndex, 'name'], e.target.value)} sx={{ mr: 1, flex: 1 }} />
                      <TextField label="Type" size="small" variant="outlined" value={prop.type} onChange={(e) => handlePlanChange(['entities', eIndex, 'properties', pIndex, 'type'], e.target.value)} sx={{ mr: 1, flex: 1 }} />
                      <Tooltip title="Delete Property">
                        <IconButton onClick={() => handleDeleteItem(['entities', eIndex, 'properties'], pIndex)} size="small"><DeleteIcon color="error" /></IconButton>
                      </Tooltip>
                    </Box>
                  ))}
                  <Button startIcon={<AddIcon />} size="small" onClick={() => handleAddItem(['entities', eIndex, 'properties'], { name: 'NewProperty', type: 'string' })}>Add Property</Button>
                </AccordionDetails>
              </Accordion>
            ))}
             <Button startIcon={<AddIcon />} sx={{mt: 1}} onClick={() => handleAddItem(['entities'], { name: 'NewEntity', properties: [] })}>Add Entity</Button>
          </Grid>
          
          {/* Controllers */}
          <Grid item xs={12} md={6}>
            {sectionHeader("Controllers", <ControllerIcon />)}
            {plan.controllers?.map((ctrl, cIndex) => (
              <Accordion key={cIndex}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>{ctrl.name}</AccordionSummary>
                <AccordionDetails>
                  {ctrl.actions?.map((action, aIndex) => (
                    <Box key={aIndex} display="flex" alignItems="center" mb={1}>
                       <TextField fullWidth label="Action Name" size="small" variant="outlined" value={action} onChange={(e) => handlePlanChange(['controllers', cIndex, 'actions', aIndex], e.target.value)} sx={{mr:1}} />
                       <Tooltip title="Delete Action">
                         <IconButton onClick={() => handleDeleteItem(['controllers', cIndex, 'actions'], aIndex)} size="small"><DeleteIcon color="error" /></IconButton>
                       </Tooltip>
                    </Box>
                  ))}
                  <Button startIcon={<AddIcon />} size="small" onClick={() => handleAddItem(['controllers', cIndex, 'actions'], 'NewAction')}>Add Action</Button>
                </AccordionDetails>
              </Accordion>
            ))}
          </Grid>

          {/* Views */}
          <Grid item xs={12} md={6}>
            {sectionHeader("Views", <ViewIcon />)}
            {plan.views?.map((view, vIndex) => (
              <Accordion key={vIndex}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>{view.name}</AccordionSummary>
                 <AccordionDetails>
                    <TextField fullWidth label="Associated Controller" size="small" variant="outlined" value={view.controller} onChange={(e) => handlePlanChange(['views', vIndex, 'controller'], e.target.value)} />
                 </AccordionDetails>
              </Accordion>
            ))}
          </Grid>

          {/* Services */}
          <Grid item xs={12} md={6}>
             {sectionHeader("Services", <ServiceIcon />)}
             {plan.services?.map((srv, sIndex) => (
               <Accordion key={sIndex}>
                 <AccordionSummary expandIcon={<ExpandMoreIcon />}>{srv.name}</AccordionSummary>
                 <AccordionDetails>
                   {srv.methods?.map((method, mIndex) => (
                     <Box key={mIndex} display="flex" alignItems="center" mb={1}>
                       <TextField fullWidth label="Method Name" size="small" variant="outlined" value={method} onChange={(e) => handlePlanChange(['services', sIndex, 'methods', mIndex], e.target.value)} sx={{mr:1}} />
                       <Tooltip title="Delete Method">
                          <IconButton onClick={() => handleDeleteItem(['services', sIndex, 'methods'], mIndex)} size="small"><DeleteIcon color="error" /></IconButton>
                       </Tooltip>
                     </Box>
                   ))}
                   <Button startIcon={<AddIcon />} size="small" onClick={() => handleAddItem(['services', sIndex, 'methods'], 'NewMethod')}>Add Method</Button>
                 </AccordionDetails>
               </Accordion>
             ))}
           </Grid>

          {/* Repositories */}
          <Grid item xs={12} md={6}>
            {sectionHeader("Repositories", <RepoIcon />)}
            {plan.repositories?.map((repo, rIndex) => (
               <Accordion key={rIndex}>
                 <AccordionSummary expandIcon={<ExpandMoreIcon />}>{repo.name}</AccordionSummary>
                 <AccordionDetails>
                   {repo.methods?.map((method, mIndex) => (
                     <Box key={mIndex} display="flex" alignItems="center" mb={1}>
                       <TextField fullWidth label="Method Name" size="small" variant="outlined" value={method} onChange={(e) => handlePlanChange(['repositories', rIndex, 'methods', mIndex], e.target.value)} sx={{mr:1}} />
                       <Tooltip title="Delete Method">
                         <IconButton onClick={() => handleDeleteItem(['repositories', rIndex, 'methods'], mIndex)} size="small"><DeleteIcon color="error" /></IconButton>
                       </Tooltip>
                     </Box>
                   ))}
                   <Button startIcon={<AddIcon />} size="small" onClick={() => handleAddItem(['repositories', rIndex, 'methods'], 'NewMethodAsync')}>Add Method</Button>
                 </AccordionDetails>
               </Accordion>
             ))}
          </Grid>
          
        </Grid>

        <Box mt={4} display="flex" justifyContent="center" gap={2}>
           <Button variant="outlined" color="secondary" onClick={onBack} disabled={isGenerating} startIcon={<BackIcon/>}>
             Back
           </Button>
           <Button 
            variant="contained" 
            onClick={handleGenerate} 
            disabled={isGenerating} 
            startIcon={isGenerating ? <Loader className="spinner-border spinner-border-sm"/> : <SaveIcon />}
            sx={{ backgroundColor: '#0d9488', '&:hover': { backgroundColor: '#0f766e' }}}
           >
             {isGenerating ? 'Generating Project...' : 'Confirm Plan & Generate'}
           </Button>
        </Box>
      </Paper>
    </div>
  );
};

export default RefinePlan;