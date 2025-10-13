#!/usr/bin/env python3
"""
BlockStreet 批量登录示例
演示如何使用批量登录功能
"""

from blockstreet_login import BlockStreetLogin
import os

def main():
    """批量登录示例"""
    
    print("=== BlockStreet 批量登录示例 ===\n")
    
    # 检查环境变量配置
    if not os.getenv('YESCAPTCHA_API_KEY') or not os.getenv('YESCAPTCHA_ID'):
        print("❌ 错误：请先配置 .env 文件")
        print("请复制 .env.example 为 .env 并填入正确的配置")
        return
    
    try:
        # 初始化客户端
        client = BlockStreetLogin()
        
        print("✅ 配置检查通过")
        print(f"📋 YesCaptcha API Key: {client.yescaptcha_api_key[:10]}...")
        print(f"📋 YesCaptcha ID: {client.yescaptcha_id}")
        print(f"📋 邀请码: {client.invite_code or '未设置'}")
        print("-" * 50)
        
        # 检查钱包文件
        wallets = client.load_wallets()
        if not wallets:
            print("❌ 没有找到可用的钱包")
            print("请在 wallet.txt 中添加钱包地址和私钥")
            return
        
        print(f"📱 找到 {len(wallets)} 个钱包待登录")
        for i, (address, _) in enumerate(wallets, 1):
            print(f"  {i}. {address}")
        print("-" * 50)
        
        # 开始批量登录
        print("🚀 开始批量登录...")
        successful_logins = client.batch_login()
        
        # 显示结果
        print("\n" + "=" * 50)
        if successful_logins:
            print(f"✅ 批量登录完成！成功登录 {len(successful_logins)} 个钱包:")
            for address, session_id in successful_logins.items():
                print(f"  🔑 {address}: {session_id[:20]}...")
            print(f"\n📄 详细信息已保存到 successful_logins.txt")
        else:
            print("❌ 没有钱包登录成功")
        
        # 检查剩余钱包
        remaining_wallets = client.load_wallets()
        if remaining_wallets:
            print(f"\n⚠️  还有 {len(remaining_wallets)} 个钱包未成功登录")
        else:
            print(f"\n🎉 所有钱包都已成功登录！")
            
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")

if __name__ == "__main__":
    main()