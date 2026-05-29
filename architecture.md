# KIẾN TRÚC DỰ ÁN (PROJECT ARCHITECTURE)

Tài liệu này quy định cấu trúc thư mục và nguyên tắc tổ chức mã nguồn cho toàn bộ dự án. Khi phát triển tính năng mới hoặc refactor, Cursor và Developer bắt buộc phải tuân thủ nghiêm ngặt cấu trúc này.

---

## 1. Cấu trúc thư mục tổng quan (Monorepo / Multi-folder)

```text
📂 dự_án_của_bạn/
├── 📂 agents/          # Hệ thống AI Agents (Python / Agentic System)
├── 📂 backend/         # API Service & Nghiệp vụ (FastAPI / Python)
├── 📂 frontend/        # Giao diện người dùng (Next.js / TypeScript)
├── .cursorrules        # Quy tắc cấu hình hệ thống dành cho Cursor
├── architecture.md     # File tài liệu này (Bản đồ kiến trúc)
└── todo.md             # Quản lý tiến độ dự án

## 2. Cấu trúc thư mục AI Agentic System

📂 agents/
├── 📂 config/          # Cấu hình Model LLMs, Prompt Templates, API Keys
├── 📂 memory/          # Xử lý bộ nhớ Agent (Short-term, Long-term, Vector DB)
├── 📂 tools/           # Các công cụ Agent có thể gọi (Function Calling)
│   ├── __init__.py
│   ├── web_search.py   # Ví dụ: Tool tìm kiếm web
│   └── db_queries.py   # Ví dụ: Tool truy vấn database hộ Agent
├── 📂 workflows/       # Định nghĩa luồng chạy (ReAct, Multi-Agent Collaboration)
│   ├── sales_agent.py  # Agent hỗ trợ bán hàng
│   └── chief_agent.py  # Agent điều phối hệ thống
├── main_agent.py       # Điểm khởi chạy (Entrypoint) của hệ thống Agent
└── requirements.txt    # Thư viện phụ thuộc riêng của Agent

## 3. Cấu trúc thư mục backend

📂 backend/
├── 📂 app/
│   ├── 📂 api/          # Lớp định tuyến API (Endpoints)
│   │   ├── 📂 v1/
│   │   │   ├── auth.py  # API Đăng nhập/Đăng ký
│   │   │   └── agent.py # API kích hoạt/theo dõi Agent
│   ├── 📂 core/         # Cấu hình hệ thống (Security, Config, Database connection)
│   ├── 📂 models/       # Database Models (SQLAlchemy / Tortoise-ORM)
│   ├── 📂 schemas/      # Pydantic Schemas (v2) để Validate dữ liệu đầu vào/đầu ra
│   ├── 📂 services/     # Tầng xử lý logic nghiệp vụ (Business Logic)
│   └── main.py          # Khởi tạo FastAPI App
├── .env.example
├── Dockerfile
└── requirements.txt

## 4. Cấu trúc thư mục frontend

📂 frontend/
├── 📂 src/
│   ├── 📂 app/               # Next.js App Router (Pages & Các Route)
│   │   ├── 📂 (auth)/        # Route group dành cho Đăng nhập/Đăng ký
│   │   ├── 📂 dashboard/     # Giao diện chính sau khi đăng nhập
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── 📂 components/        # Các thành phần giao diện tái sử dụng
│   │   ├── 📂 ui/            # UI Components cơ bản (Button, Input, Toast...)
│   │   └── 📂 agent-monitor/ # Giao diện theo dõi tiến trình chạy của Agent
│   ├── 📂 hooks/             # Custom React Hooks
│   ├── 📂 services/          # Các hàm fetch API (Kết nối sang FastAPI)
│   ├── 📂 store/             # Quản lý State toàn cục (Zustand)
│   └── 📂 types/             # Định nghĩa các Interface TypeScript
├── .env.local
├── package.json
└── tailwind.config.js