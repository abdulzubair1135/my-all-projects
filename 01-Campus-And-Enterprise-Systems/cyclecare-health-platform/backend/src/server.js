const app = require('./app');
require('dotenv').config();

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`  CYCLECARE REST API SERVER RUNNING ON PORT ${PORT}  `);
  console.log(`  Environment: ${process.env.NODE_ENV || 'development'} `);
  console.log(`====================================================`);
});
