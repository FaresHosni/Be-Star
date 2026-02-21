const fs = require('fs');
const pdf = require('pdf-parse');

let dataBuffer = fs.readFileSync('Be Star Event – Official Smart Event Platform.pdf');

pdf(dataBuffer).then(function (data) {
    console.log(data.text);
}).catch(err => console.error(err));
