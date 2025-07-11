# Use official Playwright image with Node.js
FROM mcr.microsoft.com/playwright:v1.54.0-jammy

# Set working directory
WORKDIR /app

# Copy landing page files
COPY . .

# Install dependencies for our test script
RUN npm init -y && npm install playwright

# Create test script
RUN cat > test-landing.js << 'EOF'
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function testLandingPage() {
  console.log('Starting landing page tests...');
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to landing page
    const filePath = 'file://' + path.resolve('./index.html');
    console.log('Navigating to:', filePath);
    await page.goto(filePath);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    console.log('Page loaded successfully!');
    console.log('Title:', await page.title());
    
    // Test 1: Desktop screenshot
    console.log('\n=== Desktop Testing ===');
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.screenshot({ path: '/screenshots/desktop-1920x1080.png', fullPage: true });
    console.log('✓ Desktop screenshot saved');
    
    // Test 2: Tablet screenshot
    console.log('\n=== Tablet Testing ===');
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.screenshot({ path: '/screenshots/tablet-768x1024.png', fullPage: true });
    console.log('✓ Tablet screenshot saved');
    
    // Test 3: Mobile screenshot
    console.log('\n=== Mobile Testing ===');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.screenshot({ path: '/screenshots/mobile-375x667.png', fullPage: true });
    console.log('✓ Mobile screenshot saved');
    
    // Test 4: Form functionality
    console.log('\n=== Form Testing ===');
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Test invalid email
    await page.fill('#email', 'invalid-email');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);
    
    const errorMessage = await page.textContent('#formMessage');
    if (errorMessage && errorMessage.includes('valid email')) {
      console.log('✓ Email validation working');
    } else {
      console.log('✗ Email validation failed');
    }
    
    // Test valid email
    await page.fill('#email', 'test@example.com');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    const successMessage = await page.textContent('#formMessage');
    if (successMessage && successMessage.includes('Success')) {
      console.log('✓ Form submission working');
    } else {
      console.log('✗ Form submission failed');
    }
    
    // Test duplicate prevention
    await page.reload();
    await page.waitForTimeout(1000);
    const formVisible = await page.isVisible('#waitlistForm');
    if (!formVisible) {
      console.log('✓ Duplicate prevention working (form hidden)');
    } else {
      console.log('✗ Duplicate prevention not working');
    }
    
    console.log('\n=== All tests completed! ===');
    
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    await browser.close();
  }
}

testLandingPage();
EOF

# Make screenshots directory
RUN mkdir -p /screenshots

# Set the default command
CMD ["node", "test-landing.js"]