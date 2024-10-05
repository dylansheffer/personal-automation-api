# Personal Automation API

A collection of APIs for automating personal tasks, built with FastAPI and deployable on Unraid.

## Quick Start

### Local Development (M1 MacBook)

1. **Clone and setup:**
   ```bash
   git clone https://github.com/dylansheffer/personal-automation-api.git
   cd personal-automation-api
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY and API_KEY
   ```

2. **Run locally:**
   ```bash
   ./run.sh start
   ```

3. **Access API:** Open `http://localhost:1621`

### Deployment on Unraid

1. **Initial Setup:**
   - In Unraid, go to "Apps" > search for "personal-automation-api"
   - Click "Install" and configure:
     - `API_KEY`: Your personal API key
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `WebUI Port`: Default is 1621
   - Click "Apply"

2. **Access:** Navigate to `http://[YOUR_UNRAID_IP]:1621`

### Updating on Unraid

1. **Push changes to GitHub:**
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```

2. **GitHub Actions:**
   - Automatically builds and pushes a new Docker image to Docker Hub.

3. **Update on Unraid:**
   a. **Manual Update:**
      - In Unraid, go to the Docker tab.
      - Find "personal-automation-api" and click "Update".
      - Unraid will pull the latest image and restart the container.
   
   b. **Automatic Update (Optional):**
      - Install a plugin like "Docker Auto Update" from Community Applications.
      - Configure it to check for updates to your container periodically.

4. **Template Updates:**
   - If you've made changes to the template itself:
     - Update the template file in your GitHub repository.
     - Users need to manually update the template in Unraid's Community Applications.

Note: The frequency of updates depends on your Unraid settings or any auto-update plugins you've installed.

### Making Changes

1. **Edit code locally**
2. **Test:**
   ```bash
   ./run.sh start
   ```
3. **If successful, push to GitHub (see "Updating on Unraid")**

## Key Components

- `app/main.py`: FastAPI application entry point
- `app/api.py`: API endpoints
- `Dockerfile`: Multi-architecture image configuration
- `run.sh`: Script for building and running the application locally
- `.github/workflows/deploy.yml`: CI/CD pipeline

## Current Endpoints

- `/video_summary`: YouTube video summarizer
- `/generate_follow_up`: Structured response generator

## Adding New Endpoints

1. Open `app/api.py`
2. Add new endpoint function:
   ```python
   @router.post("/new_endpoint")
   async def new_endpoint(data: SomeModel):
       # Your logic here
       return {"result": result}
   ```
3. If needed, add new models in `app/models.py`
4. Test locally, then deploy (see "Updating on Unraid")

## Troubleshooting

- **API not responding:** Check Unraid Docker logs
- **Changes not reflecting:** Ensure GitHub Actions completed successfully