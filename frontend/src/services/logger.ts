/* eslint-disable no-console */
/**
 * Logging service for Carolina's Diary
 * Provides structured logging with different levels and integrates with monitoring services
 */

export enum LogLevel {
    DEBUG = 'debug',
    INFO = 'info',
    WARN = 'warn',
    ERROR = 'error'
}

interface LogEntry {
    level: LogLevel;
    message: string;
    timestamp: string;
    context?: Record<string, any>;
    userId?: string;
}

class Logger {
    private isDevelopment: boolean;
    private userId?: string;

    constructor() {
        this.isDevelopment = process.env.NODE_ENV === 'development';
    }

    setUserId(userId: string) {
        this.userId = userId;
    }

    private createLogEntry(level: LogLevel, message: string, context?: Record<string, any>): LogEntry {
        const logEntry: LogEntry = {
            level,
            message,
            timestamp: new Date().toISOString()
        };

        if (context) logEntry.context = context;
        if (this.userId) logEntry.userId = this.userId;

        return logEntry;
    }

    private log(level: LogLevel, message: string, context?: Record<string, any>) {
        const logEntry = this.createLogEntry(level, message, context);

        // In development, use console methods
        if (this.isDevelopment) {
            const consoleMessage = `[${logEntry.timestamp}] ${level.toUpperCase()}: ${message}`;

            switch (level) {
                case LogLevel.DEBUG:
                    console.debug(consoleMessage, context || '');
                    break;
                case LogLevel.INFO:
                    console.info(consoleMessage, context || '');
                    break;
                case LogLevel.WARN:
                    console.warn(consoleMessage, context || '');
                    break;
                case LogLevel.ERROR:
                    console.error(consoleMessage, context || '');
                    break;
            }
        }

        // In production, send to monitoring service (Sentry, etc.)
        if (!this.isDevelopment) {
            // TODO: Integrate with Sentry or other monitoring service
            // Example: Sentry.addBreadcrumb({ message, level, data: context });
            if (level === LogLevel.ERROR || level === LogLevel.WARN) {
                // For now, still log warnings and errors to console in production
                console[level](message, context || '');
            }
        }
    }

    debug(message: string, context?: Record<string, any>) {
        this.log(LogLevel.DEBUG, message, context);
    }

    info(message: string, context?: Record<string, any>) {
        this.log(LogLevel.INFO, message, context);
    }

    warn(message: string, context?: Record<string, any>) {
        this.log(LogLevel.WARN, message, context);
    }

    error(message: string, context?: Record<string, any>) {
        this.log(LogLevel.ERROR, message, context);
    }
}

export const logger = new Logger(); 