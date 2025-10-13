"""
BlockStreet 登录自动化脚本
实现完整的登录流程：获取nonce -> 签名 -> CF盾解密 -> 认证登录
"""

import requests
import json
import time
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple, List
from eth_account import Account
from eth_account.messages import encode_defunct
import re
from dotenv import load_dotenv

from ysecaptcha_api import YesCaptchaApi

# 加载环境变量
load_dotenv()


class BlockStreetLogin:
    """BlockStreet登录客户端"""
    
    def __init__(self, yescaptcha_api_key: Optional[str] = None, yescaptcha_id: Optional[str] = None):
        """
        初始化登录客户端
        
        Args:
            yescaptcha_api_key: YesCaptcha API密钥，如果不提供则从环境变量读取
        """
        # 从环境变量或参数获取配置
        self.yescaptcha_api_key = yescaptcha_api_key or os.getenv('YESCAPTCHA_API_KEY')
        self.yescaptcha_id = yescaptcha_id or os.getenv('YESCAPTCHA_ID')
        self.invite_code = '5TE4Ua'
        
        if not self.yescaptcha_api_key or not self.yescaptcha_id:
            raise ValueError("YesCaptcha API密钥和ID必须通过参数或环境变量提供")
        
        self.base_url = "https://api.blockstreet.money"
        self.website_url = "https://blockstreet.money"
        self.website_key = "0x4AAAAAABpfyUqunlqwRBYN"
        self.chain_id = 56
        
        # 初始化验证码API
        self.captcha_api = YesCaptchaApi(self.yescaptcha_api_key, self.yescaptcha_id)
        
        # 设置请求头
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "fingerprint": "8a0ab76f6fe77c1e82ee52150deb2e5e",
            "priority": "u=1, i",
            "sec-ch-ua": '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://blockstreet.money/"
        }
        
        # 设置日志
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """设置日志配置"""
        # 从环境变量获取日志级别
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, log_level, logging.INFO)
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('blockstreet_login.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_wallets(self, wallet_file: str = "wallet.txt") -> List[Tuple[str, str]]:
        """
        从文件加载钱包地址和私钥
        
        Args:
            wallet_file: 钱包文件路径
            
        Returns:
            钱包地址和私钥的元组列表
            
        Raises:
            FileNotFoundError: 钱包文件不存在
            ValueError: 钱包文件格式错误
        """
        try:
            with open(wallet_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            wallets = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                if ':' not in line:
                    raise ValueError(f"第{line_num}行格式错误，应为 address:private_key")
                    
                address, private_key = line.split(':', 1)
                address = address.strip()
                private_key = private_key.strip()
                
                # 验证地址格式
                if not address.startswith('0x') or len(address) != 42:
                    raise ValueError(f"第{line_num}行地址格式错误: {address}")
                    
                # 验证私钥格式
                if not private_key.startswith('0x') or len(private_key) != 66:
                    raise ValueError(f"第{line_num}行私钥格式错误")
                    
                wallets.append((address, private_key))
                
            self.logger.info(f"成功加载 {len(wallets)} 个钱包")
            return wallets
            
        except FileNotFoundError:
            self.logger.error(f"钱包文件 {wallet_file} 不存在")
            raise
        except Exception as e:
            self.logger.error(f"加载钱包文件失败: {e}")
            raise
            
    def get_sign_nonce(self) -> Tuple[str, Optional[str]]:
        """
        获取签名nonce和初始gfsessionid
        
        Returns:
            (nonce, gfsessionid)的元组
            
        Raises:
            requests.RequestException: 网络请求失败
            ValueError: 响应数据格式错误
        """
        try:
            self.logger.info("正在获取签名nonce...")
            
            url = f"{self.base_url}/api/account/signnonce"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"nonce响应数据: {data}")
            
            if data.get('code') != 0:
                raise ValueError(f"获取nonce失败: {data.get('message', '未知错误')}")
                
            nonce = data['data']['signnonce']
            self.logger.info(f"成功获取nonce: {nonce}")
            
            # 从响应头中提取gfsessionid
            gfsessionid = None
            set_cookie = response.headers.get('set-cookie', '')
            if set_cookie:
                # 使用正则表达式提取gfsessionid
                match = re.search(r'gfsessionid=([^;]+)', set_cookie)
                if match:
                    gfsessionid = match.group(1)
                    self.logger.info(f"从nonce响应中获取到gfsessionid: {gfsessionid}")
                else:
                    self.logger.warning("nonce响应中未找到gfsessionid")
            else:
                self.logger.warning("nonce响应中没有set-cookie头")
                
            return nonce, gfsessionid
            
        except requests.RequestException as e:
            self.logger.error(f"获取nonce网络请求失败: {e}")
            raise
        except (KeyError, ValueError) as e:
            self.logger.error(f"解析nonce响应失败: {e}")
            raise
            
    def build_sign_message(self, address: str, nonce: str) -> str:
        """
        构建签名消息
        
        Args:
            address: 钱包地址
            nonce: 签名nonce
            
        Returns:
            待签名的消息字符串
        """
        # 获取当前时间和过期时间
        now = datetime.now(timezone.utc)
        issued_at = now.isoformat().replace('+00:00', 'Z')
        expiration_time = (now + timedelta(minutes=2)).isoformat().replace('+00:00', 'Z')
        
        message = f"""blockstreet.money wants you to sign in with your Ethereum account:
{address}

Welcome to Block Street

URI: https://blockstreet.money
Version: 1
Chain ID: {self.chain_id}
Nonce: {nonce}
Issued At: {issued_at}
Expiration Time: {expiration_time}"""
        
        self.logger.info(f"构建签名消息完成")
        self.logger.debug(f"签名消息内容:\n{message}")
        
        return message, issued_at, expiration_time
        
    def sign_message(self, message: str, private_key: str) -> str:
        """
        使用私钥对消息进行签名
        
        Args:
            message: 待签名的消息
            private_key: 私钥
            
        Returns:
            签名结果
            
        Raises:
            ValueError: 私钥格式错误或签名失败
        """
        try:
            self.logger.info("正在对消息进行签名...")
            
            # 创建账户对象
            account = Account.from_key(private_key)
            
            # 编码消息
            encoded_message = encode_defunct(text=message)
            
            # 签名
            signed_message = account.sign_message(encoded_message)
            signature = signed_message.signature.hex()
            
            self.logger.info(f"消息签名完成: {signature}")
            return signature
            
        except Exception as e:
            self.logger.error(f"消息签名失败: {e}")
            raise ValueError(f"签名失败: {e}")
            
    def solve_cloudflare_turnstile(self) -> str:
        """
        解决Cloudflare Turnstile验证
        
        Returns:
            CF盾token
            
        Raises:
            Exception: CF盾解密失败
        """
        try:
            self.logger.info("正在创建CF盾解密任务...")
            
            # 创建CF盾任务
            task_id = self.captcha_api.create_cf_task(
                type="TurnstileTaskProxyless",
                websiteURL=self.website_url,
                websiteKey=self.website_key
            )
            
            self.logger.info(f"CF盾任务创建成功，任务ID: {task_id}")
            
            # 轮询获取结果
            max_attempts = 30  # 最多等待6分钟 (30 * 12秒)
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                self.logger.info(f"第{attempt}次查询CF盾结果...")
                
                time.sleep(12)  # 等待12秒
                
                result = self.captcha_api.get_task_result(task_id)
                if result:
                    self.logger.info(f"CF盾解密成功: {result[:50]}...")
                    return result
                    
                self.logger.info("CF盾任务还在处理中，继续等待...")
                
            raise Exception("CF盾解密超时，请检查任务状态")
            
        except Exception as e:
            self.logger.error(f"CF盾解密失败: {e}")
            raise
            
    def verify_signature(self, address: str, nonce: str, signature: str, 
                        issued_at: str, expiration_time: str, cf_token: str, 
                        gfsessionid: Optional[str] = None) -> Optional[str]:
        """
        验证签名并获取session token
        
        Args:
            address: 钱包地址
            nonce: 签名nonce
            signature: 签名结果
            issued_at: 签发时间
            expiration_time: 过期时间
            cf_token: CF盾token
            gfsessionid: 从nonce请求中获取的gfsessionid
            
        Returns:
            gfsessionid或None
            
        Raises:
            requests.RequestException: 网络请求失败
        """
        try:
            self.logger.info("正在验证签名...")
            
            url = f"{self.base_url}/api/account/signverify"
            
            # 准备请求头
            verify_headers = self.headers.copy()
            verify_headers.update({
                "content-type": "application/json",
                "cf-turnstile-response": cf_token
            })
            
            # 如果有gfsessionid，添加到cookie中
            if gfsessionid:
                verify_headers["cookie"] = f"gfsessionid={gfsessionid}"
                self.logger.info(f"在认证请求中使用gfsessionid: {gfsessionid}")
            
            if not signature.startswith('0x'):
                signature = f'0x{signature}'
            # 准备请求体
            payload = {
                "address": address,
                "nonce": nonce,
                "signature": signature,
                "chainId": self.chain_id,
                "issuedAt": issued_at,
                "expirationTime": expiration_time,
                "invite_code": self.invite_code
            }
            
            self.logger.debug(f"验证请求数据: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=verify_headers, 
                                   json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"验证响应数据: {data}")
            
            if data.get('code') != 0:
                self.logger.error(f"签名验证失败: {data.get('message', '未知错误')}")
                return None
                
            # 从响应头中提取gfsessionid（可能是更新的）
            set_cookie = response.headers.get('set-cookie', '')
            if set_cookie:
                # 使用正则表达式提取gfsessionid
                match = re.search(r'gfsessionid=([^;]+)', set_cookie)
                if match:
                    session_id = match.group(1)
                    self.logger.info(f"成功获取最终session ID: {session_id}")
                    return session_id
                    
            # 如果响应头中没有新的gfsessionid，返回原来的
            if gfsessionid:
                self.logger.info(f"使用原有的gfsessionid: {gfsessionid}")
                return gfsessionid
                
            self.logger.warning("响应中未找到gfsessionid")
            return None
            
        except requests.RequestException as e:
            self.logger.error(f"验证签名网络请求失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"验证签名失败: {e}")
            raise
            
    def save_successful_login(self, address: str, private_key: str, session_id: str, 
                             success_file: str = "successful_logins.txt") -> None:
        """
        保存成功登录的钱包信息
        
        Args:
            address: 钱包地址
            private_key: 私钥
            session_id: 会话ID
            success_file: 成功登录文件路径
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(success_file, 'a', encoding='utf-8') as f:
                f.write(f"{address}:{private_key}:{session_id}:{timestamp}\n")
            self.logger.info(f"成功登录信息已保存到 {success_file}")
        except Exception as e:
            self.logger.error(f"保存成功登录信息失败: {e}")
    
    def remove_wallet_from_file(self, address: str, wallet_file: str = "wallet.txt") -> None:
        """
        从钱包文件中删除已登录的钱包
        
        Args:
            address: 要删除的钱包地址
            wallet_file: 钱包文件路径
        """
        try:
            # 读取所有钱包
            with open(wallet_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤掉已登录的钱包
            remaining_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(':')
                    if len(parts) >= 2 and parts[0] != address:
                        remaining_lines.append(line)
            
            # 重写文件
            with open(wallet_file, 'w', encoding='utf-8') as f:
                for line in remaining_lines:
                    f.write(line + '\n')
            
            self.logger.info(f"已从 {wallet_file} 中删除钱包 {address}")
        except Exception as e:
            self.logger.error(f"删除钱包失败: {e}")
    
    def batch_login(self, wallet_file: str = "wallet.txt", 
                   success_file: str = "successful_logins.txt") -> Dict[str, str]:
        """
        批量登录所有钱包
        
        Args:
            wallet_file: 钱包文件路径
            success_file: 成功登录文件路径
            
        Returns:
            成功登录的钱包字典 {address: session_id}
        """
        successful_logins = {}
        
        try:
            # 加载钱包
            wallets = self.load_wallets(wallet_file)
            
            if not wallets:
                self.logger.warning("没有找到可用的钱包")
                return successful_logins
            
            self.logger.info(f"开始批量登录，共 {len(wallets)} 个钱包")
            
            for i, (address, private_key) in enumerate(wallets, 1):
                self.logger.info(f"正在登录第 {i}/{len(wallets)} 个钱包: {address}")
                
                try:
                    # 执行登录
                    session_id = self.login(address, private_key)
                    
                    if session_id:
                        # 登录成功
                        successful_logins[address] = session_id
                        self.logger.info(f"钱包 {address} 登录成功")
                        
                        # 保存成功登录信息
                        self.save_successful_login(address, private_key, session_id, success_file)
                        
                        # 从钱包文件中删除已登录的钱包
                        self.remove_wallet_from_file(address, wallet_file)
                        
                    else:
                        self.logger.error(f"钱包 {address} 登录失败")
                        
                except Exception as e:
                    self.logger.error(f"钱包 {address} 登录过程中发生错误: {e}")
                
                # 添加延迟避免请求过于频繁
                if i < len(wallets):
                    time.sleep(2)
            
            self.logger.info(f"批量登录完成，成功登录 {len(successful_logins)} 个钱包")
            return successful_logins
            
        except Exception as e:
            self.logger.error(f"批量登录过程中发生错误: {e}")
            return successful_logins
    
    def login(self, address: str, private_key: str) -> Optional[str]:
        """
        执行完整的登录流程
        
        Args:
            address: 钱包地址
            private_key: 私钥
            
        Returns:
            gfsessionid或None
        """
        try:
            self.logger.info(f"开始登录流程，钱包地址: {address}")
            
            # 1. 获取签名nonce和初始gfsessionid
            nonce, gfsessionid = self.get_sign_nonce()
            
            # 2. 构建签名消息
            message, issued_at, expiration_time = self.build_sign_message(address, nonce)
            
            # 3. 签名消息
            signature = self.sign_message(message, private_key)
            
            # 4. 解决CF盾
            cf_token = self.solve_cloudflare_turnstile()
            
            # 5. 验证签名，传入初始的gfsessionid
            session_id = self.verify_signature(
                address, nonce, signature, issued_at, expiration_time, cf_token, gfsessionid
            )
            
            if session_id:
                self.logger.info(f"登录成功！Session ID: {session_id}")
                return session_id
            else:
                self.logger.error("登录失败")
                return None
                
        except Exception as e:
            self.logger.error(f"登录过程中发生错误: {e}")
            return None


def main():
    """主函数 - 批量登录所有钱包"""
    try:
        # 初始化登录客户端（从环境变量读取配置）
        client = BlockStreetLogin()
        
        print("开始批量登录...")
        print("配置信息:")
        print(f"- YesCaptcha API Key: {client.yescaptcha_api_key[:10]}...")
        print(f"- 邀请码: {client.invite_code or '未设置'}")
        print("-" * 50)
        
        # 执行批量登录
        successful_logins = client.batch_login()
        
        if successful_logins:
            print(f"\n批量登录完成！")
            print(f"成功登录 {len(successful_logins)} 个钱包:")
            for address, session_id in successful_logins.items():
                print(f"  {address}: {session_id[:20]}...")
            print(f"\n详细信息已保存到 successful_logins.txt")
        else:
            print("\n没有钱包登录成功")
            
    except ValueError as e:
        print(f"配置错误: {e}")
        print("请检查 .env 文件中的配置或设置环境变量")
    except Exception as e:
        print(f"程序执行失败: {e}")


if __name__ == "__main__":
    main()