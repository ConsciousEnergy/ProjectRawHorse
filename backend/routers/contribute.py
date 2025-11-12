"""
Contribution API routes for submitting new data via GitHub PR
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from models.schemas import ContributionBase, ContributionResponse, EntityCreate, MoneyFlowCreate, AwardCreate, FOIATargetCreate
from services.github_service import GitHubService

# Import database dependency
from dependencies import get_db

router = APIRouter()


@router.post("/entity", response_model=ContributionResponse)
async def contribute_entity(
    entity: EntityCreate,
    contributor_name: str = None,
    contributor_email: str = None,
    notes: str = None,
    github_token: str = Header(None, alias="X-GitHub-Token"),
    db: Session = Depends(get_db)
):
    """Submit a new entity contribution via GitHub PR"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    try:
        github_service = GitHubService(github_token)
        
        # Create PR with new entity data
        pr_url = github_service.create_entity_pr(
            entity=entity,
            contributor_name=contributor_name,
            contributor_email=contributor_email,
            notes=notes
        )
        
        return ContributionResponse(
            success=True,
            message="Entity contribution submitted successfully",
            pr_url=pr_url
        )
    except Exception as e:
        return ContributionResponse(
            success=False,
            message=f"Error creating contribution: {str(e)}",
            pr_url=None
        )


@router.post("/money-flow", response_model=ContributionResponse)
async def contribute_money_flow(
    money_flow: MoneyFlowCreate,
    contributor_name: str = None,
    contributor_email: str = None,
    notes: str = None,
    github_token: str = Header(None, alias="X-GitHub-Token"),
    db: Session = Depends(get_db)
):
    """Submit a new money flow contribution via GitHub PR"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    try:
        github_service = GitHubService(github_token)
        
        pr_url = github_service.create_money_flow_pr(
            money_flow=money_flow,
            contributor_name=contributor_name,
            contributor_email=contributor_email,
            notes=notes
        )
        
        return ContributionResponse(
            success=True,
            message="Money flow contribution submitted successfully",
            pr_url=pr_url
        )
    except Exception as e:
        return ContributionResponse(
            success=False,
            message=f"Error creating contribution: {str(e)}",
            pr_url=None
        )


@router.post("/award", response_model=ContributionResponse)
async def contribute_award(
    award: AwardCreate,
    contributor_name: str = None,
    contributor_email: str = None,
    notes: str = None,
    github_token: str = Header(None, alias="X-GitHub-Token"),
    db: Session = Depends(get_db)
):
    """Submit a new award contribution via GitHub PR"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    try:
        github_service = GitHubService(github_token)
        
        pr_url = github_service.create_award_pr(
            award=award,
            contributor_name=contributor_name,
            contributor_email=contributor_email,
            notes=notes
        )
        
        return ContributionResponse(
            success=True,
            message="Award contribution submitted successfully",
            pr_url=pr_url
        )
    except Exception as e:
        return ContributionResponse(
            success=False,
            message=f"Error creating contribution: {str(e)}",
            pr_url=None
        )


@router.post("/foia-target", response_model=ContributionResponse)
async def contribute_foia_target(
    foia_target: FOIATargetCreate,
    contributor_name: str = None,
    contributor_email: str = None,
    notes: str = None,
    github_token: str = Header(None, alias="X-GitHub-Token"),
    db: Session = Depends(get_db)
):
    """Submit a new FOIA target contribution via GitHub PR"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    try:
        github_service = GitHubService(github_token)
        
        pr_url = github_service.create_foia_target_pr(
            foia_target=foia_target,
            contributor_name=contributor_name,
            contributor_email=contributor_email,
            notes=notes
        )
        
        return ContributionResponse(
            success=True,
            message="FOIA target contribution submitted successfully",
            pr_url=pr_url
        )
    except Exception as e:
        return ContributionResponse(
            success=False,
            message=f"Error creating contribution: {str(e)}",
            pr_url=None
        )


@router.get("/validate-token")
async def validate_github_token(
    github_token: str = Header(None, alias="X-GitHub-Token")
):
    """Validate GitHub token"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    try:
        github_service = GitHubService(github_token)
        is_valid = github_service.validate_token()
        
        if is_valid:
            return {"valid": True, "message": "Token is valid"}
        else:
            return {"valid": False, "message": "Token is invalid"}
    except Exception as e:
        return {"valid": False, "message": str(e)}
