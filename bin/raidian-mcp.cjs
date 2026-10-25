#!/usr/bin/env node
'use strict';
require('../src/mcp/server.cjs').main().then(code=>{process.exitCode=code});
