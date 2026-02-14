# Uninstall Feature Plan

**Status:** Implemented (v0.3.3 Beta)  
**Goal:** One-click (or double-click) uninstall for Windows, macOS, and Linux.

---

## Implemented Behavior

### Scripts

- **UNINSTALL.bat** (Windows): Double-click or run `UNINSTALL.bat [/force]`. Removes all install and generated artifacts; prompts for confirmation and whether to keep `data\prh.db`. Uses port-8000 check (netstat) for server detection; long-path fallback (robocopy) for `frontend\node_modules` when `rmdir` fails. Prints a removal summary (R=removed, K=kept, N=not found).
- **UNINSTALL.sh** (macOS/Linux): Run `./UNINSTALL.sh [--force|-y]`. Same behavior; server detection via `lsof` or `ss` on port 8000; prompts for Linux desktop entry removal. Uses `set -u` only (no `set -e`) so missing artifacts do not abort the script.

### Artifacts Removed

| Artifact | Path | Notes |
|----------|------|-------|
| Python venv | `venv/` or `../venv/` | Whichever exists (matches install/RUN/START logic) |
| Node modules | `frontend/node_modules/` | Windows: robocopy fallback if long paths |
| PyInstaller output | `dist/`, `build/` | If user ran build |
| Compiled frontend | `backend/static/`, `frontend/dist/` | Both the copy and the build output |
| PyInstaller spec | `rawhorse.spec` | |
| Environment config | `.env` | |
| Database | `data/prh.db` | Only if user chooses to delete (prompted) |
| Enrichment cache | `data/scripts/.cache/` | |
| Python cache | `backend/**/__pycache__/` | Recursive |
| Logs | `logs/`, `*.log` (root) | |
| Enrichment outputs | `data/financial/enriched_flows_*.csv`, `data/financial/test_*.csv` | |
| Backups | `*.backup`, `*_backup.py`, `*_backup*.csv` (root and data) | |
| Linux desktop entry | `~/.local/share/applications/ProjectRawHorse.desktop` | Prompted (or removed with --force) |

**Never removed:** pip/npm system cache, Python/Node installs, user files outside the project.

### User Flow

1. User runs UNINSTALL.bat or UNINSTALL.sh.
2. Banner and list of what will be removed are printed.
3. **Confirmation:** "Continue with uninstall? (y/n)" (skipped if /force or --force/-y).
4. **Server check:** If port 8000 is in use, warn and offer to stop the process (skipped in force mode).
5. **Database:** "Keep your database (data/prh.db) for future use? (y/n)" (force mode defaults to delete).
6. Artifacts are removed in order; each step is tolerant of missing paths.
7. **Linux only:** If desktop entry exists, prompt "Remove Linux desktop entry? (y/n)" (force mode removes it).
8. **Removal summary** is printed (R/K/N per artifact).
9. User is told to delete the project folder to finish (script does not delete itself).

### Edge Cases Handled

- **venv at ../venv:** Both `venv/` and `../venv/` are checked; whichever exists is removed.
- **Partial install:** All removal steps guard with "if exist" (Windows) or `[[ -d ]]` / `[[ -f ]]` (Unix); no step fails if the artifact is missing.
- **Running server:** Port 8000 is checked (netstat on Windows, lsof or ss on Unix). User can choose to kill the process before continuing.
- **Windows long paths:** If `rmdir /s /q frontend\node_modules` leaves the directory (long-path issue), script uses robocopy with an empty dir to mirror-empty then rmdir.
- **Idempotent:** Running uninstall twice completes without errors; summary shows N for already-removed items.

### Documentation Updated

- **README.md:** Quick Start includes an "Uninstall" line; project structure lists UNINSTALL.bat and UNINSTALL.sh.
- **INSTALL_GUIDE.md:** "Uninstalling Project RawHorse (Windows)" and "Uninstalling Project RawHorse" (macOS, step 6) with prompts and /force / --force.
- **QUICKSTART.md:** Uninstall line under Windows and under macOS/Linux options.
- **CHANGELOG_v0.3.3Beta.md:** "One-Click Uninstall" under New Features; Files Changed lists UNINSTALL.bat, UNINSTALL.sh, and doc updates.

---

## Files Created / Modified

| File | Change |
|------|--------|
| `UNINSTALL.bat` | Created. Full logic as above. |
| `UNINSTALL.sh` | Created. Full logic as above. |
| `README.md` | Uninstall line and structure entries. |
| `INSTALL_GUIDE.md` | Windows and macOS uninstall sections. |
| `QUICKSTART.md` | Uninstall lines for Windows and macOS/Linux. |
| `CHANGELOG_v0.3.3Beta.md` | One-Click Uninstall feature and file list. |
| `docs/development/UNINSTALL_PLAN.md` | This document (refined to match implementation). |

---

## Testing

1. **Windows:** Double-click UNINSTALL.bat after full install. Verify venv (or ../venv), node_modules, backend/static, frontend/dist, .env, and optionally data/prh.db are removed. Run again; summary should show N for missing items. Test UNINSTALL.bat /force (no prompts, database removed).
2. **macOS/Linux:** Run ./UNINSTALL.sh; same checks. Verify Linux desktop entry prompt when file exists. Test ./UNINSTALL.sh --force.
3. **Running server:** Start app (port 8000), run uninstall; verify warning and optional kill. Confirm uninstall can then remove artifacts.
4. **Long-path (Windows):** If node_modules is deep, verify robocopy fallback runs when rmdir fails and directory is removed.

---

## Open Questions (unchanged)

1. **Remove entire project folder?** Current: no; user is instructed to delete the folder. Alternative: schedule rmdir on Windows after script exit.
2. **Reinstall option?** e.g. "Remove dependencies but keep data and config" could be a separate script or --clean on install.
3. **Registry / PATH:** Install does not modify these; nothing to undo.
