# Deployment Checklist

Complete this checklist before deploying to production.

## Pre-Deployment Checks

### Code Quality

- [ ] All code is committed to version control
- [ ] No debug code or print statements in production code
- [ ] All TODO comments resolved or documented
- [ ] Code follows PEP 8 style guidelines
- [ ] Type hints added to all functions
- [ ] Docstrings present for all public functions/classes

### Testing

- [ ] All unit tests passing
  ```bash
  pytest tests/ -v
  ```
- [ ] Test coverage above 80%
  ```bash
  pytest tests/ --cov=src --cov-report=term-missing
  ```
- [ ] Manual testing completed on all pages
- [ ] Error handling tested with invalid inputs
- [ ] Edge cases tested
- [ ] Performance testing completed

### Code Analysis

- [ ] Flake8 linting passes
  ```bash
  flake8 src/ app/
  ```
- [ ] Black formatting applied
  ```bash
  black src/ app/
  ```
- [ ] Pylint score acceptable
  ```bash
  pylint src/ app/
  ```
- [ ] Security scan completed
  ```bash
  safety check -r requirements.txt
  bandit -r src/ app/
  ```

### Dependencies

- [ ] requirements.txt up to date
- [ ] All dependencies have version constraints
- [ ] No unnecessary dependencies
- [ ] Security vulnerabilities checked
- [ ] License compatibility verified

### Configuration

- [ ] `.streamlit/config.toml` configured for production
- [ ] `runtime.txt` specifies correct Python version
- [ ] `packages.txt` lists all system dependencies
- [ ] `.env.example` provided with all needed variables
- [ ] Secrets documented in `.streamlit/secrets.toml.example`

### Security

- [ ] No secrets in code or config files
- [ ] `.gitignore` properly configured
- [ ] `.streamlit/secrets.toml` not in version control
- [ ] Environment variables used for sensitive data
- [ ] Input validation implemented
- [ ] File upload restrictions in place
- [ ] Error messages don't expose sensitive info
- [ ] HTTPS configured (or will be by platform)

### Documentation

- [ ] README.md complete and accurate
- [ ] DEPLOYMENT.md reviewed
- [ ] CONTRIBUTING.md present
- [ ] SECURITY.md present
- [ ] CHANGELOG.md updated
- [ ] API documentation complete
- [ ] User guide available (in-app or external)

### Files

Required files present:
- [ ] `app/main.py` (entry point)
- [ ] `requirements.txt`
- [ ] `runtime.txt`
- [ ] `packages.txt`
- [ ] `.streamlit/config.toml`
- [ ] `.gitignore`
- [ ] `README.md`
- [ ] `LICENSE`

Optional but recommended:
- [ ] `Dockerfile`
- [ ] `docker-compose.yml`
- [ ] `.dockerignore`
- [ ] `Procfile` (for Heroku)
- [ ] `setup.sh` (for Heroku)
- [ ] `.github/workflows/streamlit-app.yml` (for CI/CD)

### Data

- [ ] Sample data included in `data/raw/`
- [ ] Data format documented
- [ ] Large files not in git (use git LFS if needed)
- [ ] Data privacy compliance verified
- [ ] Data retention policy defined

## Platform-Specific Checks

### Streamlit Cloud

- [ ] GitHub repository is public or organization has Streamlit Cloud access
- [ ] Main file path is `app/main.py`
- [ ] Branch selected (usually `main`)
- [ ] Secrets configured in Streamlit Cloud dashboard
- [ ] Custom subdomain chosen (optional)
- [ ] Advanced settings reviewed

### Docker

- [ ] Dockerfile builds successfully
  ```bash
  docker build -t engagement-prediction-app .
  ```
- [ ] Docker image runs correctly
  ```bash
  docker run -p 8501:8501 engagement-prediction-app
  ```
- [ ] Health check works
  ```bash
  curl http://localhost:8501/_stcore/health
  ```
- [ ] docker-compose.yml tested
  ```bash
  docker-compose up
  ```
- [ ] Environment variables configured
- [ ] Volumes mounted correctly

### Heroku

- [ ] Procfile created
- [ ] setup.sh created and executable
- [ ] Heroku app created
- [ ] Config vars set
- [ ] Buildpacks configured (if needed)
- [ ] Database configured (if using)

### AWS/Cloud Platforms

- [ ] Instance size appropriate for workload
- [ ] Security groups configured
- [ ] Load balancer configured (if needed)
- [ ] SSL certificate configured
- [ ] Monitoring set up
- [ ] Backup strategy defined
- [ ] Auto-scaling configured (if needed)

## Post-Deployment Checks

### Immediate Verification

- [ ] Application loads without errors
- [ ] All pages accessible
- [ ] Data uploads work
- [ ] Predictions run successfully
- [ ] Charts render correctly
- [ ] Export functions work
- [ ] No console errors in browser
- [ ] Mobile responsive (check on mobile device)

### Functionality Testing

- [ ] Upload sample data
- [ ] Navigate through all pages
- [ ] Run a complete workflow:
  - [ ] Upload data
  - [ ] Explore data
  - [ ] Select variables
  - [ ] Generate prediction
  - [ ] View analytics
  - [ ] Export results
- [ ] Test error handling (invalid inputs)
- [ ] Test session state persistence

### Performance

- [ ] Page load time < 5 seconds
- [ ] Prediction time acceptable
- [ ] Charts render smoothly
- [ ] No memory leaks
- [ ] Resource usage reasonable

### Monitoring

- [ ] Access logs available
- [ ] Error logging working
- [ ] Health check endpoint responding
  ```bash
  curl https://your-app-url/_stcore/health
  ```
- [ ] Monitoring dashboard configured (if applicable)

### Documentation

- [ ] Deployment documented
- [ ] URL shared with team
- [ ] User credentials shared (if authentication enabled)
- [ ] Support contacts updated
- [ ] Incident response plan in place

## Production Maintenance

### Regular Tasks

Daily:
- [ ] Check error logs
- [ ] Monitor uptime
- [ ] Review user feedback

Weekly:
- [ ] Check security advisories
- [ ] Review analytics
- [ ] Update documentation as needed

Monthly:
- [ ] Update dependencies
  ```bash
  pip list --outdated
  ```
- [ ] Review and rotate secrets
- [ ] Backup data
- [ ] Performance audit

Quarterly:
- [ ] Security audit
- [ ] Dependency audit
- [ ] Documentation review
- [ ] Feature planning

### Issue Response

When issues occur:
1. Check application logs
2. Check server/platform status
3. Review recent changes
4. Test locally to reproduce
5. Apply fix and test
6. Deploy fix
7. Verify fix in production
8. Document issue and resolution

## Rollback Plan

In case of deployment failure:

### Streamlit Cloud
1. Go to app settings
2. Select previous branch/commit
3. Or revert GitHub commit
4. Wait for automatic redeployment

### Docker
1. Stop current container
2. Remove current container
3. Run previous image version
4. Verify functionality

### Heroku
```bash
heroku rollback
```

### Manual Deployment
1. Checkout previous commit
   ```bash
   git revert <commit-hash>
   ```
2. Redeploy

## Sign-Off

Deployment completed by: ________________

Date: ________________

Checklist completed: [ ] Yes [ ] No

Production URL: ________________

Issues noted: ________________

Next review date: ________________

---

## Quick Reference Commands

### Local Testing
```bash
# Run app locally
streamlit run app/main.py

# Run tests
pytest tests/ -v --cov=src

# Run linters
flake8 src/ app/
black --check src/ app/

# Security check
safety check -r requirements.txt
```

### Docker
```bash
# Build
docker build -t engagement-prediction-app .

# Run
docker run -p 8501:8501 engagement-prediction-app

# Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Git
```bash
# Check status
git status

# Commit changes
git add .
git commit -m "Deploy: description"

# Push to remote
git push origin main

# Tag release
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

### Health Check
```bash
# Local
curl http://localhost:8501/_stcore/health

# Production
curl https://your-app.streamlit.app/_stcore/health

# Using script
python scripts/health_check.py --url https://your-app.streamlit.app
```

---

**Remember**: Always test in a staging environment before deploying to production!
