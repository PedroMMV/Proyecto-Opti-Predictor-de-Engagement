# Deployment Guide

Complete guide for deploying the Engagement Prediction Application to various platforms.

## Table of Contents

1. [Pre-requisites](#pre-requisites)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [AWS Deployment](#aws-deployment)
6. [Environment Variables](#environment-variables)
7. [Troubleshooting](#troubleshooting)

---

## Pre-requisites

### Required Tools
- Python 3.10 or higher
- Git
- Docker (optional, for containerized deployment)
- GitHub account
- Streamlit Cloud account (for Streamlit deployment)

### Repository Setup
1. Ensure your code is in a Git repository
2. Push your code to GitHub
3. Verify all tests pass locally

```bash
# Run tests
pytest tests/ -v

# Check linting
flake8 src/ app/
black --check src/ app/
```

---

## Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. Ensure these files exist in your repository:
   - `requirements.txt` - Python dependencies
   - `runtime.txt` - Python version
   - `packages.txt` - System dependencies
   - `.streamlit/config.toml` - Streamlit configuration

2. Commit and push all changes to GitHub:
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Choose the branch (usually `main`)
6. Set the main file path: `app/main.py`

### Step 3: Configure Secrets

1. In Streamlit Cloud dashboard, go to your app settings
2. Click on "Secrets"
3. Add any secrets from `.streamlit/secrets.toml.example`
4. Format:
```toml
# Add your secrets here
[general]
# api_key = "your-key"
```

### Step 4: Deploy

1. Click "Deploy!"
2. Wait for the build to complete (usually 2-5 minutes)
3. Your app will be available at: `https://[app-name].streamlit.app`

### Step 5: Verify Deployment

1. Check that the app loads correctly
2. Test all pages and functionality
3. Verify data loading works
4. Test predictions

### Monitoring and Maintenance

- **Logs**: Access logs in the Streamlit Cloud dashboard
- **Reboot**: Use "Reboot app" if issues occur
- **Updates**: Push to GitHub to trigger automatic redeployment

---

## Docker Deployment

### Local Docker Deployment

1. **Build the Docker image**:
```bash
docker build -t engagement-prediction-app .
```

2. **Run the container**:
```bash
docker run -p 8501:8501 engagement-prediction-app
```

3. **Access the app**:
   - Open browser to `http://localhost:8501`

### Docker Compose Deployment

1. **Start the application**:
```bash
docker-compose up -d
```

2. **View logs**:
```bash
docker-compose logs -f
```

3. **Stop the application**:
```bash
docker-compose down
```

4. **Access the app**:
   - Open browser to `http://localhost:8501`

### Docker Hub Deployment

1. **Tag your image**:
```bash
docker tag engagement-prediction-app yourusername/engagement-prediction-app:latest
```

2. **Push to Docker Hub**:
```bash
docker login
docker push yourusername/engagement-prediction-app:latest
```

3. **Pull and run on any server**:
```bash
docker pull yourusername/engagement-prediction-app:latest
docker run -p 8501:8501 yourusername/engagement-prediction-app:latest
```

---

## Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. **Create Heroku app**:
```bash
heroku create your-app-name
```

2. **Create `Procfile`** (if not exists):
```
web: streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0
```

3. **Create `setup.sh`**:
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

4. **Deploy**:
```bash
git push heroku main
```

5. **Open app**:
```bash
heroku open
```

---

## AWS Deployment

### Option 1: AWS EC2

1. **Launch EC2 instance**:
   - Ubuntu 20.04 LTS
   - t2.medium or larger
   - Security group: Allow port 8501

2. **SSH into instance**:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip python3-venv git
```

4. **Clone repository**:
```bash
git clone https://github.com/yourusername/engagement-prediction-app.git
cd engagement-prediction-app
```

5. **Install Python packages**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Run with nohup**:
```bash
nohup streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0 &
```

### Option 2: AWS Elastic Beanstalk

1. **Install EB CLI**:
```bash
pip install awsebcli
```

2. **Initialize EB**:
```bash
eb init -p python-3.10 engagement-prediction-app
```

3. **Create environment**:
```bash
eb create engagement-production
```

4. **Deploy**:
```bash
eb deploy
```

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STREAMLIT_SERVER_PORT` | Port for Streamlit | 8501 |
| `STREAMLIT_SERVER_ADDRESS` | Address to bind | 0.0.0.0 |
| `DATA_PATH` | Path to data directory | ./data |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) |
| `MAX_UPLOAD_SIZE` | Maximum file upload size (MB) |
| `SESSION_TIMEOUT` | Session timeout (seconds) |

### Setting Environment Variables

**Streamlit Cloud**:
- Use the Secrets management in dashboard

**Docker**:
```bash
docker run -e STREAMLIT_SERVER_PORT=8501 -p 8501:8501 engagement-prediction-app
```

**Heroku**:
```bash
heroku config:set VARIABLE_NAME=value
```

**Local**:
Create `.env` file:
```
STREAMLIT_SERVER_PORT=8501
DATA_PATH=./data
```

---

## Troubleshooting

### Common Issues

#### Issue: App fails to start
**Solution**:
1. Check logs for error messages
2. Verify all dependencies are installed
3. Ensure Python version is 3.10+
4. Check that data files are accessible

#### Issue: Module not found errors
**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

#### Issue: Port already in use
**Solution**:
```bash
# Linux/Mac
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### Issue: Data files not loading
**Solution**:
1. Verify data files are in `data/raw/`
2. Check file permissions
3. Verify file paths in configuration

#### Issue: Memory errors
**Solution**:
1. Increase container/instance memory
2. Optimize data loading (load in chunks)
3. Clear cache regularly

### Streamlit Cloud Specific

#### Issue: Build timeout
**Solution**:
- Reduce dependencies in requirements.txt
- Use lighter versions of packages
- Increase build timeout in settings

#### Issue: Secret not found
**Solution**:
1. Verify secret name matches code
2. Check TOML syntax in secrets
3. Restart the app after adding secrets

### Docker Specific

#### Issue: Image build fails
**Solution**:
1. Check Dockerfile syntax
2. Verify base image is accessible
3. Review build logs for specific errors

#### Issue: Container exits immediately
**Solution**:
```bash
docker logs <container-id>
```
Check logs for startup errors

---

## Performance Optimization

### For Production

1. **Enable caching**:
```python
@st.cache_data
def load_data():
    # Your data loading code
    pass
```

2. **Optimize data loading**:
   - Use parquet instead of CSV
   - Load data incrementally
   - Use database for large datasets

3. **Reduce package size**:
   - Remove unused dependencies
   - Use slim versions of packages

4. **Configure resource limits**:
```yaml
# docker-compose.yml
services:
  streamlit:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Security Best Practices

1. **Never commit secrets**:
   - Use `.gitignore` for secrets
   - Use environment variables
   - Use secret management services

2. **Enable HTTPS**:
   - Use reverse proxy (nginx)
   - Configure SSL certificates
   - Force HTTPS redirects

3. **Restrict access**:
   - Use authentication
   - Implement IP whitelisting
   - Add rate limiting

4. **Keep dependencies updated**:
```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

---

## Monitoring

### Health Checks

The application includes a health check endpoint:
```
http://your-app-url/_stcore/health
```

### Logging

Logs are stored in:
- **Streamlit Cloud**: View in dashboard
- **Docker**: `docker logs <container-id>`
- **Local**: `logs/` directory

### Metrics to Monitor

- Response time
- Error rate
- Memory usage
- CPU usage
- Active users
- Prediction requests

---

## Backup and Recovery

### Backup

1. **Data backup**:
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

2. **Configuration backup**:
```bash
# Backup config files
cp .streamlit/config.toml .streamlit/config.toml.backup
```

### Recovery

1. **Restore from backup**:
```bash
tar -xzf backup-20250118.tar.gz
```

2. **Revert to previous version**:
```bash
git revert <commit-hash>
git push origin main
```

---

## Support and Maintenance

### Regular Maintenance Tasks

- Update dependencies monthly
- Review logs weekly
- Test functionality after updates
- Backup data regularly
- Monitor performance metrics

### Getting Help

- Check logs first
- Review documentation
- Search GitHub issues
- Contact support team

---

## Next Steps

After successful deployment:

1. Set up monitoring and alerts
2. Configure automated backups
3. Implement CI/CD pipeline
4. Set up staging environment
5. Document runbook procedures

For detailed Streamlit Cloud setup, see [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)
