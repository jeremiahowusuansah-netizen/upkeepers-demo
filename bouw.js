// Bundelt alle schermbestanden in bundel.js, zodat de app ook zonder server (file://) werkt.
const fs = require('fs'), path = require('path');
const dir = path.join(__dirname, 'bron');
const src = {};
for (const f of fs.readdirSync(dir)) if (f.endsWith('.dc.html')) src[f.replace('.dc.html', '')] = fs.readFileSync(path.join(dir, f), 'utf8');
fs.writeFileSync(path.join(__dirname, 'bundel.js'), 'window.UPK_SRC = ' + JSON.stringify(src) + ';\n');
console.log(Object.keys(src).length + ' schermen gebundeld');
