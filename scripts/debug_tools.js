const { spawn } = require('child_process');
const credentialsPath = "C:\\Users\\victor.bernardi\\.credentials\\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json";
process.env.GOOGLE_DRIVE_OAUTH_CREDENTIALS = credentialsPath;
delete process.env.GOOGLE_APPLICATION_CREDENTIALS;

const mcp = spawn('npx', ['-y', '@piotr-agier/google-drive-mcp@latest'], { env: process.env, shell: true });

mcp.stdout.on('data', (data) => {
    const lines = data.toString().split('\n');
    for (const line of lines) {
        try {
            const response = JSON.parse(line);
            if (response.result && response.result.tools) {
                console.log("TOOLS_LIST_START");
                response.result.tools.forEach(t => console.log(`TOOL: ${t.name}`));
                console.log("TOOLS_LIST_END");
                mcp.kill();
                process.exit();
            }
        } catch (e) {}
    }
});

setTimeout(() => {
    mcp.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "tools/list", params: {}, id: 1 }) + '\n');
}, 5000);
