#!/usr/bin/env node
'use strict';
require('../src/core/cli.cjs').main().then(code=>{process.exitCode=code});
