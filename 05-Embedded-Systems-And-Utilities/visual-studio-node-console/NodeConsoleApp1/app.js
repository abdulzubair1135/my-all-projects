const express = require('express');
const app = express();
const port = 3000;


app.use((req, res, next) => {
    console.log('Request aaya:', req.method, req.url, 'at', new Date());
    next();
});


app.get('/', (req, res) => {
    res.send('<h1>Express ke saath server chal raha hai!</h1>');
});

app.get('/about', (req, res) => {
    res.send('<h1>Ye mera About page hai!</h1>');
});

app.get('/contact', (req, res) => {
    res.send('<h1>Contact: ex@123gmai.com</h1>');
});

app.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
});