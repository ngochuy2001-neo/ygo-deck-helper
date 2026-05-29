# YGO Deck Helper

Monorepo hỗ trợ người chơi Yu-Gi-Oh!: đồng bộ thư viện lá bài (YGOPRODeck), duyệt/lọc lá bài, import decklist `.ydk`, chat với AI agent **DeckHelper**, và **giải thích luật** qua Rulebook RAG + **Rulebook Lab** (AgentScope + LM Studio).

| Thư mục | Vai trò |
|---------|---------|
| `frontend/` | Next.js (App Router), TypeScript, Tailwind |
| `backend/` | FastAPI, PostgreSQL, pgvector RAG |
| `agents/` | AgentScope ReAct agents, tools, LM Studio config |

Tài liệu chi tiết (workflow, DB, API, RAG): **[`docs/README.md`](docs/README.md)**.

## Yêu cầu

- Node.js 20+
- Python 3.10+
- PostgreSQL 14+ với extension **pgvector**
- [LM Studio](https://lmstudio.ai/) — chat model + embedding model

## Cài đặt nhanh

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
```

### Agents

```bash
cd agents
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

## Chạy local

1. **LM Studio** — bật local server, load model chat (Settings) và model embedding (`text-embedding-embeddinggamma-300m-qat` hoặc tương đương).

2. **Backend:**

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend:**

```bash
cd frontend && npm run dev
```

4. Mở `http://localhost:3000` — Dashboard, Thư viện lá bài, **Rulebook RAG**, **Thử nghiệm (Lab)**, Settings.

5. Health: `GET http://localhost:8000/health` → `{"status":"ok","database":"connected"}`

### PostgreSQL

| Biến | Mặc định |
|------|----------|
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_DB` | `ygo-helper` |

```bash
createdb -U postgres ygo-helper
# Cần extension vector (migration 003 tự CREATE EXTENSION)
```

## Rulebook RAG (tóm tắt)

Hệ thống **semantic search** trên tài liệu luật markdown (chunk theo tiêu đề `##`), lưu embedding trong PostgreSQL (**pgvector**).

### Chuẩn bị dữ liệu

1. Vào **`/rulebook-rag`** trên frontend (hoặc API `POST /api/v1/rag/rulebook/ingest`).
2. Upload **từng file** `.md` (mỗi lần ingest chỉ thay chunk của file đó):

| File gợi ý | Nội dung |
|------------|----------|
| `ygo_core_rulebook_summary.md` | Luật cốt lõi, Spell Speed, Chain |
| `ygo_advanced_psct.md` | PSCT, timing, activation |
| `ygo_advanced_conjunctions.md` | And / Then / Also (nội tại 1 lá) |

3. LM Studio phải đang chạy với model embedding (`RAG_EMBEDDING_MODEL` trong `.env`).

### API RAG

| Method | Path | Mô tả |
|--------|------|--------|
| POST | `/api/v1/rag/rulebook/preview` | Xem trước chunk (chưa embed) |
| POST | `/api/v1/rag/rulebook/ingest` | Cắt chunk + embed + lưu DB |
| GET | `/api/v1/rag/rulebook/stats` | Số chunk, danh sách file nguồn |
| POST | `/api/v1/rag/rulebook/search` | Tìm kiếm (có `rag_scope` tùy chọn) |

## Trả lời câu hỏi luật & deck (Agents)

### Rulebook Lab — `/lab`

Luồng giải thích luật (ưu tiên độ chính xác):

```
Câu hỏi → QueryAnalyzer (chuẩn hóa + rag_scope)
        → RAG có lọc intent (tránh nhầm Conjunctions khi hỏi Chain/destroy)
        → YGO Judge Lab agent (system prompt Head Judge + JSON context)
```

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/api/v1/lab/info` | Trạng thái LM Studio, RAG, model lab |
| POST | `/api/v1/lab/chat` | Chat thử nghiệm (`use_rag`, `use_query_analyzer`) |

Biến môi trường: `LAB_CHAT_MODEL`, `QUERY_ANALYZER_ENABLED` — xem `backend/.env.example`.

**Intent RAG** (tự phân loại):

| `rag_scope` | Khi nào | Nguồn retrieve |
|-------------|---------|----------------|
| `chain_interaction` | Destroy/negate trên Chain, Spell Speed | Core rulebook + PSCT — **không** Conjunctions |
| `card_text_resolution` | Then/Also/`:``;` trên một lá | Conjunctions + PSCT |
| `general_rulebook` | Còn lại | Rulebook chung (vẫn loại Conjunctions nếu không phù hợp) |

### DeckHelper — Settings & `/api/v1/agent/chat`

Agent ReAct xây deck / tra cứu lá bài: `query_card_database`, `web_search`. Cũng qua **QueryAnalyzer** trước khi trả lời.

```bash
cd agents && python main_agent.py "Gợi ý deck Dragon Link budget."
```

## API khác (tóm tắt)

| Nhóm | Ví dụ |
|------|--------|
| Lá bài | `GET /api/v1/cards`, `POST /api/v1/cards/sync`, … |
| LM Studio | `GET/PUT /api/v1/settings/lm-studio` |
| Agent deck | `POST /api/v1/agent/chat` |

Static ảnh lá bài: `/static/cards/{passcode}/...`

## CLI agent

```bash
cd agents
source .venv/bin/activate
python main_agent.py "Câu hỏi về deck hoặc lá bài..."
```

## Lưu ý

- Cấu hình LM Studio: trang **Settings** hoặc `agents/config/lm_studio.json`.
- Không commit `.env` / `.env.local`.
- Sau khi đổi code agent/RAG: **restart backend**.

## Tài liệu thêm

- [`docs/README.md`](docs/README.md) — workflow đầy đủ, schema DB, kiến trúc agent
- [`architecture.md`](architecture.md) — quy ước monorepo
- [`todo.md`](todo.md) — tiến độ
