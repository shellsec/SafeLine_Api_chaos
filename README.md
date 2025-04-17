# SafeLine_Api_chaos
一个用于管理SafeLine WAF策略的FastAPI接口服务,SafeLine_Api_chaos，HTML动态加密，JS 动态混淆，图片动态水印
=======
# SafeLine WAF API

一个用于管理SafeLine WAF策略的FastAPI接口服务。

## 功能特点

- 支持多雷池WAF实例管理
- 提供策略启用/禁用接口
- 完整的日志记录
- Token认证保护

## 安装要求

- Python 3.8+
- FastAPI
- uvicorn

## 应用场景
1、custom_policy_manager.py - 自定义策略管理
2、api_server.py - API服务

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置WAF实例
编辑`config.py`文件，配置WAF实例信息：
```python
# WAF API配置，支持多个链接
# WAF API配置
WAF_CONFIGS = {
    "office": [
        {
            "name": "waf1_instance1",
            "base_url": "https://192.168.1.1:9443/api",
            "api_token": "api_token",
            "id": [1]
        },
        {
            "name": "waf1_instance2",
            "base_url": "https://192.168.1.1:9443/api",
            "api_token": "api_token",
            "id": [2]
        }
    ]
}
```

3. 启动服务
```bash
python api_server.py
```

## API接口

启用

curl -k -X POST -H "token: api-token" http://192.168.1.2:8000/api/chaos/enable/office



关闭

curl -k -X POST -H "token: api-token" http://192.168.1.2:8000/api/chaos/disable/office


## 配置说明

### API配置
在`config.py`中配置API服务参数：
```python
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 7000,
    "tokens": ["your-api-token"],
    "log_file": "logs/waf_api.log"
}
```

## 日志
服务日志默认保存在`logs/waf_api.log`文件中。

## 贡献
欢迎提交Issue和Pull Request。

## 许可证
本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。
