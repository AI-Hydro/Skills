---
name: course-authoring
description: >
  End-to-end workflow for authoring a multi-module AI-Hydro course: interview
  the user for audience and goals, propose a module breakdown with an
  explicit prerequisite graph, scaffold the files via the course_scaffold
  tool, then author each module's body. Use when the user asks to "build
  a course", "create a curriculum", "design a learning module", or wants
  to teach a hydrology topic to students.
when_to_use: >
  build a course | create a course | design a curriculum | author modules |
  teaching materials | course outline | new course | learning path |
  module skeleton | course scaffolding | curriculum design
domain: teaching
tools_used: [course_scaffold, course_get_curriculum, course_get_state, course_navigate]
disable-model-invocation: false
allowed-tools: Read Write Edit Bash
---

## Purpose

Help the researcher author a high-quality AI-Hydro course — a folder
containing ``course.json`` and one or more module HTML files that render
inside the HTML Preview panel. A good course has a clear audience, an
ordered sequence of 3–8 modules, an explicit prerequisite graph (what must
be learned before what), and modules that each teach **one** concept with a
hands-on element.

This skill is the *workflow*; the file-creation work is done by the
``course_scaffold`` MCP tool. Do not write ``course.json`` by hand — that
is what the tool is for.

## When to use

- User says they want to teach, train, or onboard others.
- User asks for a "course", "curriculum", "learning module", or "lesson".
- User wants to repackage existing analysis work as teaching material.
- A research lab wants a shared onboarding sequence for new students.

## When NOT to use

- Single one-off interactive figure or notebook → just author one HTML
  module directly, no course wrapper needed.
- The user wants to *take* a course (be a student) → use the
  ``course_get_state`` / ``course_navigate`` tools instead.
- A documentation site or static reference → use a docs framework, not the
  course system.

## Workflow

### 1. Check if a course is already active

Call ``course_get_state``. If it returns ``active: true``, ask:

> "I see you already have the **\<title\>** course open. Should this new
> course extend it, replace a module in it, or stand alone?"

Don't assume.

### 2. Interview the user

Ask, in order — wait for answers, don't batch:

1. **Topic and angle.** What's the course about? Not just "hydrology" —
   "intro hydrograph analysis for first-year MSc students" is the right
   resolution.
2. **Audience and prerequisite knowledge.** Who is the student? What can
   you assume they already know? Python? Calculus? Field hydrology?
3. **Time budget.** Total hours the student should spend, end-to-end.
4. **Hands-on vs. read-only.** Will modules include executable Python
   cells, interactive maps, or just prose + figures?
5. **Where to write it.** Absolute path to an empty folder.

### 3. Propose a module outline — get explicit approval

Draft 3–8 modules. **Always present this as a table with the prerequisite
graph visible**:

| # | Module title | Prereqs | Est. min | One-sentence learning goal |
|---|---|---|---|---|
| 1 | Reading a hydrograph | — | 25 | Identify baseflow, peak, recession on a real time series |
| 2 | Pulling streamflow | 1 | 30 | Fetch USGS data and compute basic statistics |
| 3 | Baseflow separation | 2 | 40 | Run a digital filter and interpret the BFI |

Rules:
- **No prerequisite cycles.** ``course_scaffold`` will reject these — fix
  before calling.
- **Each module teaches one thing.** "Streamflow + baseflow + flood
  frequency" is three modules, not one.
- **Order is the *curriculum* order, not the file order.** The student
  walks through in the order given.
- **Prereqs are sparse and meaningful.** "Module 5 needs module 3" only
  if module 5 *uses* something module 3 taught. Don't chain every module
  serially "just in case" — that defeats free-roam access.

Show the outline and **ask: "Approve this structure, or would you like to
add/remove/reorder?"** Don't proceed until the user says yes.

### 4. Call ``course_scaffold``

Pass the approved outline:

```python
course_scaffold(
    title="Intro to Hydrograph Analysis",
    out_dir="/abs/path/to/courses/intro-hydrograph",
    modules=[
        {"title": "Reading a hydrograph",  "estimated_minutes": 25,
         "abstract": "Anatomy of a hydrograph: baseflow, peak, recession.",
         "executable": False},
        {"title": "Pulling streamflow",    "estimated_minutes": 30,
         "abstract": "Fetch USGS data and compute basic statistics.",
         "prerequisites": ["reading-a-hydrograph"], "executable": True},
        # ...
    ],
    author_name="<user's name>",
    author_affiliation="<user's affiliation>",
)
```

The tool auto-slugifies module ids from titles ("Reading a hydrograph" →
``reading-a-hydrograph``). Use those slugs when wiring ``prerequisites``.
The tool returns the absolute paths of every file it created — keep them.

If the tool returns an error:

- ``conflicts`` → the target folder isn't empty. Ask whether to choose a
  new folder or pass ``overwrite=True``.
- ``cycle`` → fix the prereq graph (the cycle is reported as an ordered
  list of ids).
- ``duplicate_id`` → two modules slugified to the same id. Rename one.

### 5. Author each module's body

For each ``module.html`` returned by ``course_scaffold``:

1. ``Read`` the file — note the placeholder sections (``<section class="card"
   data-aihydro-editable="prose">`` with ``<p class="placeholder">TODO
   ...</p>``).
2. Replace each placeholder with real content. Keep the
   ``data-aihydro-editable="prose"`` markers — they're what enables the
   visual edit-mode in the preview panel.
3. For executable modules, embed a Python cell using the AI-Hydro cell
   format (see any module in ``examples/courses/intro-to-hydrology/`` for
   reference). Each cell is a ``<pre><code class="language-python">`` block
   wrapped in ``<section class="aihydro-cell">``.
4. For interactive maps, use the leaflet-adapter pattern (see
   ``02-exploring-conus-hydrology/module.html``).
5. Cite real sources — embed via the ``aihydro-bridge-citation`` system,
   not free-text "(Lyne & Hollick 1979)" strings.

**Author modules in curriculum order.** This lets you reference earlier
modules naturally ("As we saw in *Reading a hydrograph*, ...").

### 6. Test in the preview

Tell the user:

> "Open ``<course_root>/<first-folder>/module.html`` in the HTML Preview
> panel. The course header should show **3/3 modules** with the cyan
> stripe on module 1. Click **Next ▶** to walk through — each module
> should render and lock/unlock its successor."

Watch for:

- **No header strip?** ``course.json`` didn't parse or wasn't found by
  the walk-up. Run ``course_get_curriculum(path_to_course_json)`` to
  validate.
- **Modules render unstyled** → the ``<style>`` block was edited out.
  Restore from the scaffold template.
- **Edit mode broken** → ``data-aihydro-editable="prose"`` markers were
  removed during authoring.

### 7. Iterate

After the user walks through:

- Ask which modules were too long / too short → adjust ``estimatedMinutes``
  in ``course.json``.
- Ask which prereqs felt wrong (locked something obvious, or didn't lock
  something that should have) → adjust the ``prerequisites`` arrays.
- Use ``course_set_progress(action='uncomplete', module_id=...)`` to reset
  any modules you completed during testing.

## Anti-patterns

- **Writing course.json by hand.** Use ``course_scaffold`` — it validates,
  formats consistently, and slugifies ids.
- **Skipping the interview.** A scaffold built from your guess at the
  user's goal usually gets thrown out. Cheap to ask, expensive to redo.
- **One mega-module.** If a module is >60 estimated minutes, split it.
- **Prereq spaghetti.** Linear chains (1 → 2 → 3 → 4 → 5) defeat
  free-roam. Use prereqs only where genuinely required.
- **Hand-coding the ``<style>`` block** in modules. The scaffold gives you
  a tested, on-brand style — only modify the content sections.

## Related skills

- ``baseflow-separation`` — useful as content inside a hydrology course
  module.
- ``frequency-analysis`` — same.

## Related tools

- ``course_scaffold`` — file writer for the workflow above.
- ``course_get_curriculum`` — validate a scaffolded course.
- ``course_get_state`` / ``course_navigate`` — test the course as a
  student would.
