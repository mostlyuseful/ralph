from pathlib import Path
import subprocess
import typer
from enum import Enum
from jinja2 import Template
from inspect import cleandoc


app = typer.Typer()


class TargetAudience(str, Enum):
    POC = "POC"
    ENTERPRISE = "Enterprise"

@app.command("brainstorm")
def brainstorm_idea(
    idea: str = typer.Argument(..., help="A brief description of the project idea you want Prof Frink to brainstorm and generate a spec for."),
    tdd: bool = typer.Option(
        False,
        help="Whether to use test-driven development (TDD) principles when brainstorming the project idea. If enabled, Prof. Frink will include test instructions in the `spec.md` file for the generated project idea.",
    ),
    audience: TargetAudience = typer.Option(
        TargetAudience.POC,
        help="Influences depth of questioning as well as complexity and scope of the generated project spec. " \
        "Choose between 'POC' for a proof-of-concept level project that is simpler and faster to implement, or 'Enterprise' for production-grade, k8s, cloud native and buzzword-compliant project ideas that are more complex and time-consuming to implement.",
    ),
):
    """Brainstorms a new project idea and creates a `spec.md` file with the project specification."""
    prompt = get_brainstorming_prompt(idea=idea, tdd=tdd, audience=audience)
    subprocess.run(
        [
            "opencode",
            "--prompt",
            prompt
        ])
            

@app.command("prd")
def bootstrap_prd_md(
    spec_path: Path = typer.Option(
        "spec.md",
        help="Path to the project specification file."),
    tdd: bool = typer.Option(
        False,
        help="Whether to generate tasks with test instructions based on test-driven development (TDD) principles. If enabled, the generated tasks in `prd.md` will include instructions for testing each task."),
):
    """Bootstraps an initial `prd.md` file with hierarchical tasks based on the project specification in `spec.md`. This is the required input for Ralph. If `prd.md` already exists, this command will not overwrite it and will exit with an error to avoid losing any existing task breakdowns."""
    
    if not spec_path.exists():
        typer.echo("Error: spec.md not found. Please create a spec.md file with the project specification before bootstrapping prd.md.")
        raise typer.Exit(code=1)
    
    spec = spec_path.read_text(encoding="utf-8")

    prompt = get_bootstrap_prd_prompt(spec, tdd=tdd)
    subprocess.run(
        [
            "opencode",
            "--prompt",
            prompt
        ])

def get_brainstorming_prompt(idea: str, tdd: bool, audience: TargetAudience) -> str:
    raw_prompt = """
    **Overall Goal:**
    Ask me one question at a time so we can develop a thorough, step-by-step spec for this idea. Each question should build on my previous answers, and our end goal is to have a detailed specification I can hand off to a developer. Let's do this iteratively and dig into every relevant detail. Remember, only one question at a time.

    **Important Guidelines:**
    Be brave and push back on stupid decisions on the user's part. Don't be sycophantic: you don't need to congratulate the user on their choices, just be matter-of-fact and concentrate on the questions. Assume the user has a high mental load and keep answers as succinct as possible without omitting important details.
    
    {% if audience == "POC" %}
    Be in-depth but avoid over-engineering. not every edge case has to be mitigated in the first iteration. The spec will be iterated on and improved over time, so it's better to start with a simpler version of the project that can be implemented quickly and then build on it in future iterations. Focus on the core functionality and the most important features that will make the project viable, and avoid getting bogged down in details that can be addressed later.
    {% elif audience == "Enterprise" %}
    Be very thorough and consider edge cases, scalability, security, and maintainability from the start. Also be sure to ask questions that clarify the non-functional requirements and constraints, such as expected traffic, data sensitivity, compliance requirements, and team expertise. It is important to understand the broader context, in which environment the project will be deployed (e.g. Cloud Native, k8s, GCP vs AWS vs Azure), and the long-term vision for the project to ensure the spec is comprehensive and future-proof.
    {% endif %}

    {% if tdd %}
    Since you will be generating a `spec.md` file that will be the foundation and single source-of-truth for the project, it is critical to include detailed instructions for testing in the spec. Please include a dedicated section in the `spec.md` file that outlines the testing strategy, including what types of tests should be implemented (e.g. unit tests, maybe property-based testing, integration tests, end-to-end tests), what testing frameworks or tools to use, and any specific testing requirements or considerations based on the project's functionality and tech stack.
    {% endif %}

    For quicker responses, generate three succinct possible answers (the first always being the recommended one). If the user just types 3 in response for example, continue as if the answer corresponding with option 3 had been typed in by the user.

    **Last Step:**
    AFTER the brainstorming has concluded, either because the user decided to stop or because you have asked all the necessary questions to have a thorough spec, create a `spec.md` file with the project specification based on the answers given by the user. The `spec.md` file should be well-structured and organized, with clear sections and headings for different aspects of the project such as functional requirements, non-functional requirements, technical specifications, and testing instructions (if TDD is enabled). The spec should be detailed enough for a developer to implement the project without needing to ask further questions.

    SUPER SUPER IMPORTANT: DO NOT START IMPLEMENTATION! Your only task is to ask questions and create a thorough spec based on the answers. The implementation will be done by Ralph in later iterations based on the spec you create, so it's critical that you focus on asking the right questions and creating a comprehensive spec that will guide the implementation.

    **User input:**
    Here's the idea:

    {{ idea }}
    """
    template = Template(cleandoc(raw_prompt))
    return template.render(idea=idea, tdd=tdd, audience=audience)

def get_bootstrap_prd_prompt(spec: str, tdd: bool) -> str:
    raw_prompt = """
    **Overall Goal:**
    Create an initial `prd.md` file with a hierarchical breakdown of tasks based on the project specification in `spec.md`. This will be the todo list for the developer to work on the project.

    **prd.md Structure:**
    `prd.md` should be structured with clear headings for each iteration, major task, and sub-tasks should be listed as checkboxes under their respective headings. For example:

    ```markdown
    # Project Name (e.g. "Awesome Web App")
    Short description of the project that gives an overview of its purpose and functionality.

    ## Iteration Name (e.g. "Iteration: User Authentication")
    Short description of the focus of iteration. The iteration is the largest unit of work and should be focused on a specific theme or area of the project. Each iteration should have a clear goal and outcome.
    
    ### Major Task Name (e.g. "Implement OAuth User Authentication")
    Detailed description of the major task. All required context to complete the task should be included in this description. If the task is too big, break it down into smaller sub-tasks. The major task is a significant piece of work that contributes to the overall goal of the iteration.
    AC: (Acceptance Criteria)
    - [ ] Description of the first acceptance criterion. Include all necessary context and details to meet this criterion.
    - [ ] Description of the second acceptance criterion. (E.g. "Users are able to log in using their Google account").
    ...

    #### Sub-task (e.g. "Research OAuth libraries")
    Detailed description of the sub-task, similar to major tasks but smaller in scope. The sub task is the smallest unit of work and should be focused on a specific aspect of the major task.
    AC:
    - [ ] Description of the acceptance criterion for the sub-task.
    ```

    **Important Guidelines:**
    Draft a detailed, step-by-step blueprint for building this project. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. Review the results and make sure that the steps are small enough to be implemented safely, but big enough to move the project forward. Iterate until you feel that the steps are right sized for this project.

    From here you should have the foundation to provide a series of iterations, major tasks and subtasks for the developer that will implement each step. Prioritize best practices, and incremental progress, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step.

    {% if tdd %}
    Ffollow test-driven development (TDD) principles. It is critical to include detailed instructions for testing in the `prd.md` file. For each major task and sub-task, include information that outlines the testing strategy for that task.
    {% endif %}

    SUPER SUPER IMPORTANT: DO NOT START IMPLEMENTATION! Your only task is to generate a well-structured `prd.md` file with a clear breakdown of tasks based on the project specification. The implementation will be done by Ralph in later iterations based on the `prd.md` you create, so it's critical that you focus on creating a comprehensive and well-organized task breakdown that will guide the implementation.
    
    **User input:**
    Here's the project specification:

    {{ spec }}
    """
    template = Template(cleandoc(raw_prompt))
    return template.render(spec=spec, tdd=tdd)