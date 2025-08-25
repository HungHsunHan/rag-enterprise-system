# Docker 版本預設帳號

當您使用 Docker 部署此 RAG Enterprise System 時，系統會自動創建以下預設帳號供測試使用。

## 🌐 訪問地址
- **前端應用**: http://localhost:4000
- **後端 API**: http://localhost:9000
- **API 文檔**: http://localhost:9000/docs

## 👤 預設帳號

### 🔐 管理員帳號
- **Email**: `admin@dev.com`  
- **密碼**: `admin123`
- **權限**: 完整系統管理權限
  - 管理所有公司和用戶
  - 上傳和管理知識文檔
  - 查看系統統計和反饋
  - 配置 AI 模型

### 👥 測試員工帳號

#### Acme Corp 公司
- **員工ID**: `BRIAN001` (Brian Zhang)
- **員工ID**: `TONY001` (Tony Chen)

#### Tech Innovations Inc 公司  
- **員工ID**: `LISA001` (Lisa Wang)
- **員工ID**: `DEV001` (Developer User)

> **注意**: 員工登錄只需輸入員工ID，無需密碼

## 🚀 登錄步驟

### 管理員登錄
1. 打開 http://localhost:4000
2. 選擇 "Admin Login"
3. 輸入 Email: `admin@dev.com`
4. 輸入密碼: `admin123`
5. 點擊登錄

### 員工登錄
1. 打開 http://localhost:4000  
2. 選擇 "Employee Login"
3. 輸入員工ID (例如: `BRIAN001`)
4. 點擊登錄

## ⚠️ 生產環境注意事項

**重要**: 這些是開發/測試用的預設帳號。在生產環境部署時：

1. **更改管理員密碼**:
   ```sql
   UPDATE admins SET password_hash = '新的bcrypt哈希值' WHERE email = 'admin@dev.com';
   ```

2. **創建新的管理員帳號並刪除預設帳號**:
   ```sql
   -- 創建新管理員
   INSERT INTO admins (id, email, password_hash) VALUES (uuid_generate_v4(), 'your-admin@company.com', '您的bcrypt哈希');
   -- 刪除預設管理員
   DELETE FROM admins WHERE email = 'admin@dev.com';
   ```

3. **刪除測試員工帳號**:
   ```sql
   DELETE FROM users WHERE employee_id IN ('BRIAN001', 'TONY001', 'LISA001', 'DEV001');
   ```

4. **創建真實的公司和員工資料**

## 🔒 安全最佳實踐

- 在生產環境中務必更改所有預設密碼
- 使用強密碼和安全的 JWT 密鑰
- 定期備份資料庫
- 監控系統訪問日誌
- 限制管理員帳號數量