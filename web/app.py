import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from plugin.config import ConfigManager

app = Flask(__name__)
app.secret_key = os.environ.get('WECHAT_REPLY_DELEGATION_SECRET_KEY', 'hermes-wechat-reply-delegation-secret-key')
CORS(app)

app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

LANGUAGES = {
    'zh': '中文',
    'en': 'English'
}

def get_locale():
    return session.get('language', 'zh')

config_manager = ConfigManager()

VALID_USERS = {
    "admin": "password123"
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in VALID_USERS and VALID_USERS[username] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
    return redirect(request.referrer or url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/config')
@login_required
def get_config():
    config = config_manager.get_global_config()
    groups = config_manager.config.get('groups', {})
    return jsonify({
        'global': config,
        'groups': groups
    })

@app.route('/api/groups')
@login_required
def get_groups():
    groups = config_manager.config.get('groups', {})
    return jsonify(groups)

@app.route('/api/groups/<group_id>', methods=['GET'])
@login_required
def get_group(group_id):
    groups = config_manager.config.get('groups', {})
    group = groups.get(group_id)
    if group:
        return jsonify(group)
    return jsonify({'error': 'Group not found'}), 404

@app.route('/api/groups', methods=['POST'])
@login_required
def add_group():
    data = request.json
    group_id = data.get('group_id')
    if not group_id:
        return jsonify({'error': 'group_id is required'}), 400
    
    config = {
        'enabled': data.get('enabled', True),
        'display_name': data.get('display_name', group_id),
        'display_name_en': data.get('display_name_en', group_id),
        'schedule': data.get('schedule', {
            'enabled': False,
            'time_ranges': []
        }),
        'online_status': data.get('online_status', {
            'reply_when': 'offline_only'
        }),
        'triggers': data.get('triggers', {
            'at_mention': True,
            'keywords': [],
            'at_all': False
        }),
        'instructions': data.get('instructions', {
            'default': '您好，用户暂时不在，他看到消息后会尽快回复您。',
            'default_en': 'Hello, the user is unavailable. They will reply when they see your message.',
            'topic_responses': [],
            'compound': []
        })
    }
    
    config_manager.config['groups'][group_id] = config
    config_manager._save_config()
    return jsonify({'status': 'success', 'group_id': group_id})

@app.route('/api/groups/<group_id>', methods=['PUT'])
@login_required
def update_group(group_id):
    data = request.json
    groups = config_manager.config.get('groups', {})
    
    if group_id not in groups:
        return jsonify({'error': 'Group not found'}), 404
    
    groups[group_id].update(data)
    config_manager._save_config()
    return jsonify({'status': 'success'})

@app.route('/api/groups/<group_id>', methods=['DELETE'])
@login_required
def delete_group(group_id):
    groups = config_manager.config.get('groups', {})
    
    if group_id not in groups:
        return jsonify({'error': 'Group not found'}), 404
    
    del groups[group_id]
    config_manager._save_config()
    return jsonify({'status': 'success'})

@app.route('/api/reload', methods=['POST'])
@login_required
def reload_config():
    success = config_manager.reload()
    return jsonify({'status': 'success' if success else 'failed'})

@app.route('/api/global', methods=['PUT'])
@login_required
def update_global():
    data = request.json
    global_config = config_manager.get_global_config()
    global_config.update(data)
    
    for key in global_config:
        if key in config_manager.config:
            config_manager.config[key] = global_config[key]
    
    config_manager._save_config()
    return jsonify({'status': 'success'})

def run(host='0.0.0.0', port=5100):
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    run()