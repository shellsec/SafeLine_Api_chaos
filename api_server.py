from flask import Flask, request, jsonify
from custom_policy_manager import CustomPolicyManager
from config import WAF_CONFIGS, API_CONFIG
import logging
import os

# 配置日志
log_dir = os.path.dirname(API_CONFIG["log_file"])
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=API_CONFIG["log_file"],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def verify_token(token):
    """验证token是否有效"""
    return token in API_CONFIG["tokens"]

def get_waf_instances(waf_name):
    """获取指定WAF名称的所有实例"""
    if waf_name not in WAF_CONFIGS:
        return []
    return WAF_CONFIGS[waf_name]

@app.route('/api/chaos/enable/<waf_name>', methods=['POST'])
def enable_chaos(waf_name):
    """启用指定WAF的混沌工程功能"""
    try:
        # 验证token
        token = request.headers.get('token')
        if not token or not verify_token(token):
            return jsonify({'error': '无效的token'}), 401

        # 获取WAF实例
        waf_instances = get_waf_instances(waf_name)
        if not waf_instances:
            return jsonify({'error': f'未找到WAF: {waf_name}'}), 404

        results = []
        for instance in waf_instances:
            try:
                manager = CustomPolicyManager(instance)
                for site_id in instance["id"]:
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
                logger.error(f"启用混沌工程失败 - WAF: {waf_name}/{instance['name']}: {str(e)}")
                results.append({
                    "waf_name": waf_name,
                    "instance": instance["name"],
                    "error": str(e)
                })

        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"启用混沌工程失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chaos/disable/<waf_name>', methods=['POST'])
def disable_chaos(waf_name):
    """禁用指定WAF的混沌工程功能"""
    try:
        # 验证token
        token = request.headers.get('token')
        if not token or not verify_token(token):
            return jsonify({'error': '无效的token'}), 401

        # 获取WAF实例
        waf_instances = get_waf_instances(waf_name)
        if not waf_instances:
            return jsonify({'error': f'未找到WAF: {waf_name}'}), 404

        results = []
        for instance in waf_instances:
            try:
                manager = CustomPolicyManager(instance)
                for site_id in instance["id"]:
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
                logger.error(f"禁用混沌工程失败 - WAF: {waf_name}/{instance['name']}: {str(e)}")
                results.append({
                    "waf_name": waf_name,
                    "instance": instance["name"],
                    "error": str(e)
                })

        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"禁用混沌工程失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=False
    )