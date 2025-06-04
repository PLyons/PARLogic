import './commands';
import 'cypress-file-upload';
import '@testing-library/cypress/add-commands';

// Prevent uncaught exceptions from failing tests
Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from failing the test
  return false;
}); 