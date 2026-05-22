const { spawn } = require('child_process');

async function listToolsNames() {
    const env = Object.assign({}, process.env, {
        GOOGLE_DRIVE_OAUTH_CREDENTIALS: 'C:\\Users\\victor.bernardi\\.credentials\\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json'
    });
    const server = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], {
        shell: true, env: env, stdio: ['pipe', 'pipe', 'inherit']
    });

    let requestId = 1;
    function sendRequest(method, params = {}) {
        server.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: requestId++, method, params }) + '\n');
    }

    server.stdout.on('data', (data) => {
        try {
            const response = JSON.parse(data.toString());
            if (response.id === 1) {
                console.log('TOOL NAMES:', response.result.tools.map(t => t.name).join(', '));
                server.kill();
                process.exit(0);
            }
        } catch (e) {}
    });

    setTimeout(() => sendRequest('tools/list'), 2000);
}
listToolsNames();
