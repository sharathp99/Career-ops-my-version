# chatgpt-career-ops (Stage 3)

Local desktop-style application for job intake, tracker management, JD processing, and OpenAI-powered tailored resume generation.

## Environment variables
- `DATABASE_URL=sqlite:///./career_ops.db`
- `OPENAI_API_KEY=<your_key>`
- `OPENAI_MODEL=gpt-5.4`
- `MASTER_RESUME_PATH=data/sample_master_resume.md`
- `MASTER_PROFILE_PATH=data/sample_master_profile.json`

## Quickstart
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
```


# adding coments 
# for testing 

## Local run commands
```bash
uvicorn app.main:app --reload
streamlit run src/ui/streamlit_app.py
```

## Batch generation command
```bash
careerops generate-resumes-batch
```

## Test commands
```bash
pytest -q
```

## API endpoints
- Stage 1/2 endpoints remain available.
- New Stage 3 endpoints:
  - `POST /resumes/generate/{job_id}`
  - `POST /resumes/generate-batch`
  - `GET /resumes/{job_id}`
  - `GET /resumes/{job_id}/download/pdf`
