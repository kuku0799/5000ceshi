#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler
from config import (
    WANGLUO_DIR,
    LOG_FILE,
    WEB_PORT,
    SECRET_KEY,
    BASIC_AUTH_ENABLED,
    BASIC_AUTH_USER,
    BASIC_AUTH_PASS,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
)
from ruamel.yaml import YAML
from jx import parse_nodes
from zw import inject_proxies
from zc import inject_groups

app = Flask(__name__)
app.secret_key = SECRET_KEY

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
rotating = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
rotating.setLevel(logging.INFO)
rotating.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(rotating)
root_logger.addHandler(logging.StreamHandler())


def _check_basic_auth(req) -> bool:
    if not BASIC_AUTH_ENABLED:
        return True
    auth = req.authorization
    return bool(auth and auth.username == BASIC_AUTH_USER and auth.password == BASIC_AUTH_PASS)


def _get_openclash_config_path() -> str:
    try:
        path = os.popen("uci get openclash.config.config_path").read().strip()
        if path:
            return path
    except Exception:
        pass
    from config import OPENCLASH_CONFIG_PATH
    return OPENCLASH_CONFIG_PATH

def get_file_list():
    """获取wangluo目录下的文件列表"""
    try:
        if not os.path.exists(WANGLUO_DIR):
            os.makedirs(WANGLUO_DIR, exist_ok=True)
        
        files = []
        for filename in os.listdir(WANGLUO_DIR):
            filepath = os.path.join(WANGLUO_DIR, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        return files
    except Exception as e:
        logging.error(f"获取文件列表失败: {e}")
        return []

def read_status():
    """读取同步状态"""
    try:
        from config import STATUS_FILE
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"读取状态失败: {e}")
    return {"success": None}


def _verify_with_openclash(tmp_yaml_path: str) -> bool:
    # 如果没有 openclash 脚本，直接返回 True 表示语法层面 OK
    if not os.path.exists("/etc/init.d/openclash"):
        return True
    rc = os.system(f"/etc/init.d/openclash verify_config {tmp_yaml_path} > /dev/null 2>&1")
    return rc == 0


def perform_verify():
    result = {
        'parsed_total': 0,
        'injected': 0,
        'invalid': 0,
        'duplicate': 0,
        'verify_pass': None,
        'message': ''
    }
    try:
        nodes_file = os.path.join(WANGLUO_DIR, 'nodes.txt')
        nodes = parse_nodes(nodes_file)
        result['parsed_total'] = len(nodes)
        if not nodes:
            result['verify_pass'] = False
            result['message'] = '未解析到有效节点'
            return result

        yaml = YAML()
        yaml.preserve_quotes = True
        config_path = _get_openclash_config_path()
        if not os.path.exists(config_path):
            # 仅进行解析层验证
            result['verify_pass'] = True
            result['message'] = '仅完成解析验证（未检测到 OpenClash 配置文件）'
            return result

        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = yaml.load(f)
        updated, injected, invalid, duplicate = inject_proxies(cfg, nodes)
        inject_groups(updated, [n.get('name') for n in nodes])
        result['injected'] = injected
        result['invalid'] = invalid
        result['duplicate'] = duplicate

        tmp_path = '/tmp/verify_web_editor.yaml'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(updated, f)

        result['verify_pass'] = _verify_with_openclash(tmp_path)
        result['message'] = 'ok' if result['verify_pass'] else 'openclash verify failed'
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return result
    except Exception as e:
        result['verify_pass'] = False
        result['message'] = str(e)
        return result

def read_file_content(filename):
    """读取文件内容"""
    try:
        filepath = os.path.join(WANGLUO_DIR, secure_filename(filename))
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"读取文件失败 {filename}: {e}")
        return None

def write_file_content(filename, content):
    """写入文件内容"""
    try:
        filepath = os.path.join(WANGLUO_DIR, secure_filename(filename))
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"文件保存成功: {filename}")
        return True
    except Exception as e:
        logging.error(f"保存文件失败 {filename}: {e}")
        return False

@app.route('/')
def index():
    """主页面"""
    if not _check_basic_auth(request):
        return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Wangluo"'})
    files = get_file_list()
    return render_template('index.html', files=files)

@app.route('/api/files')
def api_files():
    """API: 获取文件列表"""
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    files = get_file_list()
    return jsonify({'success': True, 'files': files})

@app.route('/api/status')
def api_status():
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    return jsonify({'success': True, 'status': read_status()})

@app.route('/api/file/<filename>')
def api_read_file(filename):
    """API: 读取文件内容"""
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    content = read_file_content(filename)
    if content is not None:
        return jsonify({'success': True, 'content': content})
    else:
        return jsonify({'success': False, 'error': '文件不存在或读取失败'})

@app.route('/api/file/<filename>', methods=['POST'])
def api_write_file(filename):
    """API: 写入文件内容"""
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if write_file_content(filename, content):
            return jsonify({'success': True, 'message': '文件保存成功'})
        else:
            return jsonify({'success': False, 'error': '文件保存失败'})
    except Exception as e:
        logging.error(f"API写入文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/<filename>', methods=['DELETE'])
def api_delete_file(filename):
    """API: 删除文件"""
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        filepath = os.path.join(WANGLUO_DIR, secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"文件删除成功: {filename}")
            return jsonify({'success': True, 'message': '文件删除成功'})
        else:
            return jsonify({'success': False, 'error': '文件不存在'})
    except Exception as e:
        logging.error(f"删除文件失败 {filename}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file', methods=['POST'])
def api_create_file():
    """API: 创建新文件"""
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        
        if not filename:
            return jsonify({'success': False, 'error': '文件名不能为空'})
        
        filename = secure_filename(filename)
        filepath = os.path.join(WANGLUO_DIR, filename)
        
        if os.path.exists(filepath):
            return jsonify({'success': False, 'error': '文件已存在'})
        
        # 创建空文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('')
        
        logging.info(f"文件创建成功: {filename}")
        return jsonify({'success': True, 'message': '文件创建成功'})
    except Exception as e:
        logging.error(f"创建文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/verify', methods=['POST'])
def api_verify():
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    res = perform_verify()
    return jsonify({'success': True, 'result': res})

@app.route('/api/sync', methods=['POST'])
def api_sync():
    if not _check_basic_auth(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        import subprocess, sys
        here = os.path.dirname(os.path.abspath(__file__))
        zr_path = os.path.join(here, 'zr.py')
        if not os.path.exists(zr_path):
            return jsonify({'success': False, 'error': '缺少 zr.py 脚本'}), 500
        proc = subprocess.run([sys.executable, zr_path], capture_output=True, text=True)
        ok = (proc.returncode == 0)
        return jsonify({'success': ok, 'code': proc.returncode, 'stdout': proc.stdout[-2000:], 'stderr': proc.stderr[-2000:]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs(WANGLUO_DIR, exist_ok=True)
    
    # 创建templates目录
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    print(f"Web编辑器启动中...")
    print(f"访问地址: http://localhost:{WEB_PORT}")
    print(f"文件目录: {WANGLUO_DIR}")
    
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False)