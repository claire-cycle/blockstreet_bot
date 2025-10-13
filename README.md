# BlockStreet 自动登录工具

这是一个用于自动化 BlockStreet 平台登录的 Python 工具，支持批量登录和环境变量配置。

## 功能特性

- 🔐 自动获取签名 nonce 和初始 gfsessionid
- ✍️ EVM 钱包消息签名
- 🛡️ Cloudflare Turnstile 验证码自动解决
- 🔑 自动获取用户 session token
- 📦 批量登录所有钱包
- 🗑️ 自动删除已登录的钱包
- 💾 保存成功登录的钱包信息
- 🌍 环境变量配置支持
- 📝 完整的日志记录
- 🚨 异常处理和错误恢复
- 📊 类型标注支持

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 环境变量配置

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

在 `.env` 文件中配置：

```env
# YesCaptcha API 配置
YESCAPTCHA_API_KEY=your_yescaptcha_api_key_here

# BlockStreet 邀请码（可选）
INVITE_CODE=

# 其他配置
REQUEST_TIMEOUT=30
CAPTCHA_TIMEOUT=120
LOG_LEVEL=INFO
```

### 2. 钱包配置

在 `wallet.txt` 文件中配置钱包地址和私钥，格式为：
```
钱包地址:私钥
```

示例：
```
0xa87B23899ab90748a9634536aD9e79B22C6aE4DC:0x5a9b1038bc0ec22ab91c76e5e4206743cbed052c10adbdb6d9a758a84424bae6
0xb98C34900cb91749b8745536bE0e80C33D7bF5ED:0x6b0c2049cd1fd33bc92d87f6f6f5e5317854163d21beecdb7e9b869b95535cf7
```

## 使用方法

1. 配置 `.env` 文件
2. 配置钱包文件 `wallet.txt`
3. 运行脚本：

```bash
python blockstreet_login.py
```

## 登录流程

1. **获取签名 nonce**: 从 BlockStreet API 获取用于签名的随机数，同时获取初始 gfsessionid
2. **构建签名消息**: 根据 EIP-4361 标准构建待签名消息
3. **EVM 钱包签名**: 使用私钥对消息进行签名
4. **CF 盾验证**: 自动解决 Cloudflare Turnstile 验证码
5. **认证登录**: 提交签名和验证码，使用初始 gfsessionid 进行认证
6. **批量处理**: 自动遍历所有钱包进行登录

## 批量登录特性

- **自动遍历**: 自动读取 `wallet.txt` 中的所有钱包
- **成功删除**: 登录成功的钱包会从 `wallet.txt` 中自动删除
- **信息保存**: 成功登录的钱包信息保存到 `successful_logins.txt`
- **错误处理**: 单个钱包登录失败不会影响其他钱包
- **请求限制**: 自动添加延迟避免请求过于频繁

## 输出文件

- `blockstreet_login.log`: 详细的运行日志
- `successful_logins.txt`: 成功登录的钱包信息
  - 格式：`地址:私钥:session_id:登录时间`

## 更新说明

- **v2.0**: 
  - 新增批量登录功能
  - 支持环境变量配置
  - 自动删除已登录钱包
  - 保存成功登录信息
- **v1.1**: 修复了登录流程，现在会在获取 nonce 时提取 gfsessionid，并在认证签名时使用该 cookie

## 注意事项

- 请确保 YesCaptcha API 密钥有效且有足够余额
- 钱包私钥请妥善保管，不要泄露给他人
- 建议在测试环境中先验证工具的正确性
- 登录过程中请保持网络连接稳定
- 如遇到验证码解决失败，请检查 YesCaptcha 服务状态

## 错误处理

工具包含完善的错误处理机制：

- 网络请求超时自动重试
- 验证码解决失败会记录详细错误信息
- 签名验证失败会输出具体错误原因
- 所有异常都会记录到日志文件中

## 依赖项

- `requests`: HTTP 请求库
- `eth_account`: 以太坊账户管理
- `python-dotenv`: 环境变量管理

详细依赖版本请查看 `requirements.txt` 文件。

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

### 如何贡献

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 开发环境设置

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-username/blockstreet-login-tool.git
   cd blockstreet-login-tool
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 复制配置文件：
   ```bash
   cp .env.example .env
   ```

4. 配置你的环境变量并开始开发

## 免责声明

本工具仅供学习和研究使用，请遵守相关平台的使用条款和法律法规。使用本工具产生的任何后果由使用者自行承担。

## 支持

如果这个项目对你有帮助，请给它一个 ⭐️！

如果你遇到任何问题，请在 [Issues](https://github.com/your-username/blockstreet-login-tool/issues) 中提出。