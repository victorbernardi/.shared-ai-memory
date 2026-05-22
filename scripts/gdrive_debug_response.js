const { spawn } = require('child_process');

async function debugResponse() {
    console.log('--- Debugging MCP Response Format ---');
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
        console.log('RAW RESPONSE:', data.toString());
        const response = JSON.parse(data.toString());
        if (response.id === 1) sendRequest('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'debug', version: '1.0.0' } });
        else if (response.id === 2) sendRequest('tools/call', { name: 'create_folder', arguments: { name: '_STOUT_DEBUG_' } });
        else if (response.id === 3) {
            console.log('FULL RESULT FOR CREATE_FOLDER:', JSON.stringify(response.result, null, 2));
            sendRequest('tools/call', { name: 'delete_file', arguments: { fileId: 'just_cleaning_up' } });
            server.kill();
            process.exit(0);
        }
    });

    setTimeout(() => sendRequest('tools/list'), 2000);
}
debugResponse();
