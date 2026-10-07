# SkillRadar: learn the skill that unlocks the most jobs

SerpApi India Hackathon 2026 submission. Track: **Knowledge & Public Interest**.

Live app: https://ai-career-intelligence-platform-iota.vercel.app
API docs: https://backend-production-ba306.up.railway.app/docs

## What it does

Most AI career tools answer "which jobs match my resume?". SkillRadar answers the
question job seekers actually need answered: **which skill should I learn next, and what
is it worth in real jobs?**

A user uploads a resume and picks a target role and city. SkillRadar then:

1. Pulls live Google Jobs postings for that role and city through SerpApi.
2. Extracts the skills each posting requires, using a 55-skill taxonomy with aliases.
3. Finds the postings the candidate is already close to qualifying for (they cover at
   least 25% of the requirements).
4. Scores every missing skill by **jobs unlocked per week of learning**. A posting that
   lists two gaps gives each gap half a job unlock, so skills that block several real
   postings rank highest.
5. Pulls 12-month Google Trends interest for the top skills in India. Rising skills get a
   score boost. Falling skills are down-weighted.
6. Shows every number with the live postings that produced it, each with a link to verify.

The UI streams the agent trace (each SerpApi call and its timing) so the process is visible.

### ATS CV builder

The second half of the loop: once you know what the market wants, apply with a CV that
says it. On the **CV builder** page you pick your uploaded CV, then either paste a job
description or search live postings (Google Jobs via SerpApi) and click **Use this** to
pull the full description in. SkillRadar then:

1. Rewrites the CV for that job (Groq LLM): reorders, rephrases bullets, and mirrors the
   job's exact keywords **only where your real experience supports them**.
2. Verifies the output against your original CV in code, not just in the prompt:
   - skills not evidenced in the original are removed (honest umbrella terms like
     "Machine Learning" are allowed when you have PyTorch or Scikit-learn);
   - employer or institution names absent from the original are blanked;
   - any new technology slipped into a bullet is flagged for you to edit out.
3. Scores ATS keyword coverage before and after, and lists the gaps the job wants that you
   genuinely lack, pointing you back to the market scan to decide which to learn.
4. Exports a single-column, text-based PDF and an editable DOCX (opens in Google Docs or
   Word). No tables, columns, or images, so ATS parsers read it cleanly.

It will not invent experience to raise the score. A CV that claims skills you lack may pass
the ATS filter and then fail the interview.

## Who it helps

Early-career engineers in India choosing what to learn next with limited time. The output
is concrete: a ranked list, the time each skill takes, and the actual postings it unlocks.

## How it uses SerpApi

- **Google Jobs** (`engine=google_jobs`): the core signal. Two pages of live postings per
  scan. Every ranking claim is traceable to these postings.
- **Google Trends** (`engine=google_trends`): one batched request per five skills, 12-month
  interest in India. Produces the rising, stable, or falling label and the score multiplier.
- **Google Jobs, again** in the CV builder: live posting search that pulls a full job
  description to tailor against, so the user never has to copy-paste from a job board.

SerpApi is load-bearing. Without it the product has no market data and no ranking. The
client caches results for 24 hours, so repeat scans cost no credits. A cold scan makes four
SerpApi calls: two Google Jobs pages and two Google Trends batches.

## Setup

Requirements: Python 3.12, Node 20, a SerpApi key (free tier works).

```bash
# backend
cd backend
pip install -r requirements.txt
cp .env.example .env          # set SERPAPI_KEY, GROQ_API_KEY (optional), JWT_SECRET
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                   # open http://localhost:3000/market
```

Run the tests (no network needed):

```bash
cd backend
pytest app/tests/services/test_market_intelligence.py
```

Or run the whole stack with Docker: `docker compose up --build`, then set `SERPAPI_KEY`
in the root `.env`.

## Demo script (under 3 minutes)

1. Sign in and open **Market scan** in the nav.
2. Keep "backend engineer" and "Bangalore, Karnataka, India", and select a resume.
3. Click **Run live market scan**. Point to the agent trace as each SerpApi call completes.
4. Show the stats: postings scanned, already qualified, reachable, and live versus cached calls.
5. Walk down the ranked list. Explain one recommendation: "Redis unlocks 0.37 postings in
   about two weeks, and the market is shown falling, so it ranks lower than it otherwise would."
6. Click one **View posting** link to show the evidence is real.
7. Run the same scan again to show the cache hit and zero extra credits.
8. Open **CV builder**. Search a live posting, click **Use this**, then **Generate**.
9. Show the ATS score before and after, and any removed or flagged claims (this is the
   anti-fabrication guard working). Download the PDF and the DOCX.

## Honest scope and limits

- Market intelligence is new for this hackathon. The resume parsing, authentication, and
  career-assistant features existed before. Those are disclosed below.
- Trend values are relative interest within each batch of five terms, so they are used for
  direction rather than absolute size.
- The skill taxonomy is hand-built (55 skills with aliases and learning-time estimates). The
  learning-time figures are estimates, not measured data.
- Google News, YouTube, and Maps engines are not used in this version.

## Disclosures

- **Existed before the hackathon:** the resume upload and parsing, JWT authentication,
  job matching, and the RAG career assistant. **New for the hackathon:** the market
  intelligence engine (`market_intelligence.py`, `serpapi_client.py`, `skill_taxonomy.py`),
  the `/api/v1/market/scan` endpoint, the market scan page, and the ATS CV builder
  (`cv_tailor.py`, `cv_render.py`, the `/api/v1/cv/*` endpoints, and the CV builder page).
- **AI tools used in development:** Claude (Anthropic), used as a coding assistant for
  design, implementation, debugging, and documentation.
- **AI at runtime:** the career assistant, AI advice, and CV builder call a Groq-hosted
  LLM (`openai/gpt-oss-20b`). The market scan itself uses no LLM. On Groq's free tier the
  CV builder handles about three generations per minute; past that it returns a clear
  "try again in a minute" message.
