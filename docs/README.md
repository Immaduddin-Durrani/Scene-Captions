# Documentation index

Start with the [project README](../README.md), [architecture](../architecture.txt) and [skill workflow](SKILL_WORKFLOW.md). Then read [current state](PROJECT_STATE.md) for the latest findings, decisions, snapshot coverage and unfinished work. This index is the directory guide; current state is the handoff summary.

## Find a subject

| Subject | Authoritative location |
| --- | --- |
| Product purpose, constraints, operating rules, crucial decision history | [architecture.txt](../architecture.txt) |
| Getting the prototype running | [project README](../README.md) and [Phase 1 handoff](PHASE1.md) |
| Current implementation, open decisions and next work | [PROJECT_STATE.md](PROJECT_STATE.md) |
| Skill selection, permission boundaries and evidence expectations | [SKILL_WORKFLOW.md](SKILL_WORKFLOW.md) |
| Canonical domain meanings | [GLOSSARY.md](../GLOSSARY.md) |
| Proposed study protocol | [EXPERIMENTAL_PLAN.md](EXPERIMENTAL_PLAN.md) |
| Plan source for app/export | `src/lib/experiment.ts`; regenerate plan copies with the existing exporter after approved edits |
| Import format and local media preparation | [CAPTION_IMPORT.md](CAPTION_IMPORT.md) |
| Local short-film preparation, audio, posters and subtitles | [LOCAL_MEDIA.md](LOCAL_MEDIA.md) |
| Per-title dialogue / sound coverage | [LIBRARY_CAPTIONS.md](LIBRARY_CAPTIONS.md) |
| Caption provenance, generation failures and limits | [CAPTION_GENERATION_STATUS.md](CAPTION_GENERATION_STATUS.md) |
| Dated findings and priorities | [original audit](audits/2026-10-24.md), [fixes and diagnosis](audits/2026-10-24-fixes.md), [model investigation and cleanup](audits/2026-10-24-investigation.md) |
| Model/service capability notes | [NVIDIA candidates](integrations/NVIDIA_MODELS.md) |
| Offline generation and corresponding-audio checks | [tooling guide](../scripts/generation/README.md); failed candidates never overwrite playback |
| Research references, verification limits and PDFs | [RESEARCH_INDEX.md](RESEARCH_INDEX.md), `research/` |
| Original project pitch | [proposal slides](research/proposals/SceneCaptions_Project_Proposal.pptx) and [idea document](research/proposals/SceneCaptions-Project-Idea.docx) |
| Refreshed committed structural map | [CODEBASE_MAP.md](CODEBASE_MAP.md); verify input hashes before relying on it |
| Verification history | [verification overview](verification/README.md) and [latest investigation evidence](verification/investigation-2026-10-24/README.md) |
| Manual browser-check utilities | [verification scripts guide](../scripts/verification/README.md) |

## Repository layout and ownership

```text
README.md                  Project entry point and startup
architecture.txt           Constraints, operating rules, decision history
GLOSSARY.md                Domain language
src/
  app/                     Next.js routes, page composition and global styles
  components/              Player, settings and other interface components
  lib/                     Caption rules, schemas and study/domain helpers
tests/                     Reusable automated behavior tests
scripts/
  verification/            Manually invoked browser-check utilities
  ...                      Offline ingestion, generation and maintenance tools
data/
  captions/                Precomputed caption datasets
  authoring/               Reviewed wording/source preparation
  sources/                 Preserved licensed source material and provenance
public/                    Browser-served assets and deliberate downloads only
docs/
  README.md                This navigation and file-ownership guide
  PROJECT_STATE.md         Current handoff
  SKILL_WORKFLOW.md        Required skill-selection workflow
  audits/                  Dated human-readable findings
  integrations/            External model/service reference notes
  research/
    proposals/             Original project pitch documents
    ...                    Research papers and provenance
  verification/
    audit-YYYY-MM-DD/
      README.md            Run scope and evidence navigation
      reports/             Raw machine results and command output
      screenshots/         Rendered evidence
      exports/             Synthetic test-session samples, never participant data
  ...                      Established setup, experiment and import guides
artifacts/                 Ignored temporary derived files
graphify-out/              Ignored local map; may be absent in another checkout
```

Existing root documentation guides under `docs/` keep their stable paths. Do not rename unrelated files merely to impose a new naming scheme. New audit reports use date-based names; established canonical documents retain their uppercase convention. Add a folder or module when it gives related material a clear purpose, not merely to add nesting.

## Maintenance rules

- Keep one authoritative home for each subject. Link to detailed findings instead of copying the full audit into every entry document.
- Keep offline model code outside web runtime imports. Keep pure caption/domain rules separate from UI orchestration and infrastructure.
- Keep executable verification code in scripts/tests, not among documentary outputs. Dated scripts may preserve a specific audit reproduction; promote them to maintained tests only when useful.
- Store only intentionally public files under `public/`. Keys, participant data, private model responses and local caches never belong there or in Git.
- Temporary research extraction/cache files belong under ignored artifacts. Original licensed papers and proposal documents remain in the research collection.
- After moves, update links, script output paths and handoff pointers. Preserve raw log content and document execution-time path changes in the run index. Mark affected static maps/reports stale; do not relabel a historical check as fresh.
- Document study-relevant fixes and unresolved decisions in current state. Append crucial architecture decisions; preserve earlier log entries.
- Check internal links and affected script syntax after organization-only changes. Run behavior/build tests when the actual change warrants them.
