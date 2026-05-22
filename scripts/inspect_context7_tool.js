const { spawn } = require('child_process');

async function checkTools() {
    console.log('--- Inspecionando Ferramentas do Context7 ---');
    
    const server = spawn('npx', ['-y', '@upstash/context7-mcp@latest'], {
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
                if (response.result && response.id === 1) {
                    sendRequest('tools/list', {});
                }
                if (response.id === 2) {
                    const tool = response.result.tools.find(t => t.name === 'resolve-library-id');
                    console.log('Ferramenta resolve-library-id:', JSON.stringify(tool, null, 2));
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {}
        }
    });

    // Fallback if no log detected
    setTimeout(() => {
         sendRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {},
                clientInfo: { name: 'antigravity-test', version: '1.0.0' }
            });
    }, 3000);

    setTimeout(() => {
        console.log('Timeout final.');
        server.kill();
        process.exit(0);
    }, 20000);
}

checkTools();
