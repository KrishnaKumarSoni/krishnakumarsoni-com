/**
 * CSS Validation Script
 * This script checks that all CSS classes from style.css are present
 * in the new modular CSS structure.
 * 
 * Run with Node.js:
 * node css-validation.js
 */

const fs = require('fs');
const path = require('path');

// Directory and file paths
const cssDir = path.join(__dirname, '../../static/css');
const originalCssPath = path.join(cssDir, 'style.css');

// Function to extract class names from CSS
function extractClassNames(cssContent) {
  const classPattern = /\.([\w-]+)(?=[^{}]*\{)/g;
  let match;
  const classes = new Set();
  
  while ((match = classPattern.exec(cssContent)) !== null) {
    // Skip pseudo-classes like :hover, :active, etc.
    if (!match[1].includes(':')) {
      classes.add(match[1]);
    }
  }
  
  return classes;
}

// Read original CSS file
function validateCSS() {
  try {
    const originalCss = fs.readFileSync(originalCssPath, 'utf8');
    const originalClasses = extractClassNames(originalCss);
    
    console.log(`Original CSS has ${originalClasses.size} unique classes.`);
    
    // Read all modular CSS files except main.css (which just imports others)
    const moduleClasses = new Set();
    const cssFiles = fs.readdirSync(cssDir)
      .filter(file => file.endsWith('.css') && file !== 'style.css' && file !== 'main.css');
    
    cssFiles.forEach(file => {
      const filePath = path.join(cssDir, file);
      const content = fs.readFileSync(filePath, 'utf8');
      const classes = extractClassNames(content);
      
      console.log(`${file}: ${classes.size} classes`);
      
      // Add these classes to our set of all modular classes
      classes.forEach(className => moduleClasses.add(className));
    });
    
    console.log(`\nModular CSS has ${moduleClasses.size} unique classes.`);
    
    // Find missing classes
    const missingClasses = [];
    originalClasses.forEach(className => {
      if (!moduleClasses.has(className)) {
        missingClasses.push(className);
      }
    });
    
    if (missingClasses.length > 0) {
      console.log('\nWARNING: The following classes are missing from the modular CSS:');
      missingClasses.forEach(className => console.log(`- ${className}`));
    } else {
      console.log('\nSUCCESS: All classes from the original CSS are present in the modular CSS!');
    }
    
  } catch (err) {
    console.error('Error during validation:', err);
  }
}

// Run the validation
validateCSS(); 