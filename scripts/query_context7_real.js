const { spawn } = require('child_process');

async function queryContext7() {
    console.log('--- Executando Consulta Real no Context7 ---');
    
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
                
                // 1. Initialize
                if (response.result && response.id === 1) {
                    console.log('Servidor inicializado. Buscando library ID para "google drive"...');
                    sendRequest('tools/call', {
                        name: 'resolve-library-id',
                        arguments: { 
                            query: 'how to use google drive api',
                            libraryName: 'google drive' 
                        }
                    });
                }
                
                // 2. Handle resolve-library-id response
                if (response.id === 2) {
                    console.log('Resultado da busca de biblioteca:', JSON.stringify(response.result, null, 2));
                    // Tenta extrair um ID
                    const content = response.result.content[0].text;
                    const match = content.match(/\/[\w\-\/]+/);
                    const libId = match ? match[0] : null;
                    
                    if (libId) {
                        console.log(`ID encontrado: ${libId}. Consultando documentao de MCP...`);
                        sendRequest('tools/call', {
                            name: 'query-docs',
                            arguments: { 
                                libraryId: libId, 
                                query: 'how to implement an MCP server for Google Drive' 
                            }
                        });
                    } else {
                        console.log('Nenhum ID de biblioteca encontrado para a busca.');
                        server.kill();
                        process.exit(0);
                    }
                }

                // 3. Handle query-docs response
                if (response.id === 3) {
                    console.log('--- RESULTADO DA DOCUMENTAO ---');
                    console.log(response.result.content[0].text);
                    server.kill();
                    process.exit(0);
                }
            } catch (e) {
                // Ignore non-json
            }
        }
    });

    server.stderr.on('data', (data) => {
        if (data.toString().includes('Ready to receive requests')) {
             sendRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {},
                clientInfo: { name: 'antigravity-test', version: '1.0.0' }
            });
        }
    });

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
    }, 60000);
}

queryContext7();
