# YGO Deck Helper — Tiến độ

## Đã hoàn thành

- [x] Scaffold monorepo (`frontend/`, `backend/`, `agents/`) + cấu hình tối thiểu
- [x] Backend FastAPI skeleton: settings, CORS, `GET /health`, router stub v1
- [x] Agents skeleton: tools/workflows stub, AgentScope trong `requirements.txt`
- [x] Frontend Next.js: landing, dashboard placeholder, login placeholder, `services/api.ts`
- [x] Cấu hình LM Studio dùng chung (`agents/config/lm_studio.json` + `lm_studio.py`)
- [x] Backend: settings + status + agent chat API
- [x] AgentScope ReAct agent (`agents/workflows/react_deck_agent.py`) với LM Studio
- [x] Frontend Settings: trạng thái kết nối, chọn model, thử agent
- [x] PostgreSQL: SQLAlchemy async + health check (`ygo-helper`)

## Bước tiếp theo

- [ ] ORM models & migrations (Alembic) cho lá bài / deck
- [ ] Tích hợp API YGO thật cho tools
- [ ] Auth (đăng nhập/đăng ký)
- [ ] Agent monitor streaming (SSE)
- [ ] Trang xây dựng deck đầy đủ
