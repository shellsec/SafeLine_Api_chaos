import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import WAF_CONFIGS, API_CONFIG

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 配置重试策略
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

class CustomPolicyManager:
    def __init__(self, waf_instance=None):
        self.waf_instance = waf_instance
        self.base_url = None
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # 创建Session并配置重试机制
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.verify = False

        if waf_instance:
            self.base_url = waf_instance["base_url"]
            self.headers["X-SLCE-API-TOKEN"] = waf_instance["api_token"]

    def configure_chaos(self, site_id, html_encryption=True, html_fast_decryption=False, 
                       img_encryption=False, is_enabled=True, js_encryption=False, 
                       img_text="", js_path=None):
        """配置站点的混沌工程功能
        
        Args:
            site_id: 站点ID
            html_encryption: 是否启用HTML加密
            html_fast_decryption: 是否启用HTML快速解密
            img_encryption: 是否启用图片加密
            is_enabled: 是否启用混沌工程
            js_encryption: 是否启用JS加密
            img_text: 图片文字
            js_path: JS路径列表
        """
        url = f"{self.base_url}/open/site/chaos"
        data = {
            "id": site_id,
            "html_encryption": html_encryption,
            "html_fast_decryption": html_fast_decryption,
            "img_encryption": img_encryption,
            "is_enabled": is_enabled,
            "js_encryption": js_encryption,
            "img_text": img_text,
            "js_path": js_path if js_path is not None else []
        }
        
        try:
            response = self.session.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            import logging
            logging.error(f"配置混沌工程失败 - site_id: {site_id}, error: {str(e)}")
            raise

if __name__ == "__main__":
    # 测试配置
    waf_instance = WAF_CONFIGS["office"][0]
    manager = CustomPolicyManager(waf_instance)
    
    # 测试启用混沌工程
    print("\n启用混沌工程：")
    enable_chaos = manager.configure_chaos(
        site_id=11,
        html_encryption=True,
        html_fast_decryption=False,
        img_encryption=False,
        is_enabled=True,
        js_encryption=False,
        img_text="",
        js_path=[]
    )
    print(json.dumps(enable_chaos, indent=2, ensure_ascii=False))

    # 测试关闭混沌工程
    print("\n关闭混沌工程：")
    disable_chaos = manager.configure_chaos(
        site_id=11,
        html_encryption=False,
        html_fast_decryption=False,
        img_encryption=False,
        is_enabled=False,
        js_encryption=False,
        img_text="",
        js_path=[]
    )
    print(json.dumps(disable_chaos, indent=2, ensure_ascii=False))



