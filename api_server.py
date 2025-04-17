from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Optional, List, Dict
from custom_policy_manager import CustomPolicyManager
from config import WAF_CONFIGS, API_CONFIG
import asyncio
import logging
import os
from datetime import datetime


# 配置日志
log_dir = os.path.dirname(API_CONFIG["log_file"])
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(API_CONFIG["log_file"]),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url=None,          # 禁用 Swagger UI
    redoc_url=None,         # 禁用 ReDoc
    openapi_url=None,       # 禁用 OpenAPI
    swagger_ui_oauth2_redirect_url=None,  # 禁用 OAuth2 重定向
)

async def verify_token(token: Optional[str] = Header(None)):
    """验证token是否有效"""
    if not token or token not in API_CONFIG["tokens"]:
        logger.warning(f"无效的token尝试: {token}")
        raise HTTPException(status_code=401, detail="无效的token")
    logger.info("API访问使用了有效的token")
    return token

def get_waf_instances(waf_name: str) -> List[dict]:
    """获取指定WAF名称的所有实例"""
    if waf_name not in WAF_CONFIGS:
        logger.warning(f"未找到WAF配置: {waf_name}")
        return []
    return WAF_CONFIGS[waf_name]

@app.post('/api/chaos/enable/{waf_name}')
async def enable_chaos(waf_name: str, token: str = Depends(verify_token)):
    """启用指定WAF的混沌工程功能"""
    try:
        # 获取WAF实例
        waf_instances = get_waf_instances(waf_name)
        if not waf_instances:
            logger.error(f"未找到WAF: {waf_name}")
            raise HTTPException(status_code=404, detail=f'未找到WAF: {waf_name}')

        results = []
        for instance in waf_instances:
            try:
                manager = CustomPolicyManager()
                manager.base_url = instance["base_url"]
                manager.headers["X-SLCE-API-TOKEN"] = instance["api_token"]
                
                for site_id in instance["id"]:
                    try:
                        result = manager.configure_chaos(
                            site_id=site_id,
                            html_encryption=True,
                            html_fast_decryption=False,
                            img_encryption=False,
                            is_enabled=True,
                            js_encryption=False,
                            img_text="",
                            js_path=[]
                        )
                        results.append({
                            "waf_name": waf_name,
                            "instance": instance["name"],
                            "site_id": site_id,
                            "result": result
                        })
                        logger.info(f"启用混沌工程成功 - WAF: {waf_name}/{instance['name']}, site_id: {site_id}")
                    except Exception as e:
                        logger.error(f"启用混沌工程失败 - WAF: {waf_name}/{instance['name']}, site_id: {site_id}, error: {str(e)}")
                        results.append({
                            "waf_name": waf_name,
                            "instance": instance["name"],
                            "site_id": site_id,
                            "error": str(e)
                        })
            except Exception as e:
                logger.error(f"处理WAF实例失败 - WAF: {waf_name}/{instance['name']}: {str(e)}")
                results.append({
                    "waf_name": waf_name,
                    "instance": instance["name"],
                    "error": str(e)
                })

        return {"results": results}
        
    except Exception as e:
        logger.error(f"启用混沌工程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/chaos/disable/{waf_name}')
async def disable_chaos(waf_name: str, token: str = Depends(verify_token)):
    """禁用指定WAF的混沌工程功能"""
    try:
        # 获取WAF实例
        waf_instances = get_waf_instances(waf_name)
        if not waf_instances:
            logger.error(f"未找到WAF: {waf_name}")
            raise HTTPException(status_code=404, detail=f'未找到WAF: {waf_name}')

        results = []
        for instance in waf_instances:
            try:
                manager = CustomPolicyManager()
                manager.base_url = instance["base_url"]
                manager.headers["X-SLCE-API-TOKEN"] = instance["api_token"]
                
                for site_id in instance["id"]:
                    try:
                        result = manager.configure_chaos(
                            site_id=site_id,
                            html_encryption=False,
                            html_fast_decryption=False,
                            img_encryption=False,
                            is_enabled=False,
                            js_encryption=False,
                            img_text="",
                            js_path=[]
                        )
                        results.append({
                            "waf_name": waf_name,
                            "instance": instance["name"],
                            "site_id": site_id,
                            "result": result
                        })
                        logger.info(f"禁用混沌工程成功 - WAF: {waf_name}/{instance['name']}, site_id: {site_id}")
                    except Exception as e:
                        logger.error(f"禁用混沌工程失败 - WAF: {waf_name}/{instance['name']}, site_id: {site_id}, error: {str(e)}")
                        results.append({
                            "waf_name": waf_name,
                            "instance": instance["name"],
                            "site_id": site_id,
                            "error": str(e)
                        })
            except Exception as e:
                logger.error(f"处理WAF实例失败 - WAF: {waf_name}/{instance['name']}: {str(e)}")
                results.append({
                    "waf_name": waf_name,
                    "instance": instance["name"],
                    "error": str(e)
                })

        return {"results": results}
        
    except Exception as e:
        logger.error(f"禁用混沌工程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logging.info("Starting WAF API server")
    import uvicorn
    uvicorn.run(
        app,
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        log_level="info",
        reload=False,
        workers=1,
        loop="asyncio",  # 使用默认的 asyncio 而不是 uvloop
        http="h11"      # 使用 h11 而不是 httptools
    )