// Local smoke probe for the Command Code beforeToolCall hook.
//
// Follows the installed Command Code Mod API
// (dist/bundled/mod-builder/reference/hooks-and-events.md and api.md):
// a loadable mod is a factory receiving `cmd: ModApi`; `beforeToolCall`
// returns `{block?, input?, additionalContext?, terminate?}`. When `block`
// is true the core emits the protocolar `tool_hook_blocked` event whose
// `hookOutput` is exactly the returned `additionalContext`, and that same
// text becomes the tool_result the model sees. The adapter verifies the
// hook by requiring that exact event type and `hookOutput` value in the
// NDJSON event stream — never marker text the child could print itself.
import type {ModApi} from '@commandcode/harness';

const MARKER_COMMAND = 'echo SDD_CMDC_MOD_HOOK_OK';
const HOOK_OUTPUT = 'SDD_CMDC_MOD_HOOK_HANDSHAKE';

export default function (cmd: ModApi) {
  cmd.hooks({
    beforeToolCall: async ({toolName, input}) => {
      if (toolName !== 'shell_command') return undefined;
      if (input?.command !== MARKER_COMMAND) return undefined;
      return {
        block: true,
        additionalContext: HOOK_OUTPUT,
      };
    },
  });
}
