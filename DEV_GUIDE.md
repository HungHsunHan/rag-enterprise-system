# HR Chatbot 開發指南

## 第一階段完成狀態

✅ **已完成的基礎架構元件：**

### 前端 (Frontend)
- ✅ React + TypeScript + Vite 開發環境
- ✅ MUI 元件庫整合
- ✅ Zustand 狀態管理
- ✅ ESLint + Prettier 代碼規範
- ✅ 基礎路由結構 (`/admin/*`, `/chat`, `/login`)
- ✅ 基礎 UI 元件 (Layout, Header, Button, Input)
- ✅ 登入頁面 (管理員/員工)
- ✅ 管理員儀表板
- ✅ 員工聊天介面
- ✅ 公司管理頁面
- ✅ 知識庫管理頁面

### 後端 (Backend)
- ✅ FastAPI 專案結構
- ✅ SQLAlchemy + Alembic 數據庫管理
- ✅ PostgreSQL + PGVector 整合
- ✅ 基礎 API 路由結構
- ✅ 認證系統 (JWT)
- ✅ 多租戶數據模型
- ✅ Pytest 測試環境
- ✅ Docker Compose 開發環境

### 基礎設施
- ✅ Monorepo 結構
- ✅ Docker Compose 配置
- ✅ 開發環境設置腳本

## 快速開始

### 1. 環境要求

- Node.js >= 20.0.0
- Python >= 3.11
- Docker & Docker Compose
- Git

### 2. 設置開發環境

```bash
# 克隆項目
git clone <repository-url>
cd BMad-HR_chatbot

# 安裝依賴
npm install

# 啟動數據庫服務
docker-compose up -d

# 安裝後端依賴
cd apps/backend
pip install -r requirements.txt

# 運行數據庫遷移
# Note: 需要用指定的 Python 環境
C:/Users/hunghsun/AppData/Local/anaconda3/envs/py10/python.exe -m alembic upgrade head

# 回到項目根目錄
cd ../..

# 啟動開發服務器
npm run dev
```

### 3. 訪問應用

- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs

## 項目結構

```
hr-chatbot-system/
├── apps/
│   ├── frontend/           # React 前端應用
│   │   ├── src/
│   │   │   ├── api/        # API 服務
│   │   │   ├── components/ # UI 組件
│   │   │   ├── pages/      # 頁面組件
│   │   │   ├── store/      # Zustand 狀態管理
│   │   │   └── styles/     # 樣式和主題
│   │   └── package.json
│   │
│   └── backend/            # FastAPI 後端應用
│       ├── app/
│       │   ├── api/        # API 路由
│       │   ├── core/       # 核心配置
│       │   ├── db/         # 數據庫模型
│       │   ├── schemas/    # Pydantic 模型
│       │   └── services/   # 業務邏輯服務
│       ├── tests/          # 測試文件
│       └── pyproject.toml
│
├── docs/                   # 項目文檔
├── scripts/                # 項目腳本
├── docker-compose.yml      # 開發環境配置
└── package.json            # Monorepo 配置
```

## 開發命令

### 根目錄命令
```bash
npm run dev              # 同時啟動前後端
npm run build           # 構建前端
npm run test            # 運行所有測試
npm run lint            # 代碼檢查
npm run format          # 代碼格式化
```

### 前端命令
```bash
cd apps/frontend
npm run dev             # 啟動前端開發服務器
npm run build           # 構建生產版本
npm run test            # 運行測試
npm run lint            # ESLint 檢查
npm run format          # Prettier 格式化
```

### 後端命令
```bash
cd apps/backend
# 使用指定的 Python 環境
C:/Users/hunghsun/AppData/Local/anaconda3/envs/py10/python.exe -m uvicorn app.main:app --reload
C:/Users/hunghsun/AppData/Local/anaconda3/envs/py10/python.exe -m pytest
C:/Users/hunghsun/AppData/Local/anaconda3/envs/py10/python.exe -m alembic upgrade head
```

## 測試登入帳號

目前系統需要實際的數據庫數據才能登入。你需要：

1. 確保 PostgreSQL 運行中
2. 運行數據庫遷移
3. 手動插入測試數據，或者實現種子數據腳本

## 下一步開發

根據 IMPLEMENTATION_PLAN.md，接下來需要實現：

### 第一階段剩餘任務
1. **認證系統完善** - 實際的用戶認證邏輯
2. **基礎管理員功能** - 公司 CRUD 操作的後端邏輯

### 第二階段核心功能
1. **文件處理管線** - 文件上傳、解析、向量化
2. **RAG 問答引擎** - 向量搜索和 LLM 整合
3. **前後端整合** - 完整的端到端流程

## 技術決策和約定

- **前端狀態管理**: 使用 Zustand 而不是 Redux
- **UI 組件庫**: MUI (Material-UI)
- **數據庫**: PostgreSQL + PGVector 統一管理
- **認證**: JWT Token
- **多租戶**: 通過 `company_id` 進行數據隔離
- **代碼風格**: ESLint + Prettier (前端), Black + Ruff (後端)

## 注意事項

- 所有數據庫查詢必須包含 `company_id` 過濾條件
- 敏感信息不能寫入日誌
- API 錯誤必須通過自定義異常處理
- 使用倉儲模式進行數據庫訪問