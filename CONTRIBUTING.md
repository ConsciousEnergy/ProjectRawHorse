# Contributing to Project RawHorse

Thank you for your interest in contributing to Project RawHorse! Whether you're submitting data, writing code, reporting bugs, or improving documentation, every contribution helps advance open intelligence (OPINT) research.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Your First Contribution](#your-first-contribution)
- [How to Contribute](#how-to-contribute)
  - [Contributing Data](#contributing-data)
  - [Contributing Code](#contributing-code)
  - [Reporting Issues](#reporting-issues)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Data Validation Guidelines](#data-validation-guidelines)
- [Code Style Guidelines](#code-style-guidelines)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold these standards.

### Quick Summary

- Be respectful and inclusive
- Focus on constructive feedback
- Prioritize data accuracy and source verification
- Maintain transparency in all contributions
- Respect legal and ethical boundaries

### Unacceptable Behavior

- Submitting classified or sensitive information
- Harassment or discriminatory language
- Submitting false or misleading data
- Violating export control regulations

## Your First Contribution

New to the project? Here's the fastest path to your first contribution:

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ProjectRawHorse.git
   cd ProjectRawHorse
   ```
3. **Install and run** the application:
   - Windows: double-click `START.bat`
   - macOS/Linux: `chmod +x START.sh && ./START.sh`
4. **Find an issue** labeled [`good first issue`](https://github.com/ConsciousEnergy/ProjectRawHorse/labels/good%20first%20issue) on GitHub
5. **Create a branch**, make your change, and submit a pull request

Not sure where to start? Try one of these:
- Fix a typo in documentation
- Add a missing tooltip or label
- Submit a new data entity via the in-app Contribute tab
- Improve an error message

## How to Contribute

### Contributing Data

#### Via the Application (Recommended)

This is the easiest way for non-developers:

1. Open Project RawHorse (run `START.bat` or `START.sh`)
2. Navigate to the **Contribute** tab
3. Provide a GitHub personal access token ([generate one here](https://github.com/settings/tokens))
4. Select contribution type (Entity, Money Flow, or Award)
5. Fill out the form completely with source citations
6. Submit — an automated pull request is created for review

#### Via Manual Pull Request

1. Fork the repository
2. Add your data to the appropriate CSV file:
   - Entities: `data/entities/`
   - Money flows: `data/financial/`
   - Awards: `data/financial/`
   - FOIA targets: `data/foia/`
3. Create a descriptive pull request explaining the data source
4. Wait for review and approval

#### Data Quality Requirements

All data contributions must meet these standards:

**Required:**
- Source from official public databases only
- Provide valid citations (URLs or document references)
- Include all mandatory fields for the data type
- Use consistent naming conventions

**Prohibited:**
- Classified information
- Personally Identifiable Information (PII)
- Proprietary or confidential data
- Unverified or speculative information
- Information subject to export controls

### Contributing Code

#### Areas for Contribution

- **Bug Fixes**: Fix issues or improve stability
- **Features**: Add new analysis capabilities or UI improvements
- **Documentation**: Improve guides, tutorials, or inline docs
- **Tests**: Add unit or integration tests
- **Performance**: Optimize queries or data loading
- **Data Pipelines**: Improve ingestion and enrichment scripts

#### Before You Start

1. Check existing [issues](https://github.com/ConsciousEnergy/ProjectRawHorse/issues) and pull requests
2. Open an issue to discuss major changes before implementing
3. Ensure your development environment is set up correctly (see below)

### Reporting Issues

**For Bugs:**
- Use the [Bug Report template](https://github.com/ConsciousEnergy/ProjectRawHorse/issues/new?template=bug_report.md)
- Describe what happened vs. what you expected
- Provide steps to reproduce
- Include system information (OS, Python version, Node version)
- Attach screenshots if relevant

**For Features:**
- Use the [Feature Request template](https://github.com/ConsciousEnergy/ProjectRawHorse/issues/new?template=feature_request.md)
- Describe the use case and why it would be valuable
- Suggest a potential implementation approach

**For Data Requests:**
- Use the [Data Contribution template](https://github.com/ConsciousEnergy/ProjectRawHorse/issues/new?template=data_contribution.md)
- Or the [OPINT Data Request template](https://github.com/ConsciousEnergy/ProjectRawHorse/issues/new?template=opint_data_request.md) for requesting new database integrations

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 20+ (LTS)
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend (from project root)
cd ..
python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
# In a new terminal, from project root
cd frontend
npm install

# Run frontend dev server
npm run dev
```

- Frontend dev: http://localhost:5173 (Vite dev server, proxies API to 8000)
- Backend API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs

### Database Setup

The SQLite database (`data/prh.db`) is automatically created and populated on first run from CSV files in the `data/` directory (entities, financial, foia, reference subdirectories).

For more details, see the [Developer Guide](docs/DEVELOPER_GUIDE.md).

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Follow code style guidelines (below)
- Add tests for new features
- Update documentation as needed
- Ensure the frontend builds: `cd frontend && npm run build`

### 3. Commit Changes

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add entity timeline visualization"
git commit -m "fix: correct pagination offset in Browse"
git commit -m "docs: update API reference for search endpoint"
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

### 4. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a pull request on GitHub. The [PR template](PULL_REQUEST_TEMPLATE.md) will guide you through the description.

### 5. Code Review

- Address reviewer feedback promptly
- Make requested changes in new commits
- Be open to suggestions and alternatives

### 6. Merge

Once approved, a maintainer will merge your PR.

## Data Validation Guidelines

### Entity Data

**Required Fields:**
- `entity_id`: Unique identifier
- `display_name`: Human-readable name
- `normalized_name`: Standardized name format (UPPERCASE)

**Optional Fields:**
- `entity_type`: Category (e.g., "contractor", "agency")
- `intel_stack_level`: Hierarchy level (L1–L6)

**Validation:**
- No duplicate entity_ids
- Display name must be non-empty
- Normalized names should be UPPERCASE

### Money Flow Data

**Required Fields:**
- `source`: Source entity name
- `target`: Target entity name

**Optional Fields:**
- `relationship`: Type of transaction (e.g., "M&A", "Contract")
- `amount_usd`: Dollar amount (positive number)
- `start_date`: Transaction date (YYYY-MM-DD)
- `source_citation`: Verifiable URL or reference

### Award Data

**Required Fields:**
- One of: `piid`, `recipient_name`, or `recipient_uei`

**Optional Fields:**
- `awarding_agency`: Granting agency
- `award_amount`: Contract value (positive number)
- `action_date`: Award date (valid, not future)
- `description`: Award purpose
- `naics_code`: Industry classification (6 digits)

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for public functions
- Keep functions focused and small (<50 lines)
- Use descriptive variable names with auxiliary verbs (e.g., `is_active`, `has_permission`)
- Prefer `async def` for I/O-bound operations
- Use Pydantic models for input validation

```python
async def get_entities(
    db: Session,
    search: str | None = None,
    limit: int = 100,
) -> list[Entity]:
    """Retrieve entities from database with optional filtering.

    Args:
        db: Database session.
        search: Optional search term.
        limit: Maximum number of results.

    Returns:
        List of Entity objects matching the criteria.
    """
    query = db.query(Entity)
    if search:
        query = query.filter(Entity.display_name.ilike(f"%{search}%"))
    return query.limit(limit).all()
```

### TypeScript/React (Frontend)

- Use TypeScript for type safety
- Use functional components with hooks
- Keep components focused and reusable
- Follow existing CSS patterns (CSS files alongside components)
- Define interfaces for all component props

```typescript
interface EntityTableProps {
  entities: Entity[];
  onSelect: (entity: Entity) => void;
}

export default function EntityTable({ entities, onSelect }: EntityTableProps) {
  return (
    <table className="data-table">
      {/* table content */}
    </table>
  );
}
```

### File Naming

- Python: `snake_case.py` (e.g., `entity_recognition.py`)
- TypeScript/React: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- CSS: Match the component name (e.g., `SearchBar.css` for `SearchBar.tsx`)
- Directories: `lowercase` or `snake_case`

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run build  # Type-check + build (currently no test suite)
```

### Manual Testing Checklist

- [ ] Data loads correctly on startup
- [ ] Search and filtering work as expected
- [ ] Export functions generate valid files
- [ ] GitHub contribution creates proper PR
- [ ] Application runs on target platform

## License

By contributing, you agree that your contributions will be licensed under the [GNU AGPL v3](LICENSE) license.

## Questions?

- [GitHub Discussions](https://github.com/ConsciousEnergy/ProjectRawHorse/discussions) for general questions
- [GitHub Issues](https://github.com/ConsciousEnergy/ProjectRawHorse/issues) for bugs and feature requests
- Check existing Issues and Discussions first

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation (with permission)

### Attribution and privacy

When crediting research or data sources, **use only the public identifier** (e.g. channel name, handle, or username) that the person uses publicly. Do not use real names or other identifying information unless the person has explicitly consented in writing. This applies to documentation, changelogs, release notes, and in-app attribution.

Thank you for helping advance open intelligence research!

---

**Last Updated:** February 2026
