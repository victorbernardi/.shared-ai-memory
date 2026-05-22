const { spawn } = require('child_process');
const path = require('path');

async function testGoogleDriveAuth() {
    console.log('--- Iniciando Teste de Autenticao do Google Drive MCP ---');
    
    // Pass the credentials file path
    const env = Object.assign({}, process.env, {
        GOOGLE_DRIVE_OAUTH_CREDENTIALS: 'C:\\Users\\victor.bernardi\\.credentials\\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json'
    });
    delete env.GOOGLE_APPLICATION_CREDENTIALS;

    const server = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], {
        shell: true,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: env
    });

    let messageId = 1;

    function sendRequest(method, params) {
        const req = { jsonrpc: '2.0', id: messageId++, method, params };
        server.stdin.write(JSON.stringify(req) + '\n');
    }

    server.stdout.on('data', (data) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const response = JSON.parse(line);
                console.log('[Servidor JSON]:', JSON.stringify(response, null, 2));
                
                if (response.id === 1) {
                    console.log('Inicializao Completa. Chamando tools/list...');
                    sendRequest('tools/list', {});
                }
                
                if (response.id === 2) {
                    console.log('Ferramentas Listadas. Chamando searchFiles...');
                    sendRequest('tools/call', {
                        name: 'searchFiles',
                        arguments: { query: "name contains 'a'" }
                    });
                }

                if (response.id === 3) {
                    console.log('--- RESPOSTA SEARCH FILES ---');
                    console.log(JSON.stringify(response.result, null, 2));
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {
                // Not JSON
            }
        }
    });

    server.stderr.on('data', (data) => {
        const output = data.toString();
        console.log('[Log STDERR]:', output.trim());
        
        // Se houver um link de autenticao no log, ele aparecer aqui
        if (output.includes('Ready to receive requests') || output.includes('Server initialized') || output.includes('started')) {
             // Envia initialize
             // Algumas vezes ele pode precisar do initialize para comear o oauth,
             // ou ele bloqueia a inicializao at ter o oauth
        }
    });

    // Enviar initialize logo aps um pequeno atraso
    setTimeout(() => {
        console.log('Enviando request de initialize...');
        sendRequest('initialize', {
            protocolVersion: '2024-11-05',
            capabilities: {},
            clientInfo: { name: 'antigravity-test', version: '1.0.0' }
        });
    }, 3000);

    // Mantm rodando por 5 minutos para dar tempo de fazer o login no navegador se necessrio
    setTimeout(() => {
        console.log('Timeout. Encerrando...');
        server.kill();
        process.exit(0);
    }, 300000);
}

testGoogleDriveAuth();
