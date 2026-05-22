const { spawn } = require('child_process');

async function triggerAuth() {
    console.log('--- Iniciando Trigger de Autenticao NotebookLM ---');
    
    // Inicia o servidor MCP
    const server = spawn('npx', ['-y', 'notebooklm-mcp@latest'], {
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

    const handleData = (data) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const response = JSON.parse(line);
                console.log('[Servidor JSON]:', JSON.stringify(response, null, 2));
                
                if (response.result && response.id === 1) {
                    console.log('Servidor inicializado. Chamando get_health...');
                    sendRequest('tools/call', {
                        name: 'get_health',
                        arguments: {}
                    });
                }
                
                if (response.id === 2) {
                    console.log('Health check concluído.');
                }
            } catch (e) {
                // Logs formatados
                if (line.includes('Ready to receive requests')) {
                    console.log('Detectado log de prontido. Enviando initialize...');
                    sendRequest('initialize', {
                        protocolVersion: '2024-11-05',
                        capabilities: {},
                        clientInfo: { name: 'antigravity-setup', version: '1.0.0' }
                    });
                }
            }
        }
    };

    server.stdout.on('data', handleData);
    server.stderr.on('data', handleData);

    // Mantm o processo vivo por 5 minutos para o login
    setTimeout(() => {
        console.log('Tempo limite de 5 minutos atingido. Encerrando...');
        server.kill();
        process.exit(0);
    }, 300000);
}

triggerAuth();
