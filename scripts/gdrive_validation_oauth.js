const { spawn } = require('child_process');

async function runValidationOAuth() {
    console.log('--- Iniciando Validação Google Drive (FORÇANDO OAUTH) ---');
    
    // Deletamos a variável de Service Account para forçar o uso do OAuth
    const env = Object.assign({}, process.env);
    delete env.GOOGLE_APPLICATION_CREDENTIALS;
    env.GOOGLE_DRIVE_OAUTH_CREDENTIALS = 'C:\\Users\\victor.bernardi\\.credentials\\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json';

    const server = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], {
        shell: true, env: env, stdio: ['pipe', 'pipe', 'inherit']
    });

    let requestId = 1;
    let folderId, fileId, archiveId;

    function sendRequest(method, params = {}) {
        server.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: requestId++, method, params }) + '\n');
    }

    server.stdout.on('data', async (data) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const response = JSON.parse(line);
                if (response.id === 1) {
                    sendRequest('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'validator', version: '1.0.0' } });
                } else if (response.result && response.id === 2) {
                    console.log('[STEP] listFolder...');
                    sendRequest('tools/call', { name: 'listFolder', arguments: { folderId: 'root' } });
                } else if (response.result && response.id === 3) {
                    if (response.result.isError) throw new Error(response.result.content[0].text);
                    console.log('[STEP] createFolder...');
                    sendRequest('tools/call', { name: 'createFolder', arguments: { name: '_STOUT_VAL_OAUTH_' } });
                } else if (response.result && response.id === 4) {
                    if (response.result.isError) throw new Error(response.result.content[0].text);
                    folderId = response.result.content[0].text.match(/ID: ([a-zA-Z0-9_-]+)/i)?.[1];
                    console.log(`[STEP] createTextFile in ${folderId}...`);
                    sendRequest('tools/call', { name: 'createTextFile', arguments: { name: 'val_oauth.txt', content: 'STOUT OAUTH OK', parentFolderId: folderId } });
                } else if (response.result && response.id === 5) {
                    if (response.result.isError) throw new Error(response.result.content[0].text);
                    console.log(`[STEP] deleteItem ${folderId}...`);
                    sendRequest('tools/call', { name: 'deleteItem', arguments: { itemId: folderId } });
                } else if (response.result && response.id === 6) {
                    console.log(`[SUCCESS] OAuth Validation Passed!`);
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {
                console.error('[FATAL ERROR]', e.message);
                server.kill();
                process.exit(1);
            }
        }
    });

    setTimeout(() => sendRequest('tools/list'), 2000);
}
runValidationOAuth();
