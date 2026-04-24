module.exports = {
    apps: [{
        name: 'shakti-api',
        cwd: '/var/www/ikshan/backend',
        script: 'venv/bin/uvicorn',
        args: 'main:app --host 0.0.0.0 --port 8000',
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: '1G',
        env: {
            NODE_ENV: 'production',
        },
        error_file: '/var/log/pm2/shakti-api-error.log',
        out_file: '/var/log/pm2/shakti-api-out.log',
        log_file: '/var/log/pm2/shakti-api-combined.log',
        time: true
    }]
};
