# React Server Components Vulnerability Demo

## PT-2025-48817 (CVE-2025-55182)

This component demonstrates the React Server Components vulnerability affecting React versions 19.0.0 through 19.2.1.

### Installation

```bash
cd react-components
npm install
```

### Running

```bash
npm start
```

Server will start on port 3000.

### Vulnerability Details

The vulnerability exists in `react-server-dom-webpack/server` and allows Remote Code Execution (RCE) through unsafe deserialization of React Server Components payloads. This lab endpoint accepts a JSON body with a `component` string and evaluates it unsafely to simulate the issue.

## PoC Compatibility (ejpir/CVE-2025-55182-research)

The server exposes endpoints compatible with the PoCs from:
https://github.com/ejpir/CVE-2025-55182-research

- `POST /` (multipart/form-data, Next-Action header supported)
- `POST /api/action`
- `POST /formaction`

These endpoints parse multipart form data and call `decodeReply`/`decodeAction`
from `react-server-dom-webpack/server.node`, matching the PoC request format.

## Integration Token

The lab reads `config/lab.env`. The `/api/rsc` endpoint requires an integration token:

```
LAB_DIFFICULTY=hard
RSC_TOKEN=lms-integration-token
```

Send the token in the `X-LMS-Token` header or as a `token` field in the JSON payload.

### References

- https://dbugs.ptsecurity.com/vulnerability/PT-2025-48817
- CVE-2025-55182
- https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
