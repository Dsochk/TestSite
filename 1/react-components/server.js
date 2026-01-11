process.env.NODE_ENV = process.env.NODE_ENV || 'production';

const express = require('express');
const fs = require('fs');
const path = require('path');
const { renderToPipeableStream } = require('react-server-dom-webpack/server');
const { decodeAction, decodeReply } = require('react-server-dom-webpack/server.node');
const React = require('react');

const app = express();
const PORT = 3000;

function loadLabConfig() {
    const configPath = path.join(__dirname, '..', 'config', 'lab.env');
    const config = {};
    if (!fs.existsSync(configPath)) {
        return config;
    }
    try {
        const lines = fs.readFileSync(configPath, 'utf8').split(/\r?\n/);
        for (const line of lines) {
            if (!line || line.trim().startsWith('#')) {
                continue;
            }
            const [key, ...rest] = line.split('=');
            if (!key || rest.length === 0) {
                continue;
            }
            config[key.trim()] = rest.join('=').trim();
        }
    } catch (error) {
        return config;
    }
    return config;
}

const LAB_CONFIG = loadLabConfig();
const RSC_TOKEN = process.env.RSC_TOKEN || LAB_CONFIG.RSC_TOKEN || 'lms-integration-token';

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const WEBPACK_MODULES = {
    'actions-chunk': {
        submitForm: async function (formData) {
            return { ok: true, received: formData };
        },
        updateUser: async function (userId, userData) {
            return { ok: true, userId, userData };
        },
        constructor: Function,
    },
};

global.__webpack_require__ = function (moduleId) {
    if (Object.prototype.hasOwnProperty.call(WEBPACK_MODULES, moduleId)) {
        return WEBPACK_MODULES[moduleId];
    }
    throw new Error(`Module not found: ${moduleId}`);
};

global.__webpack_chunk_load__ = function () {
    return Promise.resolve();
};

const SERVER_MANIFEST = {
    'file:///app/actions.js#submitForm': {
        id: 'actions-chunk',
        chunks: [],
        name: 'submitForm',
    },
    'file:///app/actions/user.js#updateUser': {
        id: 'actions-chunk',
        chunks: [],
        name: 'updateUser',
    },
    'file:///app/actions/user.js#constructor': {
        id: 'actions-chunk',
        chunks: [],
        name: 'constructor',
    },
};

const DEFAULT_ELEMENT = React.createElement('div', null, 'RSC Response');

function resolveElementFromPayload(payload) {
    if (!payload || typeof payload !== 'object') {
        return DEFAULT_ELEMENT;
    }

    const componentSource = payload.component || payload.fragment || payload.node;
    if (typeof componentSource !== 'string') {
        return DEFAULT_ELEMENT;
    }

    const evaluated = eval(componentSource);

    if (React.isValidElement(evaluated)) {
        return evaluated;
    }

    if (typeof evaluated === 'function') {
        return React.createElement(evaluated, payload.props || payload.data || {});
    }

    if (typeof evaluated === 'object' && evaluated !== null) {
        return React.createElement(evaluated, payload.props || payload.data || {});
    }

    return DEFAULT_ELEMENT;
}

function readRawBody(req) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        req.on('data', (chunk) => chunks.push(chunk));
        req.on('end', () => resolve(Buffer.concat(chunks)));
        req.on('error', reject);
    });
}

function createFormData(entries) {
    const map = new Map(entries);
    map.append = function (key, value) {
        map.set(key, value);
    };
    map.getAll = function (key) {
        if (!map.has(key)) {
            return [];
        }
        return [map.get(key)];
    };
    map.forEach = function (callback) {
        for (const [key, value] of map.entries()) {
            callback(value, key);
        }
    };
    return map;
}

function parseMultipartFormData(body, contentType) {
    const boundaryMatch = contentType.match(/boundary=(?:"([^"]+)"|([^;]+))/i);
    if (!boundaryMatch) {
        throw new Error('No boundary in multipart form data');
    }
    const boundary = boundaryMatch[1] || boundaryMatch[2];
    const bodyStr = body.toString('binary');
    const parts = bodyStr.split('--' + boundary);
    const entries = [];

    for (const part of parts) {
        if (!part || part.trim() === '' || part.trim() === '--') {
            continue;
        }
        const headerEnd = part.indexOf('\r\n\r\n');
        if (headerEnd === -1) {
            continue;
        }
        const headers = part.substring(0, headerEnd);
        const content = part.substring(headerEnd + 4).replace(/\r\n$/, '');
        const nameMatch = headers.match(/name="([^"]+)"/);
        if (nameMatch) {
            entries.push([nameMatch[1], content]);
        }
    }

    return createFormData(entries);
}

function parseUrlEncoded(body) {
    const params = new URLSearchParams(body);
    return createFormData(Array.from(params.entries()));
}

async function parseFormDataFromRequest(req) {
    const contentType = (req.headers['content-type'] || '').toLowerCase();

    if (contentType.includes('multipart/form-data')) {
        const body = await readRawBody(req);
        return parseMultipartFormData(body, contentType);
    }

    if (contentType.includes('application/x-www-form-urlencoded')) {
        if (req.body && typeof req.body === 'object') {
            return createFormData(Object.entries(req.body));
        }
        const body = await readRawBody(req);
        return parseUrlEncoded(body.toString());
    }

    if (contentType.includes('application/json')) {
        if (req.body && typeof req.body === 'object') {
            return createFormData(Object.entries(req.body));
        }
        const body = await readRawBody(req);
        try {
            const parsed = JSON.parse(body.toString());
            return createFormData(Object.entries(parsed));
        } catch (error) {
            return createFormData([]);
        }
    }

    if (req.body && typeof req.body === 'object') {
        return createFormData(Object.entries(req.body));
    }

    const body = await readRawBody(req);
    return parseUrlEncoded(body.toString());
}

async function executeDecodedResult(decoded) {
    if (typeof decoded !== 'function') {
        return { executed: false, result: decoded };
    }

    try {
        const maybeFn = await decoded();
        if (typeof maybeFn === 'function') {
            const output = await maybeFn();
            return { executed: true, result: output };
        }
        return { executed: true, result: maybeFn };
    } catch (error) {
        return { executed: true, error: error.message };
    }
}

async function handleActionRequest(req, res) {
    try {
        const formData = await parseFormDataFromRequest(req);
        const keys = Array.from(formData.keys());
        const hasActionRef = keys.some((key) => key.startsWith('$ACTION_'));

        let decoded = null;
        let mode = 'decodeReply';

        if (hasActionRef) {
            decoded = await decodeAction(formData, SERVER_MANIFEST);
            mode = 'decodeAction';
        }

        if (decoded === null) {
            decoded = await decodeReply(formData, SERVER_MANIFEST);
            mode = 'decodeReply';
        }

        const execution = await executeDecodedResult(decoded);
        res.json({
            ok: true,
            mode,
            executed: execution.executed,
            result: execution.result,
            error: execution.error,
        });
    } catch (error) {
        console.error('Action error:', error);
        res.status(500).json({ ok: false, error: error.message });
    }
}

app.use(express.static(__dirname + '/public'));

function isAuthorized(req) {
    const token = req.get('X-LMS-Token')
        || req.query.token
        || (req.body && req.body.token);
    return token === RSC_TOKEN;
}

app.get('/api/rsc/handshake', (req, res) => {
    res.json({
        status: 'ok',
        difficulty: 'hard',
        schema: 'rsc/v1',
    });
});

app.post('/api/rsc', (req, res) => {
    try {
        if (!isAuthorized(req)) {
            res.status(403).json({ error: 'Invalid integration token' });
            return;
        }

        const payload = req.body;
        const element = resolveElementFromPayload(payload);
        console.warn('⚠️ VULNERABLE: Processing untrusted RSC payload');
        
        res.setHeader('Content-Type', 'text/x-component');
        res.setHeader('X-React-Server-Component', '1');
        
        const stream = renderToPipeableStream(element, {
            onError: (error) => {
                console.error('RSC Error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        stream.pipe(res);
        
    } catch (error) {
        console.error('Error processing RSC request:', error);
        res.status(500).json({ 
            error: 'Failed to process RSC request',
            message: error.message 
        });
    }
});

app.post('/', handleActionRequest);
app.post('/api/action', handleActionRequest);
app.post('/formaction', handleActionRequest);

app.get('/api/rsc/demo', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>React RSC Vulnerability Demo</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .warning { background: #ffeb3b; padding: 15px; border-radius: 5px; margin: 20px 0; }
                code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
                pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>React Server Components Vulnerability Demo</h1>
            <div class="warning">
                <h2>⚠️ Vulnerability: PT-2025-48817 (CVE-2025-55182)</h2>
                <p>React Server Components версий 19.0.0-19.2.1 уязвимы к RCE через небезопасную десериализацию.</p>
            </div>
            
            <h2>Exploitation</h2>
            <p>Для эксплуатации требуется специальный payload, который использует уязвимость в react-server-dom-webpack/server.</p>
            <p>Публичные PoC доступны на GitHub:</p>
            <ul>
                <li><a href="https://github.com/ejpir/CVE-2025-55182-research">ejpir/CVE-2025-55182-research</a></li>
            </ul>
            
            <h3>Example Request:</h3>
            <pre>POST /api/rsc HTTP/1.1
Content-Type: application/json

{
  "component": "...malicious payload..."
}</pre>

            <p><strong>Server Action PoC:</strong> POST / (multipart/form-data) with Next-Action header (port 3000).</p>
            
            <p><strong>Note:</strong> This is a simplified demonstration. Real exploitation requires understanding the internal serialization format of React Server Components.</p>
        </body>
        </html>
    `);
});

app.get('/', (req, res) => {
    res.redirect('/api/rsc/demo');
});

app.listen(PORT, () => {
    console.log(`React RSC Server running on http://localhost:${PORT}`);
    console.log(`⚠️  VULNERABLE: PT-2025-48817 (CVE-2025-55182) - React 19.0.0`);
    console.log(`Demo endpoint: http://localhost:${PORT}/api/rsc/demo`);
});
