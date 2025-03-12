# GitHub Collaboration Workflow Guide

This document outlines our team's workflow for collaborating on our GitHub repository.

## Issue-Based Development Process

### Step 1: Create an Issue

1. Go to our repository and click on the "Issues" tab
2. Click "New issue"
3. Create a detailed issue with:
   - Clear, descriptive title
   - Detailed description including:
     - The problem or feature needed
     - Location of code to be modified
     - Specific requirements
   - Appropriate labels (e.g., "enhancement", "bug", "api")
   - Assign to the team member responsible

### Step 2: Add to GitHub Projects

1. Go to the Projects tab in our repository
2. Add the new issue to our project board in the "To Do" column
3. Set any relevant metadata (priority, milestone, etc.)

### Step 3: Create a Feature Branch

1. Clone the repository (if not already done)
2. Pull the latest changes from the main branch:
   ```bash
   git pull origin main
   ```
3. Create a new branch for your feature:
   ```bash
   git checkout -b feature/descriptive-name
   ```
   * Use prefixes like `feature/`, `bugfix/`, or `hotfix/` followed by a descriptive name

### Step 4: Implement the Requested Changes

1. Make the necessary code changes
2. Follow our code style guidelines
3. Add appropriate comments and documentation
4. Write tests for new functionality

### Step 5: Commit and Push Changes

1. Commit your changes with descriptive messages:
   ```bash
   git add .
   git commit -m "Implement feature X that does Y"
   ```
2. Push your branch to GitHub:
   ```bash
   git push origin feature/descriptive-name
   ```

### Step 6: Create a Pull Request

1. Go to our repository on GitHub
2. Create a PR from your feature branch to main
3. Include in the PR description:
   - A summary of changes made
   - Reference to the issue (e.g., "Fixes #123")
   - Any testing considerations or notes for reviewers

### Step 7: Review Process

1. Assigned reviewers examine the code for:
   - Functionality (does it meet requirements?)
   - Code quality and style
   - Test coverage
2. Reviewers can:
   - Comment on specific lines
   - Request changes
   - Approve the PR
3. Address any feedback by making additional commits to your branch

### Step 8: Merge the Pull Request

Once approved:
1. Merge the PR into the main branch
2. The issue will automatically close if referenced correctly
3. The card in GitHub Projects will move to "Done"

### Step 9: Update Local Repository

After merging:
1. Switch back to the main branch:
   ```bash
   git checkout main
   ```
2. Pull the latest changes:
   ```bash
   git pull origin main
   ```
3. Delete your local feature branch (optional):
   ```bash
   git branch -d feature/descriptive-name
   ```
