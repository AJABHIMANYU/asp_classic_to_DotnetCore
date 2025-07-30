// import React, { useState } from 'react';
// import {
//   Box, Typography, Button, TextField, IconButton, Accordion,
//   AccordionSummary, AccordionDetails, Grid, Paper, Tooltip, Divider, Chip
// } from '@mui/material';
// import {
//   ExpandMore as ExpandMoreIcon,
//   AddCircleOutline as AddIcon,
//   DeleteOutline as DeleteIcon,
//   Save as SaveIcon,
//   ArrowBack as BackIcon,
//   AccountTree as RepoIcon,
//   Settings as ServiceIcon,
//   DataObject as EntityIcon,
//   ViewModule as ViewIcon,
//   DeveloperBoard as ControllerIcon
// } from '@mui/icons-material';
// import { Loader } from 'lucide-react';

// // Sub-component for editing a single entity
// const EntityEditor = ({ entity, eIndex, handlePlanChange, handleAddItem, handleDeleteItem }) => (
//   <Accordion defaultExpanded>
//     <AccordionSummary expandIcon={<ExpandMoreIcon />}>
//       <Typography sx={{ fontWeight: 'bold' }}>{entity.name || "Unnamed Entity"}</Typography>
//     </AccordionSummary>
//     <AccordionDetails sx={{ backgroundColor: '#fff' }}>
//       <TextField
//         label="Entity Name"
//         size="small"
//         variant="outlined"
//         value={entity.name}
//         onChange={(e) => handlePlanChange(['entities', eIndex, 'name'], e.target.value)}
//         fullWidth
//         sx={{ mb: 2 }}
//       />
//       <Typography variant="subtitle2" sx={{ mb: 1 }}>Properties</Typography>
//       {entity.properties?.map((prop, pIndex) => (
//         <Box key={pIndex} display="flex" alignItems="center" mb={1} gap={1}>
//           <TextField label="Property Name" size="small" variant="outlined" value={prop.name} onChange={(e) => handlePlanChange(['entities', eIndex, 'properties', pIndex, 'name'], e.target.value)} sx={{ flex: 1 }} />
//           <TextField label="Type" size="small" variant="outlined" value={prop.type} onChange={(e) => handlePlanChange(['entities', eIndex, 'properties', pIndex, 'type'], e.target.value)} sx={{ flex: 1 }} />
//           <Tooltip title="Delete Property">
//             <IconButton onClick={() => handleDeleteItem(['entities', eIndex, 'properties'], pIndex)} size="small"><DeleteIcon color="error" /></IconButton>
//           </Tooltip>
//         </Box>
//       ))}
//       <Button startIcon={<AddIcon />} size="small" onClick={() => handleAddItem(['entities', eIndex, 'properties'], { name: 'NewProperty', type: 'string' })}>Add Property</Button>
//     </AccordionDetails>
//   </Accordion>
// );

// // Generic sub-component for editing components with a name and a list of strings (methods/actions)
// const ComponentEditor = ({ component, cIndex, path, nameLabel, listLabel, listName, handlePlanChange, handleAddItem, handleDeleteItem, newItemValue }) => (
//   <Accordion>
//     <AccordionSummary expandIcon={<ExpandMoreIcon />}>
//       <Typography>{component.name || `Unnamed ${nameLabel}`}</Typography>
//     </AccordionSummary>
//     <AccordionDetails sx={{ backgroundColor: '#fff' }}>
//        <TextField
//           label={`${nameLabel} Name`}
//           size="small"
//           variant="outlined"
//           value={component.name}
//           onChange={(e) => handlePlanChange([path, cIndex, 'name'], e.target.value)}
//           fullWidth
//           sx={{ mb: 2 }}
//         />
//         <Typography variant="subtitle2" sx={{ mb: 1 }}>{listLabel}</Typography>
//         {component[listName]?.map((item, iIndex) => (
//           <Box key={iIndex} display="flex" alignItems="center" mb={1} gap={1}>
//             <TextField fullWidth label="Name" size="small" variant="outlined" value={item} onChange={(e) => handlePlanChange([path, cIndex, listName, iIndex], e.target.value)} />
//             <Tooltip title={`Delete ${listLabel.slice(0, -1)}`}>
//               <IconButton onClick={() => handleDeleteItem([path, cIndex, listName], iIndex)} size="small"><DeleteIcon color="error" /></IconButton>
//             </Tooltip>
//           </Box>
//         ))}
//       <Button startIcon={<AddIcon />} size="small" onClick={() => handleAddItem([path, cIndex, listName], newItemValue)}>Add {listLabel.slice(0, -1)}</Button>
//     </AccordionDetails>
//   </Accordion>
// );


// const RefinePlan = ({ initialPlan, sessionId, namespace, onPlanConfirmed, onBack }) => {
//   const [plan, setPlan] = useState(initialPlan);
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [error, setError] = useState('');

//   // A more robust state updater that avoids re-rendering issues
//   const handlePlanChange = (path, value) => {
//     setPlan(prevPlan => {
//       const newPlan = JSON.parse(JSON.stringify(prevPlan));
//       let current = newPlan;
//       for (let i = 0; i < path.length - 1; i++) {
//         current = current[path[i]];
//       }
//       current[path[path.length - 1]] = value;
//       return newPlan;
//     });
//   };

//   const handleAddItem = (path, newItem) => {
//     setPlan(prevPlan => {
//       const newPlan = JSON.parse(JSON.stringify(prevPlan));
//       let current = newPlan;
//       for(const p of path) { current = current[p]; }
//       if (Array.isArray(current)) {
//         current.push(newItem);
//       }
//       return newPlan;
//     });
//   };

//   const handleDeleteItem = (path, index) => {
//     setPlan(prevPlan => {
//       const newPlan = JSON.parse(JSON.stringify(prevPlan));
//       let current = newPlan;
//       for(const p of path) { current = current[p]; }
//       if (Array.isArray(current)) {
//         current.splice(index, 1);
//       }
//       return newPlan;
//     });
//   };

//   const handleGenerate = async () => {
//     setIsGenerating(true);
//     setError('');
//     try {
//       await onPlanConfirmed(plan);
//     } catch (err) {
//       setError(err.message || 'An unexpected error occurred during generation.');
//       setIsGenerating(false);
//     }
//   };

//   const sectionHeader = (title, icon) => (
//     <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 1, color: '#0f766e' }}>
//       {icon}
//       <span style={{ marginLeft: '8px' }}>{title}</span>
//     </Typography>
//   );

//   return (
//     <div className="container py-5">
//       <div className="text-center mb-4">
//         <h1 className="display-5 fw-bold">Review & Refine Project Plan</h1>
//         <p className="lead text-muted">Inspect the AI-generated plan. You can edit, add, or remove items before final code generation.</p>
//       </div>

//       <Paper elevation={3} sx={{ p: { xs: 2, md: 3 }, backgroundColor: '#f8fafc' }}>
//         <Grid container spacing={3}>
//           {/* Entities */}
//           <Grid item xs={12}>
//             {sectionHeader("Domain Entities", <EntityIcon />)}
//             {plan.entities?.map((entity, eIndex) => (
//               <EntityEditor key={eIndex} entity={entity} eIndex={eIndex} handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} />
//             ))}
//              <Button startIcon={<AddIcon />} sx={{mt: 1}} onClick={() => handleAddItem(['entities'], { name: 'NewEntity', properties: [{name: 'Id', type: 'int'}] })}>Add Entity</Button>
//           </Grid>
          
//           <Grid item xs={12}><Divider/></Grid>

//           {/* Controllers & Views */}
//           <Grid item xs={12} md={6}>
//             {sectionHeader("Controllers", <ControllerIcon />)}
//             {plan.controllers?.map((ctrl, cIndex) => (
//               <ComponentEditor key={cIndex} component={ctrl} cIndex={cIndex} path="controllers" nameLabel="Controller" listLabel="Actions" listName="actions" handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} newItemValue="NewAction" />
//             ))}
//              <Button startIcon={<AddIcon />} sx={{mt: 1}} onClick={() => handleAddItem(['controllers'], { name: 'NewController', actions: ['Index'] })}>Add Controller</Button>
//           </Grid>
//           <Grid item xs={12} md={6}>
//             {sectionHeader("Views", <ViewIcon />)}
//             {plan.views?.map((view, vIndex) => (
//               <Accordion key={vIndex}>
//                 <AccordionSummary expandIcon={<ExpandMoreIcon />}>
//                   <Typography>{view.name || "Unnamed View"}</Typography>
//                 </AccordionSummary>
//                 <AccordionDetails sx={{ backgroundColor: '#fff' }}>
//                   <TextField label="View Name (.cshtml)" size="small" variant="outlined" value={view.name} onChange={(e) => handlePlanChange(['views', vIndex, 'name'], e.target.value)} fullWidth sx={{ mb: 2 }} />
//                   <TextField label="Associated Controller" size="small" variant="outlined" value={view.controller} onChange={(e) => handlePlanChange(['views', vIndex, 'controller'], e.target.value)} fullWidth />
//                 </AccordionDetails>
//               </Accordion>
//             ))}
//             <Button startIcon={<AddIcon />} sx={{mt: 1}} onClick={() => handleAddItem(['views'], { name: 'NewView.cshtml', controller: 'NewController' })}>Add View</Button>
//           </Grid>

//           <Grid item xs={12}><Divider/></Grid>

//           {/* Services & Repositories */}
//           <Grid item xs={12} md={6}>
//              {sectionHeader("Services", <ServiceIcon />)}
//              {plan.services?.map((srv, sIndex) => (
//                <ComponentEditor key={sIndex} component={srv} cIndex={sIndex} path="services" nameLabel="Service" listLabel="Methods" listName="methods" handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} newItemValue="NewMethod" />
//              ))}
//              <Button startIcon={<AddIcon />} sx={{mt: 1}} onClick={() => handleAddItem(['services'], { name: 'NewService', methods: [] })}>Add Service</Button>
//            </Grid>
//           <Grid item xs={12} md={6}>
//             {sectionHeader("Repositories", <RepoIcon />)}
//             {plan.repositories?.map((repo, rIndex) => (
//                <ComponentEditor key={rIndex} component={repo} cIndex={rIndex} path="repositories" nameLabel="Repository" listLabel="Methods" listName="methods" handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} newItemValue="NewMethodAsync" />
//              ))}
//              <Button startIcon={<AddIcon />} sx={{mt: 1}} onClick={() => handleAddItem(['repositories'], { name: 'NewRepository', methods: [] })}>Add Repository</Button>
//           </Grid>
//         </Grid>

//         <Box mt={4} display="flex" justifyContent="center" gap={2}>
//            <Button variant="outlined" color="secondary" onClick={onBack} disabled={isGenerating} startIcon={<BackIcon/>}>
//              Back
//            </Button>
//            <Button 
//             variant="contained" 
//             onClick={handleGenerate} 
//             disabled={isGenerating} 
//             startIcon={isGenerating ? <Loader className="spinner-border spinner-border-sm"/> : <SaveIcon />}
//             sx={{ backgroundColor: '#0d9488', '&:hover': { backgroundColor: '#0f766e' }}}
//            >
//              {isGenerating ? 'Generating Project...' : 'Confirm Plan & Generate'}
//            </Button>
//         </Box>
//       </Paper>
//     </div>
//   );
// };

// export default RefinePlan;


















































import React, { useState } from 'react';
import {
  Box, Typography, Button, TextField, IconButton, Accordion,
  AccordionSummary, AccordionDetails, Grid, Paper, Tooltip, Divider, Stack,
  createTheme, ThemeProvider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  AddCircleOutline as AddIcon,
  DeleteOutline as DeleteIcon,
  Save as SaveIcon,
  ArrowBack as BackIcon,
  AccountTree as RepoIcon,
  Settings as ServiceIcon,
  DataObject as EntityIcon,
  ViewModule as ViewIcon,
  DeveloperBoard as ControllerIcon
} from '@mui/icons-material';
import { Loader } from 'lucide-react';

// --- STYLING & THEME ---

// 1. Define a custom theme for consistent colors
const theme = createTheme({
  palette: {
    primary: {
      main: '#0d9488', // Teal-700
      light: '#14b8a6', // Teal-600
      dark: '#0f766e', // Teal-800
    },
    secondary: {
      main: '#64748b', // Slate-500
    },
  },
  components: {
    MuiAccordion: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          '&:before': {
            display: 'none',
          },
          '&.Mui-expanded': {
            margin: '8px 0',
          },
        },
      },
    },
    MuiAccordionSummary: {
      styleOverrides: {
        root: {
          backgroundColor: '#f8fafc',
          borderBottom: '1px solid #e2e8f0',
        },
      },
    },
    MuiTextField: {
        defaultProps: {
            variant: 'outlined',
            size: 'small'
        }
    }
  },
});

// --- SUB-COMPONENTS (for better readability) ---

const EntityEditor = ({ entity, eIndex, handlePlanChange, handleAddItem, handleDeleteItem }) => (
  <Accordion defaultExpanded>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Typography sx={{ fontWeight: '500', flexShrink: 0 }}>{entity.name || "Unnamed Entity"}</Typography>
    </AccordionSummary>
    <AccordionDetails>
      <Stack spacing={2}>
        <TextField
          label="Entity Name"
          value={entity.name}
          onChange={(e) => handlePlanChange(['entities', eIndex, 'name'], e.target.value)}
        />
        <Divider><Typography variant="caption">Properties</Typography></Divider>
        {entity.properties?.map((prop, pIndex) => (
          <Stack direction="row" spacing={1} key={pIndex} alignItems="center">
            <TextField label="Property Name" value={prop.name} onChange={(e) => handlePlanChange(['entities', eIndex, 'properties', pIndex, 'name'], e.target.value)} fullWidth />
            <TextField label="Type" value={prop.type} onChange={(e) => handlePlanChange(['entities', eIndex, 'properties', pIndex, 'type'], e.target.value)} fullWidth />
            <Tooltip title="Delete Property">
              <IconButton onClick={() => handleDeleteItem(['entities', eIndex, 'properties'], pIndex)}><DeleteIcon color="error" /></IconButton>
            </Tooltip>
          </Stack>
        ))}
        <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" onClick={() => handleAddItem(['entities', eIndex, 'properties'], { name: 'NewProperty', type: 'string' })}>
          Add Property
        </Button>
      </Stack>
    </AccordionDetails>
  </Accordion>
);

const ComponentEditor = ({ component, cIndex, path, nameLabel, listLabel, listName, handlePlanChange, handleAddItem, handleDeleteItem, newItemValue }) => (
  <Accordion>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Typography sx={{ fontWeight: '500' }}>{component.name || `Unnamed ${nameLabel}`}</Typography>
    </AccordionSummary>
    <AccordionDetails>
      <Stack spacing={2}>
        <TextField
          label={`${nameLabel} Name`}
          value={component.name}
          onChange={(e) => handlePlanChange([path, cIndex, 'name'], e.target.value)}
        />
        <Divider><Typography variant="caption">{listLabel}</Typography></Divider>
        {component[listName]?.map((item, iIndex) => (
          <Stack direction="row" spacing={1} key={iIndex} alignItems="center">
            <TextField label="Name" value={item} onChange={(e) => handlePlanChange([path, cIndex, listName, iIndex], e.target.value)} fullWidth/>
            <Tooltip title={`Delete ${listLabel.slice(0, -1)}`}>
              <IconButton onClick={() => handleDeleteItem([path, cIndex, listName], iIndex)}><DeleteIcon color="error" /></IconButton>
            </Tooltip>
          </Stack>
        ))}
        <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" onClick={() => handleAddItem([path, cIndex, listName], newItemValue)}>
          Add {listLabel.slice(0, -1)}
        </Button>
      </Stack>
    </AccordionDetails>
  </Accordion>
);


const RefinePlan = ({ initialPlan, sessionId, namespace, onPlanConfirmed, onBack }) => {
  const [plan, setPlan] = useState(initialPlan);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  // State handlers remain unchanged
  const handlePlanChange = (path, value) => {
    setPlan(prevPlan => {
      const newPlan = JSON.parse(JSON.stringify(prevPlan));
      let current = newPlan;
      for (let i = 0; i < path.length - 1; i++) { current = current[path[i]]; }
      current[path[path.length - 1]] = value;
      return newPlan;
    });
  };

  const handleAddItem = (path, newItem) => {
    setPlan(prevPlan => {
      const newPlan = JSON.parse(JSON.stringify(prevPlan));
      let current = newPlan;
      for(const p of path) { current = current[p] || (current[p] = []); }
      if (Array.isArray(current)) { current.push(newItem); }
      return newPlan;
    });
  };

  const handleDeleteItem = (path, index) => {
    setPlan(prevPlan => {
      const newPlan = JSON.parse(JSON.stringify(prevPlan));
      let current = newPlan;
      for(const p of path) { current = current[p]; }
      if (Array.isArray(current)) { current.splice(index, 1); }
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
    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', color: 'primary.dark', mb: 2 }}>
      {icon}
      <span style={{ marginLeft: '12px' }}>{title}</span>
    </Typography>
  );

  return (
    <ThemeProvider theme={theme}>
      <div className="container py-5">
        <div className="text-center mb-4">
          <h1 className="display-5 fw-bold">Review & Refine Project Plan</h1>
          <p className="lead text-muted">Inspect the AI-generated plan. You can edit, add, or remove items before final code generation.</p>
        </div>

        <Paper elevation={3} sx={{ p: { xs: 2, md: 3 }, backgroundColor: '#f8fafc', borderRadius: '12px' }}>
          <Grid container spacing={4}>
            {/* Entities */}
            <Grid item xs={12}>
              {sectionHeader("Domain Entities", <EntityIcon />)}
              <Stack spacing={1}>
                {plan.entities?.map((entity, eIndex) => (
                  <EntityEditor key={eIndex} entity={entity} eIndex={eIndex} handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} />
                ))}
              </Stack>
              <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" sx={{mt: 1.5, ml: 1}} onClick={() => handleAddItem(['entities'], { name: 'NewEntity', properties: [{name: 'Id', type: 'int'}] })}>Add Entity</Button>
            </Grid>
            
            <Grid item xs={12}><Divider/></Grid>

            {/* Controllers & Views */}
            <Grid item xs={12} md={6}>
              {sectionHeader("Controllers", <ControllerIcon />)}
              <Stack spacing={1}>
                {plan.controllers?.map((ctrl, cIndex) => (
                  <ComponentEditor key={cIndex} component={ctrl} cIndex={cIndex} path="controllers" nameLabel="Controller" listLabel="Actions" listName="actions" handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} newItemValue="NewAction" />
                ))}
              </Stack>
              <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" sx={{mt: 1.5, ml: 1}} onClick={() => handleAddItem(['controllers'], { name: 'NewController', actions: ['Index'] })}>Add Controller</Button>
            </Grid>
            <Grid item xs={12} md={6}>
              {sectionHeader("Views", <ViewIcon />)}
              <Stack spacing={1}>
                {plan.views?.map((view, vIndex) => (
                  <Accordion key={vIndex}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography sx={{ fontWeight: '500' }}>{view.name || "Unnamed View"}</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Stack spacing={2}>
                        <TextField label="View Name (.cshtml)" value={view.name} onChange={(e) => handlePlanChange(['views', vIndex, 'name'], e.target.value)} />
                        <TextField label="Associated Controller" value={view.controller} onChange={(e) => handlePlanChange(['views', vIndex, 'controller'], e.target.value)} />
                      </Stack>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Stack>
              <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" sx={{mt: 1.5, ml: 1}} onClick={() => handleAddItem(['views'], { name: 'NewView.cshtml', controller: 'NewController' })}>Add View</Button>
            </Grid>

            <Grid item xs={12}><Divider/></Grid>

            {/* Services & Repositories */}
            <Grid item xs={12} md={6}>
               {sectionHeader("Services", <ServiceIcon />)}
               <Stack spacing={1}>
                {plan.services?.map((srv, sIndex) => (
                  <ComponentEditor key={sIndex} component={srv} cIndex={sIndex} path="services" nameLabel="Service" listLabel="Methods" listName="methods" handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} newItemValue="NewMethod" />
                ))}
              </Stack>
              <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" sx={{mt: 1.5, ml: 1}} onClick={() => handleAddItem(['services'], { name: 'NewService', methods: [] })}>Add Service</Button>
             </Grid>
            <Grid item xs={12} md={6}>
              {sectionHeader("Repositories", <RepoIcon />)}
              <Stack spacing={1}>
                {plan.repositories?.map((repo, rIndex) => (
                  <ComponentEditor key={rIndex} component={repo} cIndex={rIndex} path="repositories" nameLabel="Repository" listLabel="Methods" listName="methods" handlePlanChange={handlePlanChange} handleAddItem={handleAddItem} handleDeleteItem={handleDeleteItem} newItemValue="NewMethodAsync" />
                ))}
              </Stack>
              <Button startIcon={<AddIcon />} size="small" variant="text" color="primary" sx={{mt: 1.5, ml: 1}} onClick={() => handleAddItem(['repositories'], { name: 'NewRepository', methods: [] })}>Add Repository</Button>
            </Grid>
          </Grid>

          <Box mt={4} display="flex" justifyContent="center" gap={2}>
             <Button variant="outlined" color="secondary" onClick={onBack} disabled={isGenerating} startIcon={<BackIcon/>}>
               Back
             </Button>
             <Button 
              variant="contained" 
              color="primary"
              size="large"
              onClick={handleGenerate} 
              disabled={isGenerating} 
              startIcon={isGenerating ? <Loader className="spinner-border spinner-border-sm"/> : <SaveIcon />}
             >
               {isGenerating ? 'Generating Project...' : 'Confirm Plan & Generate'}
             </Button>
          </Box>
        </Paper>
      </div>
    </ThemeProvider>
  );
};

export default RefinePlan;