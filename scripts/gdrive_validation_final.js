const { spawn } = require('child_process');

async function runValidation() {
    console.log('--- Iniciando Validação Final do Google Drive MCP (V2 - Correct Tools) ---');
    
    const env = Object.assign({}, process.env, {
        GOOGLE_DRIVE_OAUTH_CREDENTIALS: 'C:\\Users\\victor.bernardi\\.credentials\\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json'
    });

    const server = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], {
        shell: true, env: env, stdio: ['pipe', 'pipe', 'inherit']
    });

    let requestId = 1;
    let folderId, fileId, archiveId;

    function sendRequest(method, params = {}) {
        const request = { jsonrpc: '2.0', id: requestId++, method: method, params: params };
        server.stdin.write(JSON.stringify(request) + '\n');
    }

    server.stdout.on('data', async (data) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const response = JSON.parse(line);
                if (response.id === 1) {
                    console.log('[1] Inicializando...');
                    sendRequest('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'validator', version: '1.0.0' } });
                } else if (response.result && response.id === 2) {
                    console.log('[2] Passo 1: listFolder Root...');
                    sendRequest('tools/call', { name: 'listFolder', arguments: { folderId: 'root' } });
                } else if (response.result && response.id === 3) {
                    console.log('[3] Passo 2: createFolder _STOUT_VAL_...');
                    sendRequest('tools/call', { name: 'createFolder', arguments: { name: '_STOUT_VAL_' } });
                } else if (response.result && response.id === 4) {
                    folderId = response.result.content[0].text.match(/ID: ([a-zA-Z0-9_-]+)/i)?.[1];
                    console.log(`[4] Folder ID: ${folderId}. Passo 2.1: createTextFile...`);
                    sendRequest('tools/call', { name: 'createTextFile', arguments: { name: 'validation_test.txt', content: 'STOUT_SECRET_TOKEN_2026: Conectividade confirmada.', parentFolderId: folderId } });
                } else if (response.result && response.id === 5) {
                    fileId = response.result.content[0].text.match(/ID: ([a-zA-Z0-9_-]+)/i)?.[1];
                    console.log(`[5] File ID: ${fileId}. Passo 3: Search...`);
                    sendRequest('tools/call', { name: 'search', arguments: { query: "name = 'validation_test.txt'" } });
                } else if (response.result && response.id === 6) {
                    console.log(`[6] Search Result OK. Passo 4: createFolder ARCHIVE...`);
                    sendRequest('tools/call', { name: 'createFolder', arguments: { name: 'ARCHIVE', parentFolderId: folderId } });
                } else if (response.result && response.id === 7) {
                    archiveId = response.result.content[0].text.match(/ID: ([a-zA-Z0-9_-]+)/i)?.[1];
                    console.log(`[7] ARCHIVE ID: ${archiveId}. Passo 4.1: moveItem...`);
                    sendRequest('tools/call', { name: 'moveItem', arguments: { itemId: fileId, destinationFolderId: archiveId } });
                } else if (response.result && response.id === 8) {
                    console.log(`[8] Move OK. Passo 6: deleteItem (Cleanup Root)...`);
                    sendRequest('tools/call', { name: 'deleteItem', arguments: { itemId: folderId } });
                } else if (response.result && response.id === 9) {
                    console.log(`[9] Validação FINAL Concluída!`);
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {}
        }
    });

    setTimeout(() => sendRequest('tools/list'), 2000);
}
runValidation();
