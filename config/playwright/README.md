# Playwright Configuration

This directory contains Claude Code configuration files specific to browser testing with Playwright.

## Files

- `.claude.json`: MCP server configuration for Playwright with headless mode enabled
  - Used to bypass Cold Turkey Blocker interference during automated browser testing
  - Can be used with `claude --config config/playwright/.claude.json` when doing browser testing

## Usage

When you need to test browser functionality (landing page, forms, responsiveness), use:

```bash
claude --config config/playwright/.claude.json
```

This will enable the Playwright MCP server in headless mode for automated browser testing.
