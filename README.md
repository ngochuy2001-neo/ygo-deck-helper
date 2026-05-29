# YGO Deck Helper

Monorepo gồm frontend Next.js, backend FastAPI và AgentScope ReAct agent (scaffold — chưa triển khai tính năng nghiệp vụ).

## Cấu trúc

- `frontend/` — Next.js App Router, landing + dashboard/login placeholder
- `backend/` — FastAPI skeleton với health check và router stub v1
- `agents/` — AgentScope ReAct agent stub (`DeckHelper`), tools/workflows placeholder

## Yêu cầu

- Node.js 20+
- Python 3.10+
- PostgreSQL 14+ (database `ygo-helper`)
- [LM Studio](https://lmstudio.ai/)

## Cài đặt

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
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

1. Backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Frontend:

```bash
cd frontend
npm run dev
```

3. Mở `http://localhost:3000` — landing page với link tới Dashboard và Login.

4. Kiểm tra backend: `GET http://localhost:8000/health` → `{"status":"ok","database":"connected"}`

### PostgreSQL

Cấu hình trong `backend/.env` (xem `.env.example`):

| Biến | Mặc định |
|------|----------|
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | *(mật khẩu của bạn)* |
| `POSTGRES_DB` | `ygo-helper` |

Tạo database nếu chưa có:

```bash
createdb -U postgres ygo-helper
```

## API (hiện có)

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/health` | Health check (bao gồm trạng thái PostgreSQL) |

## API (planned)

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/api/v1/settings/lm-studio` | Lấy cấu hình LM Studio |
| PUT | `/api/v1/settings/lm-studio` | Lưu cấu hình |
| GET | `/api/v1/settings/lm-studio/status` | Trạng thái LM Studio |
| POST | `/api/v1/agent/chat` | Chạy ReAct agent |

## CLI agent

```bash
cd agents
source .venv/bin/activate
python main_agent.py "Tìm thông tin lá bài Dark Magician."
```

Hiện tại CLI chỉ in stub — agent thật sẽ được triển khai ở bước tiếp theo.

## Lưu ý

- File cấu hình LM Studio (`agents/config/lm_studio.json`) chưa được tạo — sẽ thêm khi tích hợp Settings.
- Không commit `.env` / `.env.local`; chỉ dùng `.env.example` / `.env.local.example`.
