const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

app.use('/api', createProxyMiddleware({
    target: 'https://map.naver.com',
    changeOrigin: true,
    pathRewrite: {
        '^/api': '/p/api'
    },
    onProxyReq: (proxyReq, req, res) => {
        proxyReq.setHeader('origin', 'https://map.naver.com');
    }
}));

app.listen(3000, () => {
    console.log('Proxy server is running on http://localhost:3000');
});