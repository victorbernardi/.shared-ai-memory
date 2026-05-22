const { spawn } = require('child_process');

async function testGoogleDrive() {
    console.log('--- Inspecionando @piotr-agier/google-drive-mcp ---');
    
    const server = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], {
        shell: true,
        stdio: ['pipe', 'pipe', 'pipe']
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
                if (response.id === 1) {
                    console.log('Inicializao Completa.');
                    if (response.result && response.result.instructions) {
                        console.log('Instrues do servidor:\n', response.result.instructions);
                    }
                    sendRequest('tools/list', {});
                }
                if (response.id === 2) {
                    console.log('Ferramentas:');
                    response.result.tools.forEach(t => console.log(`- ${t.name}: ${t.description}`));
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {}
        }
    });

    server.stderr.on('data', (data) => {
        console.log('[Log STDERR]:', data.toString().trim());
    });

    setTimeout(() => {
        sendRequest('initialize', {
            protocolVersion: '2024-11-05',
            capabilities: {},
            clientInfo: { name: 'antigravity-test', version: '1.0.0' }
        });
    }, 3000);

    setTimeout(() => {
        console.log('Timeout. Encerrando...');
        server.kill();
        process.exit(0);
    }, 15000);
}

testGoogleDrive();
