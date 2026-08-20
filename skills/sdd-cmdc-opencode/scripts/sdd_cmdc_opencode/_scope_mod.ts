import {spawnSync} from 'node:child_process';
import {isAbsolute} from 'node:path';
import type {ModApi} from '@commandcode/harness';

type Decision = {
  decision: 'allow' | 'block' | 'terminate';
  code: string;
  paths: string[];
  message: string;
};

const requiredPath = (name: string): string => {
  const value = process.env[name] ?? '';
  if (!value || !isAbsolute(value)) {
    throw new Error(`${name} must be an absolute path`);
  }
  return value;
};

const python = requiredPath('SDD_CMDC_SCOPE_PYTHON');
const helper = requiredPath('SDD_CMDC_SCOPE_HELPER');
const contract = requiredPath('SDD_CMDC_SCOPE_CONTRACT');
const runOwner = requiredPath('SDD_CMDC_SCOPE_RUN_OWNER');

const failedDecision = (message: string): Decision => ({
  decision: 'terminate',
  code: 'SCOPE_GUARD_FAILED',
  paths: [],
  message,
});

function decide(operation: string, payload: object): Decision {
  const env: NodeJS.ProcessEnv = {
    ...process.env,
    SDD_CMDC_SCOPE_PYTHON: python,
    SDD_CMDC_SCOPE_HELPER: helper,
    SDD_CMDC_SCOPE_CONTRACT: contract,
    SDD_CMDC_SCOPE_RUN_OWNER: runOwner,
  };
  const scopeNames = new Set([
    'SDD_CMDC_SCOPE_PYTHON',
    'SDD_CMDC_SCOPE_HELPER',
    'SDD_CMDC_SCOPE_CONTRACT',
    'SDD_CMDC_SCOPE_RUN_OWNER',
  ]);
  const unexpected = Object.keys(env).filter(
    (name) => name.startsWith('SDD_CMDC_SCOPE_') && !scopeNames.has(name),
  );
  if (unexpected.length) {
    return failedDecision(`unexpected scope environment variables: ${unexpected.join(', ')}`);
  }
  const result = spawnSync(
    python,
    [helper, operation, '--contract', contract],
    {input: JSON.stringify(payload), encoding: 'utf8', shell: false, env},
  );
  if (result.error || result.status !== 0) {
    return failedDecision(
      result.error?.message ?? String(result.stderr || 'scope helper failed closed'),
    );
  }
  try {
    const decision = JSON.parse(String(result.stdout || '')) as Partial<Decision>;
    if (
      (decision.decision !== 'allow' &&
        decision.decision !== 'block' &&
        decision.decision !== 'terminate') ||
      typeof decision.code !== 'string' ||
      !Array.isArray(decision.paths) ||
      typeof decision.message !== 'string'
    ) {
      return failedDecision('scope helper returned an invalid decision');
    }
    return decision as Decision;
  } catch (error) {
    return failedDecision(`scope helper returned invalid JSON: ${String(error)}`);
  }
}

export default function (cmd: ModApi) {
  cmd.hooks({
    beforeToolCall: async ({toolName, input}) => {
      if (toolName !== 'write_file' && toolName !== 'edit_file') return undefined;
      const result = decide('check-tool', {toolName, input});
      if (result.decision === 'allow') return undefined;
      return {
        block: true,
        terminate: true,
        additionalContext: `${result.code}: ${result.message}${
          result.paths.length ? ` [${result.paths.join(', ')}]` : ''
        }`,
      };
    },
    afterToolCall: async ({toolName, input, result, isError}) => {
      if (toolName !== 'shell_command') return undefined;
      const audit = decide('audit-workspace', {toolName, input, result, isError});
      if (audit.decision === 'allow') return undefined;
      return {
        terminate: true,
        isError: true,
        additionalContext: `${audit.code}: ${audit.message}${
          audit.paths.length ? ` [${audit.paths.join(', ')}]` : ''
        }`,
      };
    },
  });
}
