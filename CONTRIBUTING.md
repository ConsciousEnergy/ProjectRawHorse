# Contributing to UAP Data Explorer

Thank you for your interest in contributing to UAP Data Explorer! This document provides guidelines for contributing data, code, and documentation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Contributing Data](#contributing-data)
  - [Contributing Code](#contributing-code)
  - [Reporting Issues](#reporting-issues)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Data Validation Guidelines](#data-validation-guidelines)
- [Code Style Guidelines](#code-style-guidelines)

## Code of Conduct

### Our Standards

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

## How to Contribute

### Contributing Data

#### Via the Application (Recommended)

1. Open UAP Data Explorer
2. Navigate to the "Contribute" page
3. Provide a GitHub personal access token (generate at https://github.com/settings/tokens)
4. Select contribution type (Entity, Money Flow, or Award)
5. Fill out the form completely
6. Submit - an automated pull request will be created

#### Via Manual Pull Request

1. Fork the repository
2. Add your data to the appropriate CSV file in `UAPUFOResearch/UAPUFOResearch/`
3. Create a descriptive pull request
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
- **Documentation**: Improve README, guides, or inline documentation
- **Tests**: Add unit or integration tests
- **Performance**: Optimize queries or data loading

#### Before You Start

1. Check existing issues and pull requests
2. Open an issue to discuss major changes
3. Ensure your development environment is set up correctly

### Reporting Issues

When reporting bugs or requesting features:

**For Bugs:**
- Describe what happened vs. what you expected
- Provide steps to reproduce
- Include system information (OS, Python version, Node version)
- Attach screenshots if relevant
- Check logs for error messages

**For Features:**
- Describe the use case
- Explain why it would be valuable
- Suggest potential implementation approach
- Consider implications for data privacy/security

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/YOUR_ORG/uap-data-explorer.git
cd uap-data-explorer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend
python main.py
```

### Frontend Setup

```bash
# In new terminal
cd frontend
npm install

# Run frontend dev server
npm run dev
```

### Database Setup

The database is automatically created and populated on first run from CSV files in the `UAPUFOResearch` directory.

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
- Ensure all tests pass

### 3. Commit Changes

Use clear, descriptive commit messages:

```bash
git commit -m "Add: Feature description"
git commit -m "Fix: Bug description"
git commit -m "Docs: Documentation update"
```

### 4. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues
- Summary of changes
- Testing performed

### 5. Code Review

- Address reviewer feedback promptly
- Make requested changes in new commits
- Be open to suggestions and alternatives
- Maintain respectful communication

### 6. Merge

Once approved, a maintainer will merge your PR.

## Data Validation Guidelines

### Entity Data

**Required Fields:**
- `entity_id`: Unique identifier
- `display_name`: Human-readable name
- `normalized_name`: Standardized name format

**Optional Fields:**
- `entity_type`: Category (e.g., "contractor", "agency")

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
- `amount_usd`: Dollar amount
- `start_date`: Transaction date (YYYY-MM-DD)
- `source_citation`: URL or reference

**Validation:**
- Amounts must be positive numbers
- Dates must be valid and not in the future
- Source citations must be verifiable URLs

### Award Data

**Required Fields:**
- One of: `piid`, `recipient_name`, or `recipient_uei`

**Optional Fields:**
- `awarding_agency`: Granting agency
- `award_amount`: Contract value
- `action_date`: Award date
- `description`: Award purpose
- `naics_code`: Industry classification

**Validation:**
- Amounts must be positive
- Dates must be valid
- NAICS codes must be 6 digits

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for public functions
- Keep functions focused and small (<50 lines)
- Use descriptive variable names
- Add comments for complex logic

```python
async def get_entities(
    db: Session,
    search: Optional[str] = None,
    limit: int = 100
) -> List[Entity]:
    """
    Retrieve entities from database with optional filtering.
    
    Args:
        db: Database session
        search: Optional search term
        limit: Maximum number of results
        
    Returns:
        List of Entity objects
    """
    query = db.query(Entity)
    if search:
        query = query.filter(Entity.display_name.ilike(f"%{search}%"))
    return query.limit(limit).all()
```

### TypeScript/React (Frontend)

- Use TypeScript for type safety
- Follow React hooks best practices
- Use functional components
- Keep components focused and reusable
- Use CSS modules or styled-components
- Add PropTypes or TypeScript interfaces

```typescript
interface EntityTableProps {
  entities: Entity[];
  onSelect: (entity: Entity) => void;
}

function EntityTable({ entities, onSelect }: EntityTableProps) {
  return (
    <table className="data-table">
      {/* table content */}
    </table>
  );
}
```

### Commit Messages

Format: `<type>: <description>`

Types:
- `Add`: New feature
- `Fix`: Bug fix
- `Docs`: Documentation only
- `Style`: Formatting, no code change
- `Refactor`: Code restructuring
- `Test`: Adding tests
- `Chore`: Maintenance tasks

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Manual Testing Checklist

- [ ] Data loads correctly on startup
- [ ] Search and filtering work as expected
- [ ] Export functions generate valid files
- [ ] GitHub contribution creates proper PR
- [ ] Application runs on target platforms

## Documentation

When contributing:

- Update README.md for user-facing changes
- Update inline code comments
- Add docstrings to new functions
- Update API documentation if applicable

## License

By contributing, you agree that your contributions will be licensed under the GNU AGPL v3 license.

## Questions?

- Open a GitHub Discussion for general questions
- Open an Issue for bug reports or feature requests
- Check existing Issues and Discussions first

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation (with permission)

Thank you for helping make UAP Data Explorer better!

---

**Last Updated:** 2025-11-11
