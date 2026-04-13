import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings

from agents_app.agents import planner_agent
from agents_app.api.models import PendingAction, Session
from agents_app.services.session_memory import SessionMemory
from agents_app.services.step_execution_service import StepExecutionService
from agents_app.state.project_state_repository import ProjectStateRepository
from agents_app.utils import extract_text_from_run, safe_json_parse


class ProjectWorkflowService:
    def __init__(self, session: Session):
        self.session = session
        self.workspace = Path(settings.WORKSPACE_PATH) / "sessions" / f"session_{session.id}"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.md_path = self.workspace / "project_plan.md"
        self.state_repo = ProjectStateRepository(self.workspace / "project_state_workflow.json")

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower()).strip("-")
        return slug or "project"

    def _get_workflow(self) -> Dict[str, Any]:
        context = self.session.context or {}
        return context.get("workflow") or {}

    def _save_workflow(self, workflow: Dict[str, Any]) -> None:
        context = self.session.context or {}
        context["workflow"] = workflow
        self.session.context = context
        self.session.save(update_fields=["context"])

    def _render_markdown(self, workflow: Dict[str, Any]) -> str:
        lines = [
            f"# Projeto: {workflow.get('project_name', self.session.title)}",
            "",
            "## Objetivo",
            workflow.get("idea_text", ""),
            "",
            "## Estado do Workflow",
            f"- state: `{workflow.get('state', 'drafting_md')}`",
            f"- ready_to_implement: `{workflow.get('ready_to_implement', False)}`",
            "",
            "## Fases",
            "1. Bootstrap estrutural (base PAIA)",
            "2. Features de negócio",
            "",
            "## Features e Steps",
        ]

        for feature in workflow.get("features", []):
            lines.extend([
                "",
                f"### [{feature['feature_id']}] {feature['title']}",
                f"- phase: `{feature.get('phase', 1)}`",
                f"- branch: `{feature.get('branch')}`",
                f"- description: {feature.get('description', '')}",
                "",
            ])
            for step in feature.get("steps", []):
                lines.extend([
                    f"- [{step.get('status', 'pending')}] ({step['step_id']}) {step['title']}",
                    f"  - outputs: {', '.join(step.get('outputs', [])) or '(none)'}",
                    f"  - completion_criteria: {step.get('completion_criteria', '')}",
                ])

        lines.extend([
            "",
            "## Gate",
            "Quando este MD estiver validado, confirmar implementação com o usuário.",
        ])

        md = "\n".join(lines).strip() + "\n"
        self.md_path.write_text(md, encoding="utf-8")
        return md

    def _default_bootstrap_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Criar estrutura base de diretórios",
                "description": "Garantir pastas backend/frontend/shared e arquivo README inicial.",
                "outputs": ["backend/README.md", "frontend/README.md", "shared/README.md"],
                "completion_criteria": "Estrutura base criada e documentada.",
            },
            {
                "title": "Configurar baseline de execução",
                "description": "Definir arquivos mínimos de execução para backend e frontend conforme stack.",
                "outputs": ["backend/requirements.txt", "frontend/package.json", "docker-compose.yml"],
                "completion_criteria": "Projeto possui baseline de execução local.",
            },
        ]

    def _extract_plan(self, project_name: str, idea_text: str) -> Dict[str, Any]:
        memory = SessionMemory(session_id=self.session.id, workspace_path=self.workspace)
        rag_context = memory.get_rag_context(
            "PAIA arquitetura base, bootstrap estrutural, ordem de implementação por fases",
            top_k=6,
        )

        prompt = f"""
You are planning a markdown-first implementation workflow.

Project name: {project_name}
User idea:
{idea_text}

PAIA context:
{rag_context}

Return STRICT JSON with this shape:
{{
  "stack": {{"backend": "django|fastapi", "frontend": "angular|html_css_js", "database": "postgres"}},
  "bootstrap_steps": [
    {{"title": "...", "description": "...", "outputs": ["..."], "completion_criteria": "..."}}
  ],
  "features": [
    {{
      "title": "...",
      "description": "...",
      "phase": 1,
      "steps": [
        {{"title": "...", "description": "...", "outputs": ["..."], "completion_criteria": "..."}}
      ]
    }}
  ]
}}

Rules:
- Bootstrap MUST come before any feature.
- Steps must be atomic and user-approvable.
- Keep output lists concrete.
"""
        raw = extract_text_from_run(planner_agent.run(prompt))
        return safe_json_parse(raw)

    def _normalize_features(self, project_name: str, plan: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        stack = plan.get("stack") or {
            "backend": "django",
            "frontend": "angular",
            "database": "postgres",
        }

        normalized_features: List[Dict[str, Any]] = []
        global_step = 1
        project_slug = self._slugify(project_name)

        bootstrap_steps = plan.get("bootstrap_steps") or self._default_bootstrap_steps()
        bootstrap_feature = {
            "feature_id": "F00",
            "title": "Bootstrap Estrutural",
            "description": "Preparar base do projeto antes das features de negócio.",
            "phase": 0,
            "branch": f"feat/{project_slug}/bootstrap",
            "steps": [],
        }

        for idx, step in enumerate(bootstrap_steps, 1):
            bootstrap_feature["steps"].append({
                "step": global_step,
                "step_id": f"F00-S{idx:02d}",
                "title": step.get("title") or f"Bootstrap step {idx}",
                "description": step.get("description", ""),
                "outputs": step.get("outputs") or [],
                "completion_criteria": step.get("completion_criteria", ""),
                "status": "pending",
                "generated_files": [],
            })
            global_step += 1
        normalized_features.append(bootstrap_feature)

        input_features = plan.get("features") or [{
            "title": "Feature Principal",
            "description": "Feature inicial derivada da ideia do usuário.",
            "phase": 1,
            "steps": [{
                "title": "Implementar feature principal",
                "description": "Construir primeira entrega funcional.",
                "outputs": ["backend/main.py", "frontend/index.html"],
                "completion_criteria": "Feature principal funcional no baseline.",
            }],
        }]

        for feature_index, feature in enumerate(input_features, 1):
            feature_id = f"F{feature_index:02d}"
            feature_slug = self._slugify(feature.get("title") or feature_id)
            normalized = {
                "feature_id": feature_id,
                "title": feature.get("title") or f"Feature {feature_index}",
                "description": feature.get("description", ""),
                "phase": int(feature.get("phase", 1)),
                "branch": f"feat/{project_slug}/{feature_slug}",
                "steps": [],
            }

            steps = feature.get("steps") or []
            for step_index, step in enumerate(steps, 1):
                normalized["steps"].append({
                    "step": global_step,
                    "step_id": f"{feature_id}-S{step_index:02d}",
                    "title": step.get("title") or f"Step {step_index}",
                    "description": step.get("description", ""),
                    "outputs": step.get("outputs") or [],
                    "completion_criteria": step.get("completion_criteria", ""),
                    "status": "pending",
                    "generated_files": [],
                })
                global_step += 1
            normalized_features.append(normalized)

        normalized_features.sort(key=lambda f: (f.get("phase", 1), f.get("feature_id", "")))
        return normalized_features, stack

    def start_workflow(self, project_name: str, idea_text: str) -> Dict[str, Any]:
        project_name = (project_name or "").strip() or self.session.title
        idea_text = (idea_text or "").strip()
        if not idea_text:
            raise ValueError("idea_text is required")

        plan = self._extract_plan(project_name, idea_text)
        features, stack = self._normalize_features(project_name, plan)

        workflow = {
            "mode": "md_first",
            "state": "drafting_md",
            "project_name": project_name,
            "idea_history": [idea_text],
            "idea_text": idea_text,
            "stack": stack,
            "features": features,
            "ready_to_implement": False,
            "pending_action_id": None,
            "commit_policy": "manual_user",
            "approval_granularity": "step",
            "branching": "per_feature",
        }
        markdown = self._render_markdown(workflow)
        self._save_workflow(workflow)
        return {
            "status": "md_draft_created",
            "state": workflow["state"],
            "project_name": project_name,
            "project_plan_path": str(self.md_path),
            "markdown": markdown,
        }

    def update_workflow_markdown(self, user_input: str) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")
        if workflow.get("state") in {"implementing", "completed"}:
            raise ValueError("cannot update markdown after implementation started")

        user_input = (user_input or "").strip()
        if user_input:
            workflow.setdefault("idea_history", []).append(user_input)
            workflow["idea_text"] = "\n".join(workflow["idea_history"])

        plan = self._extract_plan(workflow.get("project_name", self.session.title), workflow["idea_text"])
        features, stack = self._normalize_features(workflow.get("project_name", self.session.title), plan)
        workflow["features"] = features
        workflow["stack"] = stack
        workflow["state"] = "drafting_md"
        workflow["ready_to_implement"] = False

        markdown = self._render_markdown(workflow)
        self._save_workflow(workflow)
        return {
            "status": "md_updated",
            "state": workflow["state"],
            "project_plan_path": str(self.md_path),
            "markdown": markdown,
        }

    def finalize_markdown(self) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")
        if workflow.get("state") in {"implementing", "completed"}:
            raise ValueError("workflow already in execution lifecycle")

        workflow["state"] = "waiting_implementation_confirmation"
        workflow["ready_to_implement"] = True
        markdown = self._render_markdown(workflow)
        self._save_workflow(workflow)
        return {
            "status": "md_ready",
            "state": workflow["state"],
            "question": "Documento concluído. Deseja implementar agora?",
            "project_plan_path": str(self.md_path),
            "markdown": markdown,
        }

    def confirm_implementation(self, confirm: bool) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")
        if workflow.get("state") != "waiting_implementation_confirmation":
            raise ValueError("workflow is not waiting implementation confirmation")

        if confirm:
            workflow["state"] = "implementing"
            self._save_workflow(workflow)
            return {
                "status": "implementation_started",
                "state": workflow["state"],
                "message": "Implementação iniciada. Solicite o próximo step para aprovação.",
            }

        return {
            "status": "implementation_not_confirmed",
            "state": workflow["state"],
            "message": "Implementação não iniciada. Continue refinando o markdown.",
        }

    def _find_feature_and_step(self, workflow: Dict[str, Any], feature_id: str, step_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        for feature in workflow.get("features", []):
            if feature.get("feature_id") != feature_id:
                continue
            for step in feature.get("steps", []):
                if step.get("step_id") == step_id:
                    return feature, step
        raise ValueError("feature/step not found")

    def _find_next_step(self, workflow: Dict[str, Any]) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        for feature in workflow.get("features", []):
            for step in feature.get("steps", []):
                if step.get("status") == "pending":
                    return feature, step
        return None

    @staticmethod
    def _all_completed(workflow: Dict[str, Any]) -> bool:
        for feature in workflow.get("features", []):
            for step in feature.get("steps", []):
                if step.get("status") != "completed":
                    return False
        return True

    def propose_next_step(self) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")
        if workflow.get("state") != "implementing":
            raise ValueError("workflow is not implementing")

        pending = workflow.get("pending_action_id")
        if pending:
            return {
                "status": "awaiting_approval",
                "pending_action_id": pending,
                "message": "Já existe um step pendente de aprovação.",
            }

        for feature in workflow.get("features", []):
            for step in feature.get("steps", []):
                if step.get("status") == "awaiting_commit":
                    return {
                        "status": "awaiting_commit_confirmation",
                        "feature_id": feature["feature_id"],
                        "step_id": step["step_id"],
                        "message": "Há um step aguardando confirmação de commit manual.",
                        "git": step.get("git", {}),
                    }

        nxt = self._find_next_step(workflow)
        if not nxt:
            workflow["state"] = "completed"
            self._save_workflow(workflow)
            return {
                "status": "completed",
                "state": "completed",
                "message": "Todas as features/steps foram concluídos.",
            }

        feature, step = nxt
        pending_action = PendingAction.objects.create(
            session=self.session,
            tool_name="execute_step",
            tool_input={
                "feature_id": feature["feature_id"],
                "step_id": step["step_id"],
            },
            description=f"Executar step {step['step_id']} ({step['title']}) da feature {feature['title']}",
        )

        step["status"] = "awaiting_approval"
        workflow["pending_action_id"] = pending_action.id
        self._save_workflow(workflow)
        self._render_markdown(workflow)
        return {
            "status": "confirmation_required",
            "pending_action_id": pending_action.id,
            "feature_id": feature["feature_id"],
            "step_id": step["step_id"],
            "branch": feature.get("branch"),
            "step": {
                "title": step["title"],
                "description": step.get("description", ""),
                "outputs": step.get("outputs", []),
                "completion_criteria": step.get("completion_criteria", ""),
            },
        }

    def _build_git_suggestions(self, feature: Dict[str, Any], step: Dict[str, Any], files: List[str]) -> Dict[str, Any]:
        branch = feature.get("branch")
        add_targets = " ".join(files) if files else "."
        message = f"feat({feature.get('feature_id')}): {step.get('title')}"
        return {
            "branch": branch,
            "commands": [
                f"git checkout -b {branch}",
                f"git add {add_targets}",
                f'git commit -m "{message}"',
            ],
            "note": "Commit é manual; execute os comandos após revisar o diff.",
        }

    def execute_approved_step(self, pending_action: PendingAction) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")
        if workflow.get("state") != "implementing":
            raise ValueError("workflow is not implementing")
        if pending_action.tool_name != "execute_step":
            raise ValueError("pending action is not workflow step execution")

        feature_id = pending_action.tool_input.get("feature_id")
        step_id = pending_action.tool_input.get("step_id")
        feature, step = self._find_feature_and_step(workflow, feature_id, step_id)
        if step.get("status") != "awaiting_approval":
            raise ValueError("step is not awaiting approval")

        service = StepExecutionService(workspace=self.workspace, state_repo=self.state_repo)
        project_meta = {
            "project_name": workflow.get("project_name"),
            "stack": workflow.get("stack", {}),
            "feature": {
                "id": feature["feature_id"],
                "title": feature.get("title"),
            },
        }

        execution_step = {
            "step": step["step"],
            "title": step.get("title"),
            "description": step.get("description"),
            "outputs": step.get("outputs", []),
            "completion_criteria": step.get("completion_criteria", ""),
        }

        result = service.execute_next_step(project_meta=project_meta, execution_plan=[execution_step])
        workflow["pending_action_id"] = None

        if result.get("status") == "step_completed":
            files = result.get("generated_files", [])
            step["status"] = "awaiting_commit"
            step["generated_files"] = files
            step["git"] = self._build_git_suggestions(feature, step, files)
            status_value = "step_executed_waiting_commit"
        else:
            step["status"] = "failed"
            step["failure"] = result
            status_value = "step_failed"

        self._save_workflow(workflow)
        self._render_markdown(workflow)
        return {
            "status": status_value,
            "feature_id": feature_id,
            "step_id": step_id,
            "execution": result,
            "git": step.get("git"),
            "project_plan_path": str(self.md_path),
        }

    def reject_pending_step(self, pending_action: PendingAction) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")

        feature_id = pending_action.tool_input.get("feature_id")
        step_id = pending_action.tool_input.get("step_id")
        feature, step = self._find_feature_and_step(workflow, feature_id, step_id)
        step["status"] = "pending"
        workflow["pending_action_id"] = None
        self._save_workflow(workflow)
        self._render_markdown(workflow)
        return {
            "status": "step_rejected",
            "feature_id": feature["feature_id"],
            "step_id": step["step_id"],
        }

    def confirm_step_commit(self, feature_id: str, step_id: str, commit_ref: str = "") -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            raise ValueError("workflow not started")
        feature, step = self._find_feature_and_step(workflow, feature_id, step_id)
        if step.get("status") != "awaiting_commit":
            raise ValueError("step is not awaiting commit confirmation")

        step["status"] = "completed"
        step["commit_confirmed"] = True
        if commit_ref:
            step["commit_ref"] = commit_ref

        if self._all_completed(workflow):
            workflow["state"] = "completed"

        self._save_workflow(workflow)
        self._render_markdown(workflow)
        return {
            "status": "commit_confirmed",
            "feature_id": feature_id,
            "step_id": step_id,
            "workflow_state": workflow.get("state"),
        }

    def get_status(self) -> Dict[str, Any]:
        workflow = self._get_workflow()
        if not workflow:
            return {"status": "not_started"}

        total = 0
        completed = 0
        awaiting_approval = 0
        awaiting_commit = 0
        failed = 0

        for feature in workflow.get("features", []):
            for step in feature.get("steps", []):
                total += 1
                st = step.get("status")
                if st == "completed":
                    completed += 1
                elif st == "awaiting_approval":
                    awaiting_approval += 1
                elif st == "awaiting_commit":
                    awaiting_commit += 1
                elif st == "failed":
                    failed += 1

        return {
            "status": "ok",
            "workflow_state": workflow.get("state"),
            "project_name": workflow.get("project_name"),
            "project_plan_path": str(self.md_path),
            "pending_action_id": workflow.get("pending_action_id"),
            "counters": {
                "total_steps": total,
                "completed_steps": completed,
                "awaiting_approval": awaiting_approval,
                "awaiting_commit": awaiting_commit,
                "failed_steps": failed,
            },
        }

    def get_markdown(self) -> str:
        if self.md_path.exists():
            return self.md_path.read_text(encoding="utf-8")
        workflow = self._get_workflow()
        return self._render_markdown(workflow) if workflow else ""
