"""
GitHub service for creating PRs with contributed data
"""
import os
import csv
import hashlib
from datetime import datetime
from typing import Optional
from github import Github, GithubException
import io

from models.schemas import EntityCreate, MoneyFlowCreate, AwardCreate, FOIATargetCreate


class GitHubService:
    def __init__(self, token: str, repo_url: str = "YOUR_ORG/UAPUFOResearch"):
        """Initialize GitHub service with token"""
        self.token = token
        self.github = Github(token)
        self.repo_name = repo_url
    
    def validate_token(self) -> bool:
        """Validate GitHub token"""
        try:
            user = self.github.get_user()
            user.login  # This will raise exception if token is invalid
            return True
        except GithubException:
            return False
    
    def _get_or_create_fork(self):
        """Get existing fork or create new one"""
        try:
            user = self.github.get_user()
            repo = self.github.get_repo(self.repo_name)
            
            # Check if fork already exists
            try:
                fork = user.get_repo(repo.name)
                return fork
            except GithubException:
                # Create fork
                return user.create_fork(repo)
        except GithubException as e:
            raise Exception(f"Error accessing repository: {str(e)}")
    
    def _create_branch(self, fork, branch_name: str):
        """Create a new branch in fork"""
        try:
            # Get default branch
            default_branch = fork.get_branch(fork.default_branch)
            
            # Create new branch
            fork.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=default_branch.commit.sha
            )
            
            return branch_name
        except GithubException as e:
            raise Exception(f"Error creating branch: {str(e)}")
    
    def _generate_branch_name(self, contribution_type: str) -> str:
        """Generate unique branch name"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"contribution/{contribution_type}/{timestamp}"
    
    def create_entity_pr(
        self,
        entity: EntityCreate,
        contributor_name: Optional[str] = None,
        contributor_email: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create PR with new entity"""
        fork = self._get_or_create_fork()
        branch_name = self._generate_branch_name("entity")
        self._create_branch(fork, branch_name)
        
        # Prepare CSV row
        csv_content = f"{entity.entity_id},{entity.display_name},{entity.normalized_name},{entity.entity_type or ''}\n"
        
        # Get current file content
        file_path = "UAPUFOResearch/uap_entities_master.csv"
        try:
            file = fork.get_contents(file_path, ref=branch_name)
            current_content = file.decoded_content.decode('utf-8')
            new_content = current_content + csv_content
            
            # Update file
            fork.update_file(
                path=file_path,
                message=f"Add entity: {entity.display_name}",
                content=new_content,
                sha=file.sha,
                branch=branch_name
            )
        except GithubException:
            # File doesn't exist, create it
            fork.create_file(
                path=file_path,
                message=f"Add entity: {entity.display_name}",
                content=csv_content,
                branch=branch_name
            )
        
        # Create PR
        pr_body = self._generate_pr_body("entity", entity, contributor_name, contributor_email, notes)
        
        upstream = self.github.get_repo(self.repo_name)
        pr = upstream.create_pull(
            title=f"Add entity: {entity.display_name}",
            body=pr_body,
            head=f"{fork.owner.login}:{branch_name}",
            base=upstream.default_branch
        )
        
        return pr.html_url
    
    def create_money_flow_pr(
        self,
        money_flow: MoneyFlowCreate,
        contributor_name: Optional[str] = None,
        contributor_email: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create PR with new money flow"""
        fork = self._get_or_create_fork()
        branch_name = self._generate_branch_name("money-flow")
        self._create_branch(fork, branch_name)
        
        # Prepare CSV row
        csv_content = f"{money_flow.source},{money_flow.target},{money_flow.relationship or ''},{money_flow.amount_usd or ''},{money_flow.start_date or ''},{money_flow.source_citation or ''}\n"
        
        # Similar logic to entity PR
        file_path = "UAPUFOResearch/uap_money_edges.csv"
        try:
            file = fork.get_contents(file_path, ref=branch_name)
            current_content = file.decoded_content.decode('utf-8')
            new_content = current_content + csv_content
            
            fork.update_file(
                path=file_path,
                message=f"Add money flow: {money_flow.source} -> {money_flow.target}",
                content=new_content,
                sha=file.sha,
                branch=branch_name
            )
        except GithubException:
            fork.create_file(
                path=file_path,
                message=f"Add money flow: {money_flow.source} -> {money_flow.target}",
                content=csv_content,
                branch=branch_name
            )
        
        pr_body = self._generate_pr_body("money_flow", money_flow, contributor_name, contributor_email, notes)
        
        upstream = self.github.get_repo(self.repo_name)
        pr = upstream.create_pull(
            title=f"Add money flow: {money_flow.source} -> {money_flow.target}",
            body=pr_body,
            head=f"{fork.owner.login}:{branch_name}",
            base=upstream.default_branch
        )
        
        return pr.html_url
    
    def create_award_pr(
        self,
        award: AwardCreate,
        contributor_name: Optional[str] = None,
        contributor_email: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create PR with new award"""
        fork = self._get_or_create_fork()
        branch_name = self._generate_branch_name("award")
        self._create_branch(fork, branch_name)
        
        # Prepare CSV row
        csv_content = f"{award.piid or ''},{award.recipient_name or ''},{award.recipient_uei or ''},{award.awarding_agency or ''},{award.award_amount or ''},{award.action_date or ''}\n"
        
        file_path = "UAPUFOResearch/awards.csv"
        try:
            file = fork.get_contents(file_path, ref=branch_name)
            current_content = file.decoded_content.decode('utf-8')
            new_content = current_content + csv_content
            
            fork.update_file(
                path=file_path,
                message=f"Add award: {award.recipient_name}",
                content=new_content,
                sha=file.sha,
                branch=branch_name
            )
        except GithubException:
            fork.create_file(
                path=file_path,
                message=f"Add award: {award.recipient_name}",
                content=csv_content,
                branch=branch_name
            )
        
        pr_body = self._generate_pr_body("award", award, contributor_name, contributor_email, notes)
        
        upstream = self.github.get_repo(self.repo_name)
        pr = upstream.create_pull(
            title=f"Add award: {award.recipient_name}",
            body=pr_body,
            head=f"{fork.owner.login}:{branch_name}",
            base=upstream.default_branch
        )
        
        return pr.html_url
    
    def create_foia_target_pr(
        self,
        foia_target: FOIATargetCreate,
        contributor_name: Optional[str] = None,
        contributor_email: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create PR with new FOIA target"""
        fork = self._get_or_create_fork()
        branch_name = self._generate_branch_name("foia-target")
        self._create_branch(fork, branch_name)
        
        # Prepare CSV row
        csv_content = f"{foia_target.agency},{foia_target.record_request},{foia_target.timeframe or ''},{foia_target.relevance or ''},{foia_target.notes or ''}\n"
        
        file_path = "UAPUFOResearch/foia_targets.csv"
        try:
            file = fork.get_contents(file_path, ref=branch_name)
            current_content = file.decoded_content.decode('utf-8')
            new_content = current_content + csv_content
            
            fork.update_file(
                path=file_path,
                message=f"Add FOIA target: {foia_target.agency}",
                content=new_content,
                sha=file.sha,
                branch=branch_name
            )
        except GithubException:
            fork.create_file(
                path=file_path,
                message=f"Add FOIA target: {foia_target.agency}",
                content=csv_content,
                branch=branch_name
            )
        
        pr_body = self._generate_pr_body("foia_target", foia_target, contributor_name, contributor_email, notes)
        
        upstream = self.github.get_repo(self.repo_name)
        pr = upstream.create_pull(
            title=f"Add FOIA target: {foia_target.agency} - {foia_target.record_request}",
            body=pr_body,
            head=f"{fork.owner.login}:{branch_name}",
            base=upstream.default_branch
        )
        
        return pr.html_url
    
    def _generate_pr_body(
        self,
        data_type: str,
        data: any,
        contributor_name: Optional[str],
        contributor_email: Optional[str],
        notes: Optional[str]
    ) -> str:
        """Generate PR description"""
        body = f"## Data Contribution: {data_type}\n\n"
        
        if contributor_name:
            body += f"**Contributor:** {contributor_name}\n"
        if contributor_email:
            body += f"**Email:** {contributor_email}\n"
        
        body += f"\n**Data:**\n```\n{data}\n```\n\n"
        
        if notes:
            body += f"**Notes:** {notes}\n\n"
        
        body += "---\n*This contribution was submitted via Project RawHorse*"
        
        return body
