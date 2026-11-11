import fs from 'fs';

const file1 = 'c:/backend/wss/wssbhuj.in/assets/DishTVBilling-D3j08EmX.js';
const file2 = 'c:/backend/wss/wssbhuj.in/assets/OTTBilling-D90Rju0v.js';

if (fs.existsSync(file1)) {
  const content = fs.readFileSync(file1, 'utf8');
  let idx = 0;
  while (true) {
    idx = content.indexOf('de(', idx);
    if (idx === -1) break;
    console.log(`\n--- DishTVBilling de( call at index ${idx} ---`);
    console.log(content.substring(idx - 100, idx + 200));
    idx += 3;
  }
}

if (fs.existsSync(file2)) {
  const content = fs.readFileSync(file2, 'utf8');
  let idx = 0;
  while (true) {
    idx = content.indexOf('me(', idx);
    if (idx === -1) break;
    console.log(`\n--- OTTBilling me( call at index ${idx} ---`);
    console.log(content.substring(idx - 100, idx + 200));
    idx += 3;
  }
}
