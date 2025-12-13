import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import {defineConfig} from 'rollup';
import {builtinModules} from 'node:module';

// Base configuration for both browser and Node.js
const baseConfig = {
    input: 'src/index.ts',
    external: [
        // Mark external dependencies that shouldn't be bundled
        'axios',
    ],
};

// Browser-specific configuration
const browserConfig = {
    ...baseConfig,
    input: 'src/index.browser.ts',
    external: [
        ...baseConfig.external,
        // Cloud storage SDKs are Node.js only
        '@aws-sdk/client-s3',
        '@google-cloud/storage',
    ],
    output: [
        {
            file: 'dist/index.browser.js',
            format: 'esm',
            sourcemap: true,
        },
        {
            file: 'dist/index.browser.cjs',
            format: 'cjs',
            sourcemap: true,
        },
    ],
    plugins: [
        resolve({browser: true}),
        commonjs(),
        json(),
        typescript({
            tsconfig: './tsconfig.build.json',
            sourceMap: true,
            inlineSources: true,
        }),
    ],
};

// Node.js-specific configuration
const nodeConfig = {
    ...baseConfig,
    external: [
        ...baseConfig.external,
        // These are bundled for browser but external for Node
        '@aws-sdk/client-s3',
        '@google-cloud/storage',
    ],
    output: [
        {
            file: 'dist/index.node.js',
            format: 'esm',
            sourcemap: true,
        },
        {
            file: 'dist/index.node.cjs',
            format: 'cjs',
            sourcemap: true,
        },
    ],
    plugins: [
        resolve({browser: false}),
        commonjs(),
        json(),
        typescript({
            tsconfig: './tsconfig.build.json',
            sourceMap: true,
            inlineSources: true,
        }),
    ],
};

// Default configuration (for backward compatibility)
const defaultConfig = {
    ...baseConfig,
    external: [
        ...baseConfig.external,
        '@aws-sdk/client-s3',
        '@google-cloud/storage',
    ],
    output: [
        {
            file: 'dist/index.js',
            format: 'esm',
            sourcemap: true,
        },
        {
            file: 'dist/index.cjs',
            format: 'cjs',
            sourcemap: true,
        },
    ],
    plugins: [
        resolve(),
        commonjs(),
        json(),
        typescript({
            tsconfig: './tsconfig.build.json',
            sourceMap: true,
            inlineSources: true,
        }),
    ],
};

export default [browserConfig, nodeConfig, defaultConfig];
