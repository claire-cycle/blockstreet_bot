"""
BlockStreet 登录工具使用示例
"""

from blockstreet_login import BlockStreetLogin


def example_single_wallet_login():
    """单个钱包登录示例"""
    # 配置 YesCaptcha 参数
    YESCAPTCHA_API_KEY = "your_yescaptcha_api_key_here"
    YESCAPTCHA_ID = "your_yescaptcha_id_here"
    
    # 初始化登录客户端
    client = BlockStreetLogin(YESCAPTCHA_API_KEY, YESCAPTCHA_ID)
    
    # 手动指定钱包信息
    address = "0xa87B23899ab90748a9634536aD9e79B22C6aE4DC"
    private_key = "0x5a9b1038bc0ec22ab91c76e5e4206743cbed052c10adbdb6d9a758a84424bae6"
    
    # 执行登录
    session_id = client.login(address, private_key)
    
    if session_id:
        print(f"登录成功！Session ID: {session_id}")
        return session_id
    else:
        print("登录失败")
        return None


def example_batch_wallet_login():
    """批量钱包登录示例"""
    # 配置 YesCaptcha 参数
    YESCAPTCHA_API_KEY = "your_yescaptcha_api_key_here"
    YESCAPTCHA_ID = "your_yescaptcha_id_here"
    
    # 初始化登录客户端
    client = BlockStreetLogin(YESCAPTCHA_API_KEY, YESCAPTCHA_ID)
    
    try:
        # 加载所有钱包
        wallets = client.load_wallets("wallet.txt")
        
        successful_logins = []
        failed_logins = []
        
        for i, (address, private_key) in enumerate(wallets, 1):
            print(f"\n正在处理第 {i}/{len(wallets)} 个钱包: {address}")
            
            # 执行登录
            session_id = client.login(address, private_key)
            
            if session_id:
                successful_logins.append((address, session_id))
                print(f"✅ 钱包 {address} 登录成功")
            else:
                failed_logins.append(address)
                print(f"❌ 钱包 {address} 登录失败")
                
        # 输出统计结果
        print(f"\n=== 登录统计 ===")
        print(f"总钱包数: {len(wallets)}")
        print(f"成功登录: {len(successful_logins)}")
        print(f"登录失败: {len(failed_logins)}")
        
        # 保存成功的 session
        if successful_logins:
            with open('batch_sessions.txt', 'w', encoding='utf-8') as f:
                for address, session_id in successful_logins:
                    f.write(f"{address}:{session_id}\n")
            print(f"成功的 session 已保存到 batch_sessions.txt")
            
        return successful_logins
        
    except Exception as e:
        print(f"批量登录过程中发生错误: {e}")
        return []


def example_with_custom_config():
    """自定义配置示例"""
    # 配置 YesCaptcha 参数
    YESCAPTCHA_API_KEY = "your_yescaptcha_api_key_here"
    YESCAPTCHA_ID = "your_yescaptcha_id_here"
    
    # 初始化登录客户端
    client = BlockStreetLogin(YESCAPTCHA_API_KEY, YESCAPTCHA_ID)
    
    # 可以修改一些配置
    client.invite_code = "your_invite_code"  # 修改邀请码
    
    # 加载钱包并登录
    wallets = client.load_wallets()
    if wallets:
        address, private_key = wallets[0]
        session_id = client.login(address, private_key)
        return session_id
    
    return None


if __name__ == "__main__":
    print("BlockStreet 登录工具使用示例")
    print("请先配置 YesCaptcha API 密钥和 ID")
    
    # 选择运行哪个示例
    choice = input("\n选择示例:\n1. 单个钱包登录\n2. 批量钱包登录\n3. 自定义配置登录\n请输入选择 (1-3): ")
    
    if choice == "1":
        example_single_wallet_login()
    elif choice == "2":
        example_batch_wallet_login()
    elif choice == "3":
        example_with_custom_config()
    else:
        print("无效选择")