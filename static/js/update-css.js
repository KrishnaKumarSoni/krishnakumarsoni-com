/**
 * Script to update HTML files to use the new modular CSS structure.
 * This will replace references to style.css with main.css.
 * 
 * Run with Node.js:
 * node update-css.js
 */

const fs = require('fs');
const path = require('path');

// Directory paths
const templatesDir = path.join(__dirname, '../../templates');

// Function to replace CSS references in HTML files
function updateHtmlFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Replace style.css with main.css
    const updatedContent = content.replace(
      /<link rel="stylesheet" href=".*?\/css\/style\.css">/g,
      '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/main.css\') }}">'
    );
    
    if (content !== updatedContent) {
      fs.writeFileSync(filePath, updatedContent, 'utf8');
      console.log(`Updated: ${filePath}`);
    } else {
      console.log(`No changes needed: ${filePath}`);
    }
  } catch (err) {
    console.error(`Error processing ${filePath}:`, err);
  }
}

// Function to walk through directory and process HTML files
function processDirectory(directory) {
  const files = fs.readdirSync(directory);
  
  files.forEach(file => {
    const filePath = path.join(directory, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      processDirectory(filePath);
    } else if (file.endsWith('.html')) {
      updateHtmlFile(filePath);
    }
  });
}

// Start processing
console.log('Updating HTML files to use modular CSS...');
processDirectory(templatesDir);
console.log('Done!'); 