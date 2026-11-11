const { store, supabase } = require('../supabase');
const { evaluateProjectRisks } = require('../engine/deterministicRiskEngine');
const { evaluateScenario } = require('../engine/whatIfSchedulingEngine');
const { v4: uuidv4 } = require('uuid');

async function getProjectRisks(req, res) {
  if (supabase) {
    try {
      const { data: dbTasks, error } = await supabase.from('tasks').select('*').eq('project_id', req.params.id);
      if (!error && dbTasks) {
        dbTasks.forEach(dt => {
          const idx = store.tasks.findIndex(t => t.id === dt.id);
          const mapped = {
            id: dt.id,
            projectId: dt.project_id,
            title: dt.title,
            description: dt.description || '',
            priority: dt.priority,
            statusCategory: dt.status_category,
            progressPercent: dt.progress_percent,
            completedAt: dt.completed_at,
            dueDate: dt.due_date,
            assigneeId: dt.assignee_id,
            createdAt: dt.created_at
          };
          if (idx >= 0) store.tasks[idx] = { ...store.tasks[idx], ...mapped };
          else store.tasks.push(mapped);
        });
      }
    } catch (e) {}
  }
  const project = store.projects.find(p => p.id === req.params.id) || store.projects[0];
  const projectTasks = store.tasks.filter(t => t.projectId === req.params.id);
  const findings = evaluateProjectRisks(project, projectTasks, store.dependencies || []);
  res.json(findings);
}

function evaluateRisks(req, res) {
  const project = store.projects.find(p => p.id === req.params.id) || store.projects[0];
  const projectTasks = store.tasks.filter(t => t.projectId === req.params.id);
  const findings = evaluateProjectRisks(project, projectTasks, store.dependencies || []);
  res.json(findings);
}

function evaluateProjectScenario(req, res) {
  const project = store.projects.find(p => p.id === req.params.id) || store.projects[0];
  const projectTasks = store.tasks.filter(t => t.projectId === req.params.id);
  const comparison = evaluateScenario(project, projectTasks, store.dependencies || [], req.body);
  res.json(comparison);
}

function simulateScenario(req, res) {
  const { projectId, scenarioName, changes } = req.body;
  const project = store.projects.find(p => p.id === projectId) || store.projects[0];
  const projectTasks = store.tasks.filter(t => t.projectId === (project ? project.id : ''));
  const scenario = {
    id: uuidv4(),
    name: scenarioName || 'What-If Simulation',
    changes: changes || []
  };
  const result = evaluateScenario(project, projectTasks, store.dependencies || [], scenario);
  res.json(result);
}

module.exports = {
  getProjectRisks,
  evaluateRisks,
  evaluateProjectScenario,
  simulateScenario
};
