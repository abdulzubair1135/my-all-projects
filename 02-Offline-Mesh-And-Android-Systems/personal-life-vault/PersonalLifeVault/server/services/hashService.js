const fs = require('fs');
const crypto = require('crypto');

/**
 * Computes SHA-256 hash of a file on disk via streaming to prevent high memory usage.
 * @param {string} filePath 
 * @returns {Promise<string>} Hex SHA-256 string
 */
function computeFileHash(filePath) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash('sha256');
    const stream = fs.createReadStream(filePath);

    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('end', () => resolve(hash.digest('hex')));
    stream.on('error', (err) => reject(err));
  });
}

module.exports = {
  computeFileHash
};
