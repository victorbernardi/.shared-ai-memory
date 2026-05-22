const { spawn } = require('child_process');
const path = require('path');

// Configurao de Ambiente
const credentialsPath = "C:\\Users\\victor.bernardi\\.credentials\\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json";
delete process.env.GOOGLE_APPLICATION_CREDENTIALS; // Remover interferncia da Service Account
process.env.GOOGLE_DRIVE_OAUTH_CREDENTIALS = credentialsPath;

console.log("--- INICIANDO VALIDAO STOUT - MCP GOOGLE DRIVE ---");
console.log(`Credenciais: ${credentialsPath}`);

const mcp = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], {
    env: process.env,
    shell: true
});

let requestId = 1;
const pendingRequests = new Map();

mcp.stdout.on('data', (data) => {
    const lines = data.toString().split('\n');
    for (const line of lines) {
        if (!line.trim()) continue;
        try {
            const response = JSON.parse(line);
            if (response.id && pendingRequests.has(response.id)) {
                const { resolve, method } = pendingRequests.get(response.id);
                pendingRequests.delete(response.id);
                resolve(response);
            }
        } catch (e) {
            // No  JSON, log de debug do servidor
            if (!line.includes("Content-Length")) {
                console.log(`[MCP Debug]: ${line.trim()}`);
            }
        }
    }
});

mcp.stderr.on('data', (data) => {
    console.error(`[MCP Error]: ${data}`);
});

function sendRequest(method, params = {}) {
    return new Promise((resolve) => {
        const id = requestId++;
        const request = { jsonrpc: "2.0", method, params, id };
        pendingRequests.set(id, { resolve, method });
        mcp.stdin.write(JSON.stringify(request) + '\n');
    });
}

async function callTool(name, args) {
    console.log(`\n> Executando Tool: ${name}...`);
    const response = await sendRequest("tools/call", { name, arguments: args });
    if (response.result && response.result.isError) {
        console.error(`  !! ERRO: ${JSON.stringify(response.result.content)}`);
        return null;
    }
    console.log(`  OK: Operao realizada.`);
    return response.result;
}

async function runValidation() {
    try {
        // 1. Criar Arquivo de Teste
        const fileName = `stout_test_${Date.now()}.txt`;
        console.log(`1. Criando arquivo de teste: ${fileName}`);
        const fileRes = await callTool("createTextFile", {
            name: fileName,
            content: "TOKEN_VALIDACAO_INFRA_2026: Sucesso total na integrao."
        });

        if (!fileRes) throw new Error("Falha ao criar arquivo");
        const fileId = fileRes.content[0].text.match(/id: ([a-zA-Z0-9_-]+)/)?.[1] || "";
        console.log(`   ID do Arquivo: ${fileId}`);

        // 2. Busca por Contedo
        console.log("2. Testando Busca por Contedo...");
        const searchRes = await callTool("search", {
            query: "TOKEN_VALIDACAO_INFRA_2026"
        });
        console.log(`   Resultado da Busca: ${JSON.stringify(searchRes.content[0].text)}`);

        // 3. Deleo (Higiene)
        console.log("3. Testando Higiene (DeleteItem)...");
        await callTool("deleteItem", {
            fileId: fileId
        });
        
        console.log("\n--- VALIDAO CONCLUDA COM SUCESSO ---");
    } catch (error) {
        console.error("\n--- FALHA NA VALIDAO ---");
        console.error(error);
    } finally {
        mcp.kill();
        process.exit();
    }
}

// Aguardar o servidor iniciar
setTimeout(runValidation, 5000);
