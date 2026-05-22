const { spawn } = require('child_process');

async function testContext7() {
    console.log('--- Iniciando Teste de Context7 (@upstash/context7-mcp) ---');
    
    const server = spawn('npx', ['-y', '@upstash/context7-mcp@latest'], {
        shell: true,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let messageId = 1;

    function sendRequest(method, params) {
        const req = {
            jsonrpc: '2.0',
            id: messageId++,
            method,
            params
        };
        server.stdin.write(JSON.stringify(req) + '\n');
    }

    server.stdout.on('data', (data) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const response = JSON.parse(line);
                console.log('[Servidor JSON]:', JSON.stringify(response, null, 2));
                
                if (response.result && response.id === 1) {
                    console.log('Servidor inicializado. Listando ferramentas...');
                    sendRequest('tools/list', {});
                }
                
                if (response.id === 2) {
                    console.log('Ferramentas disponveis:', JSON.stringify(response.result.tools.map(t => t.name), null, 2));
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {
                // Ignore non-json logs
            }
        }
    });

    server.stderr.on('data', (data) => {
        console.log('[Log]:', data.toString());
        if (data.toString().includes('Ready to receive requests') || data.toString().includes('MCP server running')) {
             sendRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {},
                clientInfo: { name: 'antigravity-test', version: '1.0.0' }
            });
        }
    });

    // Fallback if no log detected
    setTimeout(() => {
         sendRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {},
                clientInfo: { name: 'antigravity-test', version: '1.0.0' }
            });
    }, 5000);

    setTimeout(() => {
        console.log('Timeout.');
        server.kill();
        process.exit(0);
    }, 30000);
}

testContext7();
